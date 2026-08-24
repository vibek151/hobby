import os
import requests
from django.conf import settings
from django.template.loader import render_to_string


def send_student_email(
    student,
    subject,
    template,
    context,
    files=None,
    connection=None
):
    html_content = render_to_string(
        template,
        context
    )

    message = {
        "From": {
            "Email": settings.DEFAULT_FROM_EMAIL,
            "Name": "Smart Computer Institute"
        },
        "To": [
            {
                "Email": student.email
            }
        ],
        "Subject": subject,
        "HTMLPart": html_content
    }

    # Add PDF attachments if provided
    if files:
        attachments = []

        for file in files:
            attachments.append({
                "ContentType": "application/pdf",
                "Filename": file[0],
                "Base64Content": file[1]
            })

        message["Attachments"] = attachments

    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(
            os.environ["MAILJET_API_KEY"],
            os.environ["MAILJET_SECRET_KEY"]
        ),
        json={
            "Messages": [message]
        }
    )

    response.raise_for_status()

    return response.json()