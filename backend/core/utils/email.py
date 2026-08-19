# import threading
# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
# import time

# def send_email_async(subject, message, recipient_list, html_message=None, files=None):

#     def send():
#         try:
#             time.sleep(1.5)
#             print("SMTP USER:", settings.EMAIL_HOST_USER)
#             print("SMTP PASSWORD SET:", bool(settings.EMAIL_HOST_PASSWORD))
#             msg = EmailMultiAlternatives(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 recipient_list,
#             )

#             # HTML support
#             if html_message:
#                 msg.attach_alternative(html_message, "text/html")

#             # Attach PDF files
#             if files:
#                 for file_name, file_content in files:
#                     print(f"📎 Attaching: {file_name}")
#                     print(f"📦 Size: {len(file_content)} bytes")
#                     msg.attach(file_name, file_content, "application/pdf")
#             else:
#                 print("❌ No files received by send_email_async()")

#             msg.send(fail_silently=False)

#             print("✅ Email sent successfully")

#         except Exception as e:
#             print("❌ Email Error:", e)

#     threading.Thread(target=send, daemon=True).start()
#     # send()

import threading
import os
import base64
import requests


def send_email_async(
    subject,
    message,
    recipient_list,
    html_message=None,
    files=None
):

    def send():
        try:
            attachments = []

            if files:
                for file_name, file_content in files:
                    print(f"📎 Attaching: {file_name}")
                    print(f"📦 Size: {len(file_content)} bytes")

                    attachments.append({
                        "ContentType": "application/pdf",
                        "Filename": file_name,
                        "Base64Content": base64.b64encode(
                            file_content
                        ).decode("utf-8")
                    })

            message_data = {
                "From": {
                    "Email": "settings.DEFAULT_FROM_EMAIL",
                    "Name": "Smart Computer Institute"
                },
                "To": [
                    {
                        "Email": email
                    }
                    for email in recipient_list
                ],
                "Subject": subject,
                "TextPart": message,
            }

            if html_message:
                message_data["HTMLPart"] = html_message

            if attachments:
                message_data["Attachments"] = attachments

            response = requests.post(
                "https://api.mailjet.com/v3.1/send",
                auth=(
                    os.environ["MAILJET_API_KEY"],
                    os.environ["MAILJET_SECRET_KEY"]
                ),
                json={
                    "Messages": [message_data]
                },
                timeout=30,
            )

            print("MAILJET STATUS:", response.status_code)
            print("MAILJET RESPONSE:", response.text)

            response.raise_for_status()

            print("✅ Email sent successfully through Mailjet")

        except Exception as e:
            print("❌ Mailjet Email Error:", e)

    threading.Thread(
        target=send,
        daemon=True
    ).start()