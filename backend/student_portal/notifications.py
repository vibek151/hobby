from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


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


    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[student.email],
        connection=connection
    )

    email.content_subtype = "html"

    if files:
        for file in files:
            email.attach(
                file[0],
                file[1],
                "application/pdf"
            )

    result = email.send(
        fail_silently=False
    )

