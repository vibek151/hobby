from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
import os

def send_certificate_email(instance, force=False):
    instance.refresh_from_db()
    
    # if instance.email_sent and not force:
    #     print(f"⛔ Certificate {instance.id} already sent, skipping.")
    #     return

    student = instance.student
    if not student or not student.email:
        print(f"❌ No email found for student in instance {instance.id}")
        return

    # --- Data Preparation ---
    email_address = student.email.strip().lower()
    subject = "Certificate Issued"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email_address]
    
    student_id = getattr(student, 'student_id', 'N/A')
    course_name = instance.completed_course.name if instance.completed_course else "your course"
    download_text = "Please find your documents attached below."

    if instance.marksheet_file:
        issue_text = "Your certificate & marksheet have been officially issued by our institute."
    else:
        issue_text = "Your certificate has been officially issued by our institute."


    # --- HTML Template (Logo Removed) ---
    html_content = f"""
    <html>
    <body style="margin:0; padding:0; background:#eef2f7; font-family: 'Segoe UI', Arial, sans-serif;">
        <div style="max-width:650px; margin:30px auto; background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.08);">
            <div style="background:linear-gradient(135deg,#2b7de9,#1a4fb5); padding:20px; text-align:center; color:white;">
                <h2 style="margin:0;">Smart Computer Institute</h2>
                <p style="margin:5px 0 0; font-size:14px; opacity:0.9;">Certificate Issuance Notification</p>
            </div>
            <div style="padding:25px; color:#333;">
                <p style="font-size:16px;">Dear <b>{student.name}</b>,</p>
                <p style="font-size:15px; line-height:1.6;">
                    We are delighted to inform you that you have successfully completed the course 
                    <b style="color:#2b7de9;">{course_name}</b>.
                </p>
                <p style="font-size:15px;">{issue_text}</p>
                <div style="background:#f5f9ff; border-left:4px solid #2b7de9; padding:12px 15px; margin:20px 0; border-radius:6px;">
                    {download_text}
                </div>
                <table style="width:100%; margin-top:15px; border-collapse:collapse;">
                    <tr>
                        <td style="padding:10px; border-bottom:1px solid #eee;"><b>Student ID</b></td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">{student_id}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border-bottom:1px solid #eee;"><b>Certificate No</b></td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">{instance.certificate_no}</td>
                    </tr>"""

    if instance.marksheet_no:
        html_content += f"""
                    <tr>
                        <td style="padding:10px; border-bottom:1px solid #eee;"><b>Marksheet No</b></td>
                        <td style="padding:10px; border-bottom:1px solid #eee;">{instance.marksheet_no}</td>
                    </tr>"""

    html_content += """
                </table>
                <p style="margin-top:25px; font-size:15px; line-height:1.6;">
                    We congratulate you on your achievement and wish you continued success in your future endeavors.
                </p>
                <p style="margin-top:20px;"> Warm regards,<br><b>Smart Computer Institute</b></p>
            </div>
            <div style="background:#f1f1f1; text-align:center; padding:15px; font-size:12px; color:#666;">
                © Smart Computer Institute • All Rights Reserved
            </div>
        </div>
    </body>
    </html>"""
    # --- Connection & Sending (UPDATED CLEAN VERSION) ---

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")

    # 📄 Attach Certificate
    if instance.certificate_file and os.path.exists(instance.certificate_file.path):
        try:
            with open(instance.certificate_file.path, "rb") as f:
                msg.attach("Certificate.pdf", f.read(), "application/pdf")
        except Exception as e:
            print(f"❌ Certificate attachment error: {e}")

    # 📄 Attach Marksheet
    if instance.marksheet_file and os.path.exists(instance.marksheet_file.path):
        try:
            with open(instance.marksheet_file.path, "rb") as f:
                msg.attach("Marksheet.pdf", f.read(), "application/pdf")
        except Exception as e:
            print(f"❌ Marksheet attachment error: {e}")

    # 📤 Send Email
    try:
        msg.send(fail_silently=False)

        # ✅ Update DB safely (NO SIGNAL LOOP)
        from student_portal.models import Certificate
        Certificate.objects.filter(pk=instance.pk).update(
            email_sent=True,
            email_error=None
        )

        print(f"✅ Email sent successfully for ID {instance.id}")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email failed for ID {instance.id}: {error_msg}")

        from student_portal.models import Certificate
        Certificate.objects.filter(pk=instance.pk).update(
            email_error=error_msg
        )