import os
import requests

from django.contrib.auth.forms import PasswordResetForm


class MailjetPasswordResetForm(PasswordResetForm):

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        from django.template.loader import render_to_string
        context["domain"] = "smartci.in"
        context["protocol"] = "https"
        subject = "Password Reset | Smart Computer Institute"

        text_content = render_to_string(
            email_template_name,
            context
        )

        html_content = None

        if html_email_template_name:
            html_content = render_to_string(
                html_email_template_name,
                context
            )

        message = {
            "From": {
                "Email": "noreply@smartci.in",
                "Name": "Smart Computer Institute",
            },
            "To": [
                {
                    "Email": to_email,
                }
            ],
            "Subject": subject,
            "TextPart": text_content,
        }

        if html_content:
            message["HTMLPart"] = html_content

        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ["MAILJET_API_KEY"],
                os.environ["MAILJET_SECRET_KEY"],
            ),
            json={
                "Messages": [message]
            },
            timeout=30,
        )

        response.raise_for_status()

    def save(self, *args, **kwargs):
        kwargs["email_template_name"] = "registration/password_reset_email.txt"
        kwargs["html_email_template_name"] = "registration/password_reset_email.html"
        return super().save(*args, **kwargs)