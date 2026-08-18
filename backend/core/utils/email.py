import threading
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import time

def send_email_async(subject, message, recipient_list, html_message=None, files=None):

    def send():
        try:
            time.sleep(1.5)
            print("SMTP USER:", settings.EMAIL_HOST_USER)
            print("SMTP PASSWORD SET:", bool(settings.EMAIL_HOST_PASSWORD))
            msg = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
            )

            # HTML support
            if html_message:
                msg.attach_alternative(html_message, "text/html")

            # Attach PDF files
            if files:
                for file_name, file_content in files:
                    print(f"📎 Attaching: {file_name}")
                    print(f"📦 Size: {len(file_content)} bytes")
                    msg.attach(file_name, file_content, "application/pdf")
            else:
                print("❌ No files received by send_email_async()")

            msg.send(fail_silently=False)

            print("✅ Email sent successfully")

        except Exception as e:
            print("❌ Email Error:", e)

    threading.Thread(target=send, daemon=True).start()
    # send()