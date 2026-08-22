from django.dispatch import receiver
from django.db.models import Sum
from .models import Certificate, StudentAdmission, Fee
from django.db.models.signals import post_save, post_delete, pre_save
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import threading
from django.core.mail import get_connection
from core.utils.email import send_email_async
from core.utils.pdf import generate_admission_pdf
from email.mime.image import MIMEImage
from core.utils.email_tasks import send_certificate_email_async
import os
import requests
from django.utils import timezone
# -------------------------------
# COURSE COMPLETION LOGIC
# -------------------------------

from .models import CourseEnrollment
from django.db.models.signals import pre_save

@receiver(pre_save, sender=Certificate)
def track_publish_change(sender, instance, **kwargs):
    if not instance.pk:
        instance._was_published = False
        return

    try:
        old = Certificate.objects.get(pk=instance.pk)
        instance._was_published = old.is_published
    except Certificate.DoesNotExist:
        instance._was_published = False

def update_completion(student):

    

    if not student:
        return

    enrollment = CourseEnrollment.objects.filter(
        student=student,
        is_active=True   # 🔥 IMPORTANT (only current course)
    ).first()

    if not enrollment:
        return

    # TOTAL PAID
    total_paid = (
        Fee.objects
        .filter(enrollment=enrollment)
        .exclude(fee_type="ADMISSION")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # CERTIFICATE STATUS
    is_certificate_published = Certificate.objects.filter(
        student=student,
        completed_course=enrollment.course,
        is_published=True
    ).count() > 0

    # FINAL CONDITION
    is_completed = (
        total_paid >= (enrollment.total_fee or 0)
        and is_certificate_published
    )


    # print("DEBUG:")
    # print("Course:", enrollment.course)
    # print("Paid:", total_paid)
    # print("Cert:", is_certificate_published)
    # print("Completed:", is_completed)


    # UPDATE STUDENT (MAIN FLAG)
    if student.course_completed != is_completed:
        student.course_completed = is_completed
        student.save()

    # UPDATE ACTIVE STATUS
    new_active = not is_completed
    if student.is_active != new_active:
        student.is_active = new_active
        student.save()


@receiver(post_delete, sender=Certificate)
def cert_deleted(sender, instance, **kwargs):
    update_completion(instance.student)


# -------------------------------
# CERTIFICATE PUBLISH LOGIC
# -------------------------------
@receiver(post_save, sender=Fee)
@receiver(post_delete, sender=Fee)
def update_certificate_status(sender, instance, created=False, **kwargs):

    enrollment = instance.enrollment

    # ==========================================
    # TOTAL COURSE FEE PAID
    # ==========================================

    total_paid = (
        Fee.objects
        .filter(
            enrollment=enrollment,
            fee_type__in=["MONTHLY", "ADVANCE"]
        )
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    remaining_fee = max(
        (enrollment.total_fee or 0) - total_paid,
        0
    )

    # ==========================================
    # REMAINING FINE
    # ==========================================

    latest_fee = (
        Fee.objects
        .filter(enrollment=enrollment)
        .order_by("-id")
        .first()
    )

    remaining_fine = (
        latest_fee.remaining_fine or 0
        if latest_fee
        else 0
    )

    # ==========================================
    # CERTIFICATES
    # ==========================================

    certificates = Certificate.objects.filter(
        student=enrollment.student,
        completed_course=enrollment.course
    )

    for cert in certificates:

        exams_completed = cert.check_exam_completion()

        print("--------------------------------")
        print("Certificate:", cert.id)
        print("Before:", cert.is_published)
        print("Total Course Fee:", enrollment.total_fee)
        print("Total Paid:", total_paid)
        print("Remaining Fee:", remaining_fee)
        print("Remaining Fine:", remaining_fine)
        print("Exam Result:", exams_completed)

        # ==========================================
        # FINAL PUBLISH CONDITION
        # ==========================================

        new_status = (
            remaining_fee <= 0
            and remaining_fine <= 0
            and exams_completed
        )

        # ==========================================
        # UPDATE ONLY IF STATUS CHANGED
        # ==========================================

        if cert.is_published != new_status:

            cert.is_published = new_status

            if new_status:
                if not cert.published_at:
                    cert.published_at = timezone.now()
            else:
                cert.published_at = None

            cert.save(
                update_fields=[
                    "is_published",
                    "published_at"
                ]
            )

    # ==========================================
    # UPDATE STUDENT COMPLETION
    # ==========================================

    update_completion(enrollment.student)

@receiver(post_save, sender=CourseEnrollment)
def enrollment_created(sender, instance, created, **kwargs):
    if created:
        student = instance.student

        # 🔥 Deactivate old enrollments
        CourseEnrollment.objects.filter(
            student=student
        ).exclude(id=instance.id).update(is_active=False)

        # 🔥 Ensure new one is active
        if not instance.is_active:
            instance.is_active = True
            instance.save(update_fields=["is_active"])

        # 🔥 RESET STUDENT STATUS
        student.course_completed = False
        student.is_active = True

        # ✅ Don't recreate admission fee during upgrade
        student.save(from_upgrade=True)

        # Optional: run completion check
        update_completion(student)


# send mail for receive a payment

def send_fee_email(student, instance):
    

    subject = "Payment Receipt"
    from_email=settings.DEFAULT_FROM_EMAIL
    to = [student.email]

    # ✅ FIX 1: Use correct field
    payment_date = getattr(instance, "payment_date", None)
    formatted_date = payment_date.strftime("%d %b %Y") if payment_date else "N/A"

    # ✅ FIX 2: Use correct fine field
    late_fine = getattr(instance, "fine", 0)

    # ✅ FIX 3: Correct total calculation
    total_paid = (instance.amount or 0) + (late_fine or 0)

    student_id = getattr(student, "student_id", "N/A")

    text_content = f"Your payment of ₹{total_paid} is received."

    # ✅ NEW: Due Date
    due_date = getattr(instance, "due_date", None)
    formatted_due_date = due_date.strftime("%d %b %Y") if due_date else "N/A"

    # ✅ NEW: Payment Method (change field name if needed)
    payment_method = getattr(instance, "pay_via", "N/A")
    payment_method = str(payment_method).title()

    waive_note = ""

    if getattr(instance, "waive_fine", False):
        waive_note = """
        <p style="
            margin-top: 12px;
            font-weight: 600;
            color: #2e7d32;
            font-size: 14px;
        ">
            (Fine Waived)
        </p>
        """

    is_waived = getattr(instance, "waive_fine", False)

    display_fine = 0 if is_waived else late_fine
    display_total = (instance.amount or 0) + display_fine

    html_content = f"""
    <html>
    <body style="font-family: Arial; background-color:#f5f5f5; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:10px;">
            
            <h1 style="color:#2b7de9;">Payment Receipt</h1>

            <p>Hello <b>{student.name}</b>,</p>
            <p>Your payment has been successfully received.</p>

            <hr>

            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Receipt No</td>
                    <td style="border:1px solid #ddd; padding:10px;">RCPT-{instance.receipt_no}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Student ID</td>
                    <td style="border:1px solid #ddd; padding:10px;">{student_id}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Due Date</td>
                    <td style="border:1px solid #ddd; padding:10px;">{formatted_due_date}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Payment Date</td>
                    <td style="border:1px solid #ddd; padding:10px;">{formatted_date}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Amount</td>
                    <td style="border:1px solid #ddd; padding:10px;">₹{instance.amount}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Late Fee</td>
                    <td style="border:1px solid #ddd; padding:10px;">₹{display_fine} {"(Waived)" if is_waived else ""}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;">Payment Method</td>
                    <td style="border:1px solid #ddd; padding:10px;">{payment_method}</td>
                </tr>

                <tr>
                    <td style="border:1px solid #ddd; padding:10px;"><b>Total Paid</b></td>
                    <td style="border:1px solid #ddd; padding:10px;"><b>₹{display_total}</b></td>
                </tr>
            </table>
            {waive_note}

            <p style="margin-top:20px;"><b>~ Smart Computer Institute</b></p>
            

        </div>
    </body>
    </html>
    """
    

    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(
            os.environ["MAILJET_API_KEY"],
            os.environ["MAILJET_SECRET_KEY"]
        ),
        json={
            "Messages": [
                {
                    "From": {
                        "Email": "noreply@smartci.in",
                        "Name": "Smart Computer Institute"
                    },
                    "To": [
                        {
                            "Email": student.email,
                            "Name": student.name
                        }
                    ],
                    "Subject": subject,
                    "TextPart": text_content,
                    "HTMLPart": html_content,
                }
            ]
        },
        timeout=30,
    )

    print("MAILJET STATUS:", response.status_code)
    print("MAILJET RESPONSE:", response.text)

    response.raise_for_status()





def send_fee_email_async(student, instance):
    def send():
        send_fee_email(student, instance)  # your HTML email function

    threading.Thread(target=send).start()
    


from .models import Fee



@receiver(post_save, sender=Fee)
def send_payment_email(sender, instance, created, **kwargs):
    
    if created:
        student = instance.enrollment.student
        
        if student.email:
            send_fee_email_async(student, instance)








@receiver(post_save, sender=StudentAdmission)
def admission_email_signal(sender, instance, created, **kwargs):
    print("Admission signal fired")
    # if created and instance.email:
    if not created or not instance.email:
        return

    # if instance.email:
    pdf_buffer = generate_admission_pdf(instance)

    subject = "🎓 Admission Confirmed - Smart Computer Institute"

    message = f"""
Hello {instance.name},
hii
Your admission has been successfully completed.

Please find your receipt attached.

Regards,
Smart Computer Institute
        """

    html_message = f"""
<html>
<body style="margin:0; padding:0; background:#eef2f7; font-family:'Segoe UI', Arial, sans-serif;">

<div style="max-width:620px; margin:40px auto; background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,0.08);">

    <!-- HEADER -->
    <div style="background:linear-gradient(135deg,#0f172a,#1e40af); padding:22px 25px; color:white;">
        <h2 style="margin:0; font-size:20px;">🎓 Smart Computer Institute</h2>
        <p style="margin:6px 0 0; font-size:13px; opacity:0.85;">
            Official Admission Confirmation
        </p>
    </div>

    <!-- BODY -->
    <div style="padding:28px; color:#333;">

        <p style="font-size:15px; margin:0 0 10px;">
            Hello <b>{instance.name}</b>,
        </p>

        <p style="font-size:14px; color:#555; line-height:1.6;">
            We are pleased to inform you that your admission has been successfully completed.
            Please find your official details below.
        </p>

        <!-- STUDENT ID HIGHLIGHT -->
        <div style="margin:20px 0; padding:14px; background:#0f172a; color:white; border-radius:8px; text-align:center;">
            <span style="font-size:12px; opacity:0.7;">STUDENT ID</span><br>
            <span style="font-size:18px; font-weight:bold; letter-spacing:1px;">
                {instance.student_id}
            </span>
        </div>

        <!-- DETAILS BOX -->
        <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:18px; border-radius:8px;">

            <table style="width:100%; font-size:14px; color:#333;">
                <tr>
                    <td style="padding:6px 0;"><b>Course</b></td>
                    <td style="padding:6px 0;">{instance.course.name}</td>
                </tr>
                <tr>
                    <td style="padding:6px 0;"><b>Admission Date</b></td>
                    <td style="padding:6px 0;">{instance.admission_date}</td>
                </tr>
            </table>

        </div>

        <!-- INFO -->
        <p style="margin:20px 0 5px; font-size:14px; color:#444;">
            📎 Your official admission receipt is attached with this email.
        </p>

        <hr style="border:none; border-top:1px solid #e5e7eb; margin:25px 0;">

        <p style="font-size:14px; margin:0;">
            Regards,<br>
            <b style="color:#0f172a;">Smart Computer Institute</b>
        </p>

    </div>

    <!-- FOOTER -->
    <div style="background:#f1f5f9; padding:14px 20px; font-size:12px; color:#666; text-align:center;">

        <p style="margin:5px 0;">
            📍 Smart Computer Institute
        </p>

        <p style="margin:5px 0; color:#999;">
            This is an automated email. Please do not reply.
        </p>

    </div>

</div>

</body>
</html>
"""
    send_email_async(
        subject=subject,
        message=message,
        recipient_list=[instance.email],
        html_message=html_message,
        files=[("Admission_Receipt.pdf", pdf_buffer.read())]  # 🔥 HERE
    )

from django.db.models.signals import pre_save

from .models import StudentAdmission


@receiver(pre_save, sender=StudentAdmission)
def detect_course_change(sender, instance, **kwargs):

    if not instance.pk:
        return  # New student, skip

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # 🎯 Detect change
    if old.course != instance.course:

        # Save old course name for email
        instance._old_course = old.course.name



@receiver(post_save, sender=StudentAdmission)
def send_upgrade_email(sender, instance, created, **kwargs):

    if created:
        return  # Skip new admission

    if not hasattr(instance, "_old_course"):
        return  # No course change → skip

    if not instance.email:
        return

    # 🧾 Subject
    subject = "Course Upgrade Confirmation - Smart Computer Institute"

    # 📄 Plain text (fallback)
    message = f"""
Hello {instance.name},

Your course has been successfully upgraded.

Previous Course: {instance._old_course}
New Course: {instance.course.name}

Regards,
Smart Computer Institute
"""

    # 🎨 HTML Design (Professional)
    html_message = f"""
<html>
<body style="margin:0; padding:0; background:#eef2f7; font-family:Arial, sans-serif;">

<div style="max-width:600px; margin:30px auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 4px 10px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#1e3a8a; color:white; padding:18px;">
        <h2 style="margin:0;">Smart Computer Institute</h2>
        <p style="margin:5px 0 0; font-size:13px;">Course Upgrade Confirmation</p>
    </div>

    <!-- Body -->
    <div style="padding:25px; color:#333;">

        <p style="font-size:14px;">Hello <b>{instance.name}</b>,</p>

        <p style="font-size:14px; color:#555;">
            Your course has been successfully upgraded. Please find the updated details below:
        </p>

        <!-- Highlight Box -->
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:15px; margin:20px 0;">

            <table style="width:100%; font-size:14px;">
                <tr>
                    <td style="padding:6px;"><b>Previous Course</b></td>
                    <td style="padding:6px;">{instance._old_course}</td>
                </tr>
                <tr>
                    <td style="padding:6px;"><b>New Course</b></td>
                    <td style="padding:6px; color:#1e3a8a; font-weight:bold;">
                        {instance.course.name}
                    </td>
                </tr>
            </table>

        </div>

        <p style="font-size:13px; color:#555;">
            Your updated course is now active in our system.
        </p>

        <p style="margin-top:20px; font-size:14px;">
            Regards,<br>
            <b>Smart Computer Institute</b>
        </p>

    </div>

    <!-- Footer -->
    <div style="background:#f1f5f9; padding:12px; text-align:center; font-size:12px; color:#666;">
        This is an automated notification. Please do not reply to this email.
    </div>

</div>

</body>
</html>
"""

    # 📤 Send email
    send_email_async(
        subject=subject,
        message=message,
        recipient_list=[instance.email],
        html_message=html_message
    )
    if hasattr(instance, "_old_course"):
        del instance._old_course
    
    


from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from student_portal.models import Certificate
from core.utils.email_tasks import send_certificate_email_async


# @receiver(post_save, sender=Certificate)
# def certificate_email_signal(sender, instance, created, **kwargs):

#     if not instance.is_published:
#         return

#     if instance.email_sent:
#         return

#     if not instance.student:
#         return

#     if not instance.student.email:
#         return

#     transaction.on_commit(
#         lambda: send_certificate_email_async(
#             instance.id,
#             instance.student.franchise
#         )
#     )

#     Certificate.objects.filter(
#         pk=instance.pk
#     ).update(
#         email_sent=True
#     )

@receiver(post_save, sender=Certificate)
def certificate_email_signal(sender, instance, created, **kwargs):

    # Only when a NEW certificate is created
    if not created:
        return

    if not instance.is_published:
        return

    if not instance.student:
        return

    if not instance.student.email:
        return

    transaction.on_commit(
        lambda: send_certificate_email_async(
            instance.id,
            instance.student.franchise
        )
    )