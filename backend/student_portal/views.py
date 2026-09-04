import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from student_portal.fee_engine import calculate_student_dues
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
from django.db import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from xhtml2pdf import pisa
from management_portal.models import StudentMarks
from student_portal.models import Fee
from .models import Certificate
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from mailjet_rest import Client
import os
from student_portal.models import (
    BatchDay,
    BatchTiming,
    StudentAdmission,
    Course,
    Certificate
)

# Set up logging for error tracking
logger = logging.getLogger(__name__)

# ================= AUTH & DASHBOARD =================

def custom_logout(request):
    logout(request)
    return redirect('/admin/login/')

# def student_dashboard(request):
#     return render(request, "student_portal/dashboard.html")

# ================= DATA RETRIEVAL APIs =================

def get_student_data(request):
    sid = request.GET.get('student_id')
    try:
        student = StudentAdmission.objects.get(student_id=sid)
        return JsonResponse({
            "name": student.name,
            "gender": student.gender, 
            "admission_pay_via": student.admission_pay_via,
            "dob": student.dob.strftime('%Y-%m-%d') if student.dob else "",
            "admission_date": student.admission_date.strftime('%Y-%m-%d') if student.admission_date else "",
            "monthly_fee": float(student.monthly_fee),
            "admission_amount": float(student.admission_amount),
            "discount_percent": float(student.discount_percent),
            "final_amount": float(student.final_amount),
            "course_id": student.course.id if student.course else "",
        })
    except StudentAdmission.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_course_data(request):
    course_id = request.GET.get("course_id")
    try:
        course = Course.objects.get(id=course_id)
        return JsonResponse({
            "duration": course.duration,
            "monthly_fee": float(course.monthly_fee or 0),
            "admission_fee": float(course.admission_fee or 0),
            "fees": float(course.total_fees or 0)
        })
    except Course.DoesNotExist:
        return JsonResponse({}, status=404)

# ================= PAYMENTS & STATEMENTS =================

def student_payments(request):
    students = StudentAdmission.objects.prefetch_related(
        "enrollments__payments"
    ).annotate(
        total_paid=Sum("enrollments__payments__amount")
    )
    return render(request, "student_portal/payments.html", {"students": students})

def make_payment(request):
    return render(request, "student_portal/pay.html")

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum



def student_statement(request, student_id):

    student = get_object_or_404(StudentAdmission, id=student_id)

    enrollments = (
        student.enrollments
        .select_related("course")
        .prefetch_related("payments")
        .order_by("admission_date")
    )

    overall_paid = 0
    overall_fine = 0
    course_data = []
    first_enrollment = enrollments.first()

    for enrollment in enrollments:
        payments = enrollment.payments.all().order_by("payment_date")

        if enrollment != first_enrollment:
            payments = payments.exclude(fee_type="ADMISSION")

        total_paid = payments.aggregate(total=Sum("amount"))["total"] or 0
        total_fine = payments.aggregate(total=Sum("fine"))["total"] or 0

        # ✅ NEW: calculate waived fine
        total_waived = 0
        for p in payments:
            if p.waive_fine:
                if p.waive_fine is True:
                    waived = p.fine or 0
                else:
                    waived = p.waive_fine or 0
            else:
                waived = 0

            total_waived += waived

        # ✅ NEW: net fine (after waive)
        net_fine = total_fine - total_waived

        overall_paid += total_paid
        overall_fine += total_fine

        course_data.append({
            "course": enrollment.course,
            "enrollment": enrollment,
            "payments": payments,
            "total_paid": total_paid,
            "total_fine": total_fine,
            "total_waived": total_waived,   # ✅ ADD THIS LINE
            "net_fine": net_fine,           # ✅ ADD THIS (optional but useful)
            "remaining": enrollment.total_fee - total_paid,
            "is_active": enrollment.is_active
        })

    context = {
        "student": student,
        "course_data": course_data,
        "overall_paid": overall_paid,
        "overall_fine": overall_fine,
        "grand_total": overall_paid + overall_fine,
    }

    # 🔥 PDF MODE
    # DEBUG (optional)
    print("DOWNLOAD PARAM:", request.GET.get("download"))

    if request.GET.get("download") == "pdf":
        return render(
            request,
            "student_portal/student_statement_pdf.html",
            context
        )
    
    return render(
        request,
        "student_portal/student_statement.html",
        context
    )


def student_dashboard(request):
    from student_portal.models import StudentAdmission

    student = StudentAdmission.objects.first()  # force test

    if student and student.is_suspended:
        return render(request, "student_portal/suspended.html", {
            "student_id": student.student_id
        })

    return render(request, "student_portal/dashboard.html")
# ================= PDF GENERATION =================

def generate_admission_form(request, pk):
    student_admission = get_object_or_404(StudentAdmission, pk=pk)
    prev_course = StudentAdmission.objects.filter(
        student_id=student_admission.student_id, 
        course_completed=True
    ).exclude(id=pk).order_by('-id').first()

    prev_data = None
    if prev_course:
        cert_info = Certificate.objects.filter(student=prev_course, is_published=True).first()
        prev_data = {
            'course_name': prev_course.course.course_name if prev_course.course else "N/A",
            'course_code': prev_course.course.course_code if prev_course.course else "N/A",
            'start_date': prev_course.joining_date,
            'end_date': cert_info.upload_date if cert_info else "N/A",
            'cert_no': cert_info.certificate_no if cert_info else "N/A",
            'mark_no': cert_info.marksheet_no if cert_info else "N/A",
        }

    template_path = 'admission_form_pdf.html'
    context = {'object': student_admission, 'prev_course': prev_data}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="admission_{student_admission.student_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
       return HttpResponse(f'Error: {pisa_status.err}')
    return response

# ================= ADMIN & BATCH LOGIC =================

def batchlistview(request):
    count = int(request.GET.get("count", 10))
    days = BatchDay.objects.all()
    times = BatchTiming.objects.all()
    students_by_time = {t.id: StudentAdmission.objects.filter(class_time=t) for t in times}

    context = {
        "setup_ready": days.exists() and times.exists(),
        "days": days,
        "times": times,
        "students_by_time": students_by_time,
        "count": count,
        "range": range(1, count + 1),
    }
    return render(request, "admin/batch_list.html", context)

def franchise_account(request):
    return render(request, "student_portal/franchiseaccount.html")

# ================= ACCOUNT SECURITY & OTP LOGIC =================

def send_old_email_otp(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=403)
            
        email = request.user.email
        otp = str(random.randint(100000, 999999))
        request.session["old_email_otp"] = otp
        request.session["old_email_exp"] = (datetime.now() + timedelta(minutes=5)).timestamp()

        try:
            send_mail(
                "Verify Current Email",
                f"Your OTP is: {otp}",
                "your_email@gmail.com",   # ✅ FIXED
                [email],
                fail_silently=True
            )
        except Exception as e:
            print("🔥 Email Error:", e)
        return JsonResponse({"status": "sent"})

def send_new_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"status": "error", "error": "Email required"}, status=400)

        otp = str(random.randint(100000, 999999))
        request.session["new_email"] = email
        request.session["new_email_otp"] = otp
        request.session["new_email_exp"] = (datetime.now() + timedelta(minutes=5)).timestamp()

        try:
            send_mail(
                "Verify New Email",
                f"Your verification code for your new email is {otp}",
                "settings.DEFAULT_FROM_EMAIL",
                [email],
                fail_silently=True
            )
            return JsonResponse({"status": "sent"})
        except Exception as e:
            logger.error(f"SMTP Error: {e}")
            return JsonResponse({"status": "error", "error": "Email service slow. Check terminal."}, status=500)
    return JsonResponse({"status": "error", "error": "Invalid request"}, status=400)


from django.contrib.auth import get_user_model



from django.contrib.auth import logout, get_user_model
from django.core.mail import send_mail

from django.contrib.auth import get_user_model

from django.core.mail import send_mail

from franchise.models import Franchise

def update_email(request):

    # ✅ Only POST allowed
    if request.method != "POST":
        return JsonResponse({"status": "error", "error": "Invalid request"}, status=405)

    # ✅ Must be logged in
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({"status": "error", "error": "Session expired. Please login again."}, status=403)

    try:
        # 🔹 Inputs
        new_email = request.POST.get('email')
        old_otp_input = request.POST.get('old_otp')
        new_otp_input = request.POST.get('new_otp')

        # 🔹 Session
        session_old_otp = request.session.get('old_email_otp')
        session_new_otp = request.session.get('new_email_otp')
        session_new_email = request.session.get('new_email')

        old_exp = request.session.get("old_email_exp")
        new_exp = request.session.get("new_email_exp")

        # ✅ Validation
        if not all([new_email, old_otp_input, new_otp_input]):
            return JsonResponse({"status": "error", "error": "All fields required."})

        if not session_old_otp or not session_new_otp:
            return JsonResponse({"status": "error", "error": "Session expired. Resend OTPs."})

        # ✅ Expiry check
        if old_exp and new_exp:
            try:
                if datetime.now().timestamp() > float(old_exp) or datetime.now().timestamp() > float(new_exp):
                    return JsonResponse({"status": "error", "error": "OTP expired. Please resend OTP."})
            except:
                return JsonResponse({"status": "error", "error": "Session expired. Please resend OTP."})

        # ✅ Attempt limit
        attempts = request.session.get("otp_attempts", 0)
        if attempts >= 5:
            return JsonResponse({"status": "error", "error": "Too many attempts. Try again later."})

        request.session["otp_attempts"] = attempts + 1

        # ✅ OTP check
        if old_otp_input != str(session_old_otp) or new_otp_input != str(session_new_otp):
            return JsonResponse({"status": "error", "error": "Invalid OTP codes."})

        # ✅ Email match
        if new_email != session_new_email:
            return JsonResponse({"status": "error", "error": "Email mismatch."})

        # ✅ Duplicate check
        User = get_user_model()
        if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
            return JsonResponse({"status": "error", "error": "Email already in use."})

        # ✅ Get user safely
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "error": "User not found. Please login again."})

        old_email = user.email

        # 🔥 HANDLE BOTH CASES (IMPORTANT PART)
        franchise = Franchise.objects.filter(user=user).first()

        if franchise:
            # ✅ Franchise user
            franchise.email = new_email
            franchise.save()

        # ✅ Always update main user
        user.email = new_email
        user.save()

        # ✅ Send notification (safe)
        send_mail(
            "Email Updated Successfully",
            "Your new email is now active for your account.",
            "settings.DEFAULT_FROM_EMAIL",
            [new_email],
            fail_silently=True
        )

        # ✅ Clean session
        for key in [
            'old_email_otp',
            'new_email_otp',
            'new_email',
            'old_email_exp',
            'new_email_exp',
            'otp_attempts'
        ]:
            request.session.pop(key, None)

        return JsonResponse({
            "status": "success",
            "message": "Email updated successfully!"
        })

    except Exception as e:
        import traceback
        print("🔥 FULL ERROR:")
        traceback.print_exc()
        return JsonResponse({"status": "error", "error": "Something went wrong."}, status=500)

def verify_account_change(request):
    """ Handles Username Updates """
    if request.method == "POST":
        try:
            otp = request.POST.get("otp")
            new_username = request.POST.get("username")
            session_otp = request.session.get("old_email_otp")

            if not otp or not new_username:
                return JsonResponse({"status": "error", "error": "OTP and Username required"})

            if str(otp) == str(session_otp):
                user = request.user
                user.username = new_username
                user.save()
                return JsonResponse({"status": "success", "message": "Username updated!"})
            return JsonResponse({"status": "error", "error": "Invalid OTP"})
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)
    return JsonResponse({"status": "error", "error": "Invalid request"}, status=400)

def update_password(request):
    """ Handles Password Updates """
    if request.method == "POST":
        try:
            otp = request.POST.get("otp")
            new_pw = request.POST.get("password")
            session_otp = request.session.get("old_email_otp")

            if not otp or not new_pw:
                return JsonResponse({"status": "error", "error": "OTP and Password required"})

            if str(otp) == str(session_otp):
                user = request.user
                user.set_password(new_pw)
                user.save()
                update_session_auth_hash(request, user)
                return JsonResponse({"status": "success", "message": "Password updated!"})
            return JsonResponse({"status": "error", "error": "Invalid OTP"})
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)
    return JsonResponse({"status": "error", "error": "Invalid request"}, status=400)



from student_portal.models import CourseEnrollment, get_safe_date

def calculate_fee(request):
    from django.db import connection

    print("=" * 50)
    print("DATABASE =", connection.settings_dict["NAME"])
    print("=" * 50)
    print("=" * 50)
    print("REQUEST.GET =", request.GET)
    print("PAYMENT DATE RAW =", request.GET.get("payment_date"))
    print("=" * 50)
    enrollment_id = request.GET.get(
        "enrollment_id"
    )

    payment_date = request.GET.get(
        "payment_date"
    )
    print(
        "REQUEST.GET payment_date =",
        request.GET.get("payment_date")
    )
    print(
        "AJAX PAYMENT DATE =",
        payment_date
    )

    if not enrollment_id or not payment_date:
        return JsonResponse(
            {"error": "Missing data"},
            status=400
        )

    try:

        enrollment = (
            CourseEnrollment.objects.get(
                id=enrollment_id
            )
        )

        calc_date = datetime.strptime(
            payment_date,
            "%Y-%m-%d"
        ).date()
        
        print("AJAX PAYMENT DATE =", payment_date)
        print("CALC DATE =", calc_date)



        data = calculate_student_dues(
            enrollment,
            calc_date
        )
        print("=" * 50)
        print("CALCULATOR RETURN")
        print(data)
        print("=" * 50)

        from django.db.models import Sum
        from decimal import Decimal

        paid_total = (
            Fee.objects
            .filter(
                enrollment=enrollment,
                fee_type__in=["MONTHLY", "ADVANCE"]
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )

        remaining_course_fee = max(
            (enrollment.total_fee or Decimal("0")) - paid_total,
            Decimal("0")
        )

        final_amount = min(
            data["amount"],
            remaining_course_fee
        )

        
        return JsonResponse({

            "monthly_fee": float(final_amount),
            "amount": float(final_amount),

            "fine":
                float(data["fine"]),

            "total": float(final_amount + data["fine"]),

            "due_date":
                data[
                    "due_date"
                ].strftime("%Y-%m-%d"),

            "pending_months":
                data["pending_months"]

        })

    except CourseEnrollment.DoesNotExist:

        return JsonResponse(
            {"error":"Enrollment not found"},
            status=404
        )

    except Exception as e:

        print("FEE API ERROR:", e)

        return JsonResponse(
            {"error": str(e)},
            status=500
        )


from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

@csrf_exempt
def send_otp(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        })

    data = json.loads(request.body)
    # print(data)
    login_mode = data.get("mode")
    login_value = data.get("value")
    dob = data.get("dob")
    from .models import StudentAdmission

    if login_mode == "email":

        student = StudentAdmission._base_manager.filter(
            email=login_value,
            dob=dob
        ).first()

    else:
        raw_student_id = str(login_value or "").strip()
        parts = raw_student_id.split("/")

        student = None

        if (
            len(parts) == 3
            and parts[0].strip()
            and parts[1].strip()
            and parts[2].strip().isdigit()
        ):
            prefix = parts[0].strip().upper()
            branch = parts[1].strip().upper()
            number = parts[2].strip()

            normalized_student_id = f"{prefix}/{branch}/{number}"

            student = StudentAdmission.original_objects.filter(
                student_id=normalized_student_id,
                dob=dob
            ).first()

   
    if not student:

        return JsonResponse({
            "success": False,
            "message": "Invalid credentials"
        })

    otp = str(random.randint(100000, 999999))

    request.session["student_otp"] = otp
    request.session["student_id"] = student.student_id
    request.session.save()

    # print("Student OTP sent successfully.")
    # print("SESSION KEY =", request.session.session_key)
    subject = "Student Portal Login OTP"

    message = f"""
    Hello {student.name},

    Your One-Time Password (OTP) for logging into the Smart Computer Institute Student Portal is:

    {otp}

    This OTP is valid for 10 minutes.

    If you did not request this login, please ignore this email.

    Regards,
    Smart Computer Institute
    """

    html_message = f"""
    <html>
    <body style="margin:0;padding:0;background:#eef2f7;font-family:'Segoe UI',Arial,sans-serif;">

    <div style="max-width:650px;margin:30px auto;background:#ffffff;border-radius:12px;
    overflow:hidden;box-shadow:0 4px 15px rgba(0,0,0,0.08);">

        <div style="background:linear-gradient(135deg,#2b7de9,#1a4fb5);
        padding:20px;text-align:center;color:white;">
            <h2 style="margin:0;">Smart Computer Institute</h2>
            <p style="margin:5px 0 0;font-size:14px;">Student Portal Login Verification</p>
        </div>

        <div style="padding:25px;color:#333;">

            <p>Dear <b>{student.name}</b>,</p>

            <p>
                A login request has been received for your Student Portal account.
                Please use the OTP below to continue.
            </p>

            <div style="
                background:#f5f9ff;
                border:2px dashed #2b7de9;
                border-radius:8px;
                text-align:center;
                padding:20px;
                margin:25px 0;
            ">
                <div style="font-size:13px;color:#666;">YOUR LOGIN OTP</div>

                <div style="
                    font-size:36px;
                    font-weight:bold;
                    color:#2b7de9;
                    letter-spacing:8px;
                    margin-top:10px;
                ">
                    {otp}
                </div>
            </div>

            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:10px;border-bottom:1px solid #eee;"><b>Student ID</b></td>
                    <td style="padding:10px;border-bottom:1px solid #eee;">{student.student_id}</td>
                </tr>
            </table>

            <p style="margin-top:20px;">
                This OTP will expire in <b>10 minutes</b>.
            </p>

            <p style="color:#666;">
                If you did not request this login, you can safely ignore this email.
            </p>

            <p style="margin-top:25px;">
                Regards,<br>
                <b>Smart Computer Institute</b>
            </p>

        </div>

        <div style="background:#f1f1f1;text-align:center;padding:15px;
        font-size:12px;color:#666;">
            © Smart Computer Institute • All Rights Reserved
        </div>

    </div>

    </body>
    </html>
    """

    mailjet = Client(
        auth=(
            os.environ.get("MAILJET_API_KEY"),
            os.environ.get("MAILJET_SECRET_KEY")
        ),
        version="v3.1"
    )

    data = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("DEFAULT_FROM_EMAIL"),
                    "Name": "Smart Computer Institute"
                },
                "To": [
                    {
                        "Email": student.email,
                        "Name": student.name
                    }
                ],
                "Subject": subject,
                "TextPart": message,
                "HTMLPart": html_message
            }
        ]
    }

    try:
        result = mailjet.send.create(data=data)

        print("MAILJET STATUS:", result.status_code)
        print("MAILJET RESPONSE:", result.json())

        if result.status_code not in [200, 201]:
            return JsonResponse({
                "success": False,
                "message": "Mailjet rejected the email",
                "mailjet_response": result.json()
            }, status=500)

    except Exception as e:
        print("MAILJET ERROR:", str(e))

        return JsonResponse({
            "success": False,
            "message": "Mailjet connection failed"
        }, status=500)


    return JsonResponse({
        "success": True,
        "message": "OTP sent successfully"
    })

@csrf_exempt
def verify_otp(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        })

    data = json.loads(request.body)

    otp = data.get("otp")

    print("COOKIES =", request.COOKIES)
    print("VERIFY SESSION KEY =", request.session.session_key)
    print("ALL SESSION DATA =", dict(request.session))
    print("SESSION OTP =", request.session.get("student_otp"))
    print("INPUT OTP =", otp)

    session_otp = request.session.get("student_otp")

    if str(otp) == str(session_otp):

        return JsonResponse({
            "success": True,
            "student_id": request.session["student_id"]
        })

    return JsonResponse({
        "success": False,
        "message": "Invalid OTP"
    })



def get_profile(request):

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return JsonResponse({
            "success": False,
            "message": "Login required"
        })

    student = StudentAdmission._base_manager.get(
        student_id=student_id
    )


    return JsonResponse({

        "success": True,

        # Personal Information
        "name": student.name,
        "student_id": student.student_id,
        "guardian_name": student.guardian_name,
        "gender": student.get_gender_display() if student.gender else "",
        "qualification": student.qualification,
        "email": student.email,
        "phone": student.phone,
        "dob": student.dob,

        # Photo
        "passport_photo":
            request.build_absolute_uri(student.passport_photo.url)
            if student.passport_photo
            else "",

        # Course
        "course": (
            f"{student.course.code} - {student.course.name}"
            if student.course
            else ""
        ),

        "course_type": student.course_type,
        "course_duration": student.course_duration,
        "monthly_fee": float(student.monthly_fee or 0),
        "admission_date": student.admission_date,

        # Address & Documents
        "address": student.address,
        "document_type": student.get_document_type_display()
            if student.document_type
            else "",
        "document_number": student.document_number,

        # Payment Information
        "admission_amount": float(student.admission_amount or 0),
        "advance_fees": float(student.advance_fees or 0),
        "discount_percent": float(student.discount_percent or 0),
        "final_amount": float(student.final_amount or 0),
        "admission_pay_via": student.admission_pay_via,
        "receipt_no": student.receipt_no,

        # System Information
        "is_active": student.is_active,
        "is_suspended": student.is_suspended,
        "course_completed": student.course_completed,
        "is_freezed": student.is_freezed,
  
        "form_pdf": request.build_absolute_uri(
            reverse("student_pdf")
        ),


        # Header
        "franchise_name":
            student.franchise.institute_name
            if student.franchise
            else "SCI Portal",

    })




def get_course_history(request):

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return JsonResponse({
            "success": False
        })

    student = StudentAdmission._base_manager.get(
        student_id=student_id
    )

    certificate = Certificate._base_manager.filter(
        student__student_id=student.student_id,
        completed_course=student.course,
        is_published=True
    ).first()
    print("Student =", student)
    print("Course =", student.course)
    print("Certificate =", certificate)

    if certificate:
        print("End date =", certificate.end_date)
    data = [

        {

            "code": student.course.code,

            "name": student.course.name,

            "duration": student.course.duration,

            "start_date":
                student.admission_date.strftime("%d-%m-%Y")
                if student.admission_date
                else "-",

            "end_date":
                certificate.end_date.strftime("%d-%m-%Y")
                if certificate and certificate.end_date
                else None,

            "status":
                "Completed"
                if student.course_completed
                else "Running"

        }

    ]

    return JsonResponse({

        "success": True,

        "courses": data

    })




def get_marks(request):

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return JsonResponse({
            "success": False
        })

    student = StudentAdmission._base_manager.get(
        student_id=student_id
    )

    marks = StudentMarks.objects.filter(
        student=student
    ).select_related(
        "exam"
    )

    data = []

    for mark in marks:

        data.append({

            "exam_name":
                mark.exam.exam_name,

            "marks":
                mark.marks,

            "total_marks":
                mark.exam.total_marks,

            "result":
                "Pass"
                if mark.marks >= 40
                else "Fail"

        })

    return JsonResponse({

        "success": True,

        "marks": data

    })


def get_payments(request):

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return JsonResponse({
            "success": False
        })

    student = StudentAdmission._base_manager.get(
        student_id=student_id
    )

    payments = Fee._base_manager.filter(
        enrollment__student=student
    ).order_by(
        "-payment_date"
    )

    data = []

    for payment in payments:

        data.append({

            "date":
                payment.payment_date,

            "due_date":
                payment.due_date,

            "receipt_no":
                payment.receipt_no,

            "fee_type":
                payment.fee_type,

            "amount":
                float(payment.amount),

            "fine":
                float(payment.fine),

            "fine_waived":
                payment.waive_fine,

            "total_amount":
                float(payment.total_amount),

            "pay_via":
                payment.pay_via

        })

    return JsonResponse({

        "success": True,

        "payments": data

    })

def get_certificates(request):

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return JsonResponse({
            "success": False
        })

    student = StudentAdmission._base_manager.get(
        student_id=student_id
    )

    certificates = Certificate._base_manager.filter(
        student=student,
        is_published=True
    ).order_by(
        "-upload_date"
    )

    data = []

    for certificate in certificates:

        data.append({

            "certificate_no":
                certificate.certificate_no,

            "course":
                certificate.completed_course.name,

            "upload_date":
                certificate.upload_date,

            "certificate_file":
                certificate.certificate_file.url,

            "marksheet_file":
                (
                    certificate.marksheet_file.url
                    if certificate.marksheet_file
                    else None
                )

        })

    return JsonResponse({

        "success": True,

        "certificates": data

    })



from management_portal.models import Notice
from .models import StudentAdmission


def get_notices(request):

    student_id = request.session.get(
        "student_id"
    )

    if not student_id:

        return JsonResponse({

            "success": False

        })

    student = StudentAdmission._base_manager.get(

        student_id=student_id

    )

    notices = []

    for notice in Notice._base_manager.all():

        # Notice sent to this student specifically
        if notice.students.filter(
            pk=student.pk
        ).exists():

            notices.append(notice)

        # Notice sent to all students of the same franchise
        elif (
            notice.students.count() == 0
            and
            (
                notice.franchise == student.franchise
                or
                notice.franchise is None
            )
        ):

            notices.append(notice)

    notices = sorted(

        notices,

        key=lambda x: x.created_at,

        reverse=True

    )

    data = []

    for notice in notices:

        data.append({

            "title":
                notice.title,

            "body":
                notice.body,

            "date":
                notice.created_at

        })

    return JsonResponse({

        "success": True,

        "notices": data

    })



from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import StudentAdmission, Notice # Adjust import path if needed

def get_recent_notices(request):
    # This retrieves the string (e.g., "MG/SLG/0001") from session storage
    student_session_id = request.session.get("student_id") 
    
    if not student_session_id:
        return JsonResponse({"success": False, "notices": []})

    try:
        # Match using the alphanumeric 'student_id' string field
        student = StudentAdmission._base_manager.get(student_id=student_session_id)
    except (ObjectDoesNotExist, ValueError):
        # Graceful fallback: returns a clean 200 with empty list instead of a 500 error crash
        return JsonResponse({"success": True, "notices": []})

    seven_days_ago = timezone.now() - timedelta(days=7)

    # Filter notices linked directly to this specific student record instance
    notices = (
        Notice._base_manager
        .filter(
            students=student,
            is_sent=True,
            created_at__gte=seven_days_ago
        )
        .distinct()
        .order_by("-created_at")[:10]
    )

    return JsonResponse({
        "success": True,
        "notices": [
            {
                "title": notice.title,
                "body": notice.body,
                "created_at": notice.created_at.strftime("%d/%m/%Y")
            }
            for notice in notices
        ]
    })


from django.contrib import admin
from .admin import StudentAdmissionAdmin
from .models import StudentAdmission

def student_pdf(request):

    student_id = request.session.get("student_id")
    print("SESSION STUDENT ID =", student_id)
    if not student_id:
        return JsonResponse({
            "success": False,
            "message": "Login required"
        })

    student = StudentAdmission._base_manager.get(
        student_id=student_id
    )

    admin_instance = StudentAdmissionAdmin(
        StudentAdmission,
        admin.site
    )

    return admin_instance.generate_pdf(
        request,
        student.id
    )

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def download_statement(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return HttpResponse("Login required")

    student = StudentAdmission._base_manager.get(student_id=student_id)
    fees = Fee._base_manager.filter(enrollment__student=student).order_by("payment_date")
    admission_fees = fees.filter(
        fee_type="ADMISSION"
    )

    monthly_fees = fees.exclude(
        fee_type="ADMISSION"
    )
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.student_id}_statement.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    # --- Header Section ---
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "SMART COMPUTER INSTITUTE")
    
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, y, "Payment Statement")
    
    y -= 15
    p.setStrokeColor(colors.black)
    p.line(40, y, width - 40, y)

    # --- Student Profile Section ---
    y -= 40
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, f"Student ID   : {student.student_id}")
    y -= 18
    p.drawString(50, y, f"Student Name : {student.name}")
    y -= 18
    p.drawString(50, y, f"Course       : {student.course.code} - {student.course.name}")

    # Passport Photo (Top Right)
    # Passport Photo
    if student.passport_photo:
        try:
            photo_x = width - 140
            photo_y = y - 40

            p.rect(
                photo_x,
                photo_y,
                80,
                100
            )

            p.drawImage(
                student.passport_photo.path,
                photo_x,
                photo_y,
                width=80,
                height=100
            )

        except Exception as e:
            print("Photo error:", e)

    # Leave enough space below photo
    y -= 60

    # --- Table Header ---
    y -= 10
    p.line(40, y + 15, width - 40, y + 15) # Top line of header
    p.setFont("Helvetica-Bold", 9)
    
    # Column alignment logic
    cols = {
        "due": 40,
        "pay": 95,
        "rec": 150,
        "type": 210,
        "amt": 270,
        "fine": 325,
        "waived": 380,
        "total": 445,
        "via": 515
    }
    
    p.drawString(cols["due"], y, "Due Date")
    p.drawString(cols["pay"], y, "Pay Date")
    p.drawString(cols["rec"], y, "Receipt")
    p.drawString(cols["type"], y, "Type")
    p.drawString(cols["amt"], y, "Amount")
    p.drawString(cols["fine"], y, "Fine")
    p.drawString(cols["waived"], y, "Waived")
    p.drawString(cols["total"], y, "Total")
    p.drawString(cols["via"], y, "Via")
    
    y -= 8
    p.line(40, y, width - 40, y) # Bottom line of header
    y -= 20

    # --- Table Rows ---
    p.setFont("Helvetica-Bold", 11)
    p.drawString(
        40,
        y,
        "ADMISSION PAYMENT"
    )

    y -= 20

    admission_total = 0
    monthly_total = 0

    p.setFont("Helvetica", 8)

    for fee in admission_fees:
        # Check if we are running out of page space
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 8)

        due_date = fee.due_date.strftime("%d-%m-%y") if fee.due_date else "-"
        pay_date = fee.payment_date.strftime("%d-%m-%y")
        waived = "Yes" if fee.waive_fine else "No"

        p.drawString(cols["due"], y, due_date)
        p.drawString(cols["pay"], y, pay_date)
        p.drawString(cols["rec"], y, str(fee.receipt_no))
        p.drawString(cols["type"], y, fee.fee_type[:10]) # Allowed more chars
        p.drawString(cols["amt"], y, f"Rs.{int(fee.amount)}")
        p.drawString(cols["fine"], y, f"Rs.{int(fee.fine)}")
        p.drawString(cols["waived"], y, waived)
        p.drawString(cols["total"], y, f"Rs.{int(fee.total_amount)}")
        p.drawString(cols["via"], y, fee.pay_via)

        admission_total += fee.total_amount
        y -= 20 # Row spacing

    # ---------- MONTHLY PAYMENT SECTION ----------
    y -= 20
    p.line(40, y, width - 40, y)
    y -= 25
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, y, "MONTHLY PAYMENTS")
    y -= 20
    p.setFont("Helvetica", 8)

    for fee in monthly_fees:

        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 8)

        due_date = fee.due_date.strftime("%d-%m-%y") if fee.due_date else "-"
        pay_date = fee.payment_date.strftime("%d-%m-%y")
        waived = "Yes" if fee.waive_fine else "No"

        p.drawString(cols["due"], y, due_date)
        p.drawString(cols["pay"], y, pay_date)
        p.drawString(cols["rec"], y, str(fee.receipt_no))
        p.drawString(cols["type"], y, fee.fee_type[:10])
        p.drawString(cols["amt"], y, f"Rs.{int(fee.amount)}")
        p.drawString(cols["fine"], y, f"Rs.{int(fee.fine)}")
        p.drawString(cols["waived"], y, waived)
        p.drawString(cols["total"], y, f"Rs.{int(fee.total_amount)}")
        p.drawString(cols["via"], y, fee.pay_via)

        monthly_total += fee.total_amount
        y -= 20

    # ---------- FOOTER ----------
    y -= 10
    p.line(40, y + 5, width - 40, y + 5)

    # y -= 20
    # p.setFont("Helvetica-Bold", 11)
    # p.drawString(
    #     40,
    #     y,
    #     f"Admission Fee Paid : Rs.{int(admission_total)}"
    # )

    y -= 20
    p.setFont("Helvetica-Bold", 11)
    p.drawString(
        40,
        y,
        f"Monthly Fees Paid : Rs.{int(monthly_total)}"
    )

    y -= 20
    p.setFont("Helvetica-Bold", 13)
    p.drawString(
        40,
        y,
        f"GRAND TOTAL OF COURSE FEES : Rs.{int(monthly_total)}"
    )

    y -= 50
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(
        width / 2,
        y,
        "*** This is a system-generated document and requires no signature ***"
    )

    y -= 15
    p.setFont("Helvetica", 7)
    p.drawCentredString(
        width / 2,
        y,
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

  
    p.save()

    return response


from .models import Certificate
from django.http import FileResponse, HttpResponse

def download_certificate(request):

    student_id = request.session.get(
        "student_id"
    )

    certificate = Certificate._base_manager.filter(
        student__student_id=student_id
    ).first()

    if not certificate:
        return HttpResponse(
            "Certificate not found"
        )

    return FileResponse(
        certificate.certificate_file.open("rb"),
        as_attachment=True,
        filename=certificate.certificate_file.name.split("/")[-1]
    )


def download_marksheet(request):

    student_id = request.session.get(
        "student_id"
    )

    certificate = Certificate._base_manager.filter(
        student__student_id=student_id
    ).first()

    if not certificate:
        return HttpResponse(
            "Marksheet not found"
        )

    return FileResponse(
        certificate.marksheet_file.open("rb"),
        as_attachment=True,
        filename=certificate.marksheet_file.name.split("/")[-1]
    )


from django.http import JsonResponse
from .models import Course

# def get_courses(request):
#     courses = Course._base_manager.all()

#     # print("TOTAL COURSES =", courses.count())

#     data = []

#     for course in courses:
#         print(course.id, course.name)

#         data.append({
#             "id": course.id,
#             "code": course.code,
#             "name": course.name,
#         })

#     return JsonResponse({"courses": data})

from django.http import JsonResponse
from .models import Certificate


def verify_certificate(request):
    certificate_no = request.GET.get("certificate_no")

    try:
        certificate = Certificate._base_manager.get(
            certificate_no=certificate_no,
            is_published=True
        )

        return JsonResponse({
            "valid": True,
            "photo": (
                request.build_absolute_uri(
                    certificate.student.passport_photo.url
                )
                if certificate.student.passport_photo
                else None
            ),
            "student_name": certificate.student.name,
            "course": certificate.completed_course.name,
            "certificate_no": certificate.certificate_no,
            "end_date": certificate.end_date,
        })

    except Certificate.DoesNotExist:

        return JsonResponse({
            "valid": False
        })


import os
from django.http import JsonResponse
from django.core.management import call_command


def fee_reminder_cron(request):

    token = request.GET.get("token")

    if token != os.environ.get("FEE_CRON_SECRET"):
        return JsonResponse(
            {"error": "Unauthorized"},
            status=401
        )

    try:
        call_command("send_fee_reminders")

        return JsonResponse({
            "success": True,
            "message": "Fee reminder job completed"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)