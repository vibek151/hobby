from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from student_portal.models import Fee, StudentAdmission

import os
import requests


def send_reminder_email(subject, text_message, html_message, recipient):
    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(
            os.environ["MAILJET_API_KEY"],
            os.environ["MAILJET_SECRET_KEY"],
        ),
        json={
            "Messages": [{
                "From": {
                    "Email": "noreply@smartci.in",
                    "Name": "Smart Computer Institute",
                },
                "To": [{"Email": recipient}],
                "Subject": subject,
                "TextPart": text_message,
                "HTMLPart": html_message,
            }]
        },
        timeout=30,
    )

    print("MAILJET STATUS:", response.status_code)
    print("MAILJET RESPONSE:", response.text)
    response.raise_for_status()


def send_birthday_email(student):
    subject = f"Happy Birthday, {student.name}! 🎂"

    text_message = f"""
Dear {student.name},

Wishing you a very Happy Birthday!

May your special day be filled with happiness, laughter,
and beautiful moments.

May the year ahead bring you success, good health,
and many wonderful memories.

Have a fantastic birthday and a wonderful year ahead!

Warm wishes,
SCI
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="
    margin:0;
    padding:0;
    background:#f6f7f9;
    font-family:Arial, Helvetica, sans-serif;
">

    <div style="
        width:100%;
        padding:35px 10px;
        box-sizing:border-box;
    ">

        <div style="
            max-width:600px;
            margin:0 auto;
            background:#ffffff;
            border-radius:14px;
            overflow:hidden;
            border:1px solid #e9ebef;
        ">

            <!-- Birthday Header -->
            <div style="
                padding:20px;
                text-align:center;
                background:#fffaf7;
            ">
                <img
                    src="https://smartci.in/static/birthday_animation.gif"
                    alt="Happy Birthday"
                    width="560"
                    style="
                        display:block;
                        width:100%;
                        max-width:560px;
                        height:auto;
                        margin:0 auto;
                        border:0;
                    "
                >
            </div>


            <!-- Main Message -->
            <div style="
                padding:35px 30px;
                text-align:center;
            ">

                <p style="
                    margin:0 0 8px;
                    color:#666666;
                    font-size:15px;
                ">
                    Dear
                </p>

                <p style="
                    margin:0 0 25px;
                    color:#222222;
                    font-size:24px;
                    font-weight:700;
                ">
                    {student.name}
                </p>


                <p style="
                    margin:0 auto 22px;
                    max-width:480px;
                    color:#444444;
                    font-size:16px;
                    line-height:1.8;
                ">
                    Wishing you a day filled with
                    <strong>happiness, laughter</strong>
                    and beautiful moments.
                </p>


                <!-- Highlighted Birthday Wish -->
                <div style="
                    max-width:470px;
                    margin:25px auto;
                    padding:22px 18px;
                    background:#fff8f2;
                    border:1px solid #f2dfcf;
                    border-radius:10px;
                    box-sizing:border-box;
                ">

                    <p style="
                        margin:0;
                        color:#444444;
                        font-size:15px;
                        line-height:1.8;
                    ">
                        May the year ahead bring you
                        <strong>success, good health</strong>
                        and many wonderful memories.
                    </p>

                </div>


                <p style="
                    margin:25px 0 0;
                    color:#555555;
                    font-size:15px;
                    line-height:1.8;
                ">
                    Have a fantastic birthday and
                    a wonderful year ahead! 🎉
                </p>

            </div>


            <!-- Small Institutional Signature -->
            <div style="
                padding:18px 20px;
                text-align:center;
                background:#fafafa;
                border-top:1px solid #eeeeee;
            ">

                <p style="
                    margin:0;
                    color:#777777;
                    font-size:13px;
                ">
                    Warm wishes,
                </p>

                <p style="
                    margin:5px 0 0;
                    color:#333333;
                    font-size:14px;
                    font-weight:700;
                    letter-spacing:1px;
                ">
                    SCI
                </p>

            </div>

        </div>

    </div>

</body>
</html>
"""

    send_reminder_email(
        subject,
        text_message,
        html_message,
        student.email,
    )


class Command(BaseCommand):
    help = "Send fee reminder emails"

    def handle(self, *args, **kwargs):

        today = timezone.now().date()

        fees = Fee.objects.select_related(
            "enrollment__student"
        ).filter(
            fee_type="MONTHLY"
        )

        for fee in fees:

            student = fee.enrollment.student

            if not student.email:
                continue

            due = fee.due_date

            # =========================
            # 2 DAYS BEFORE REMINDER
            # =========================

            if due == today + timedelta(days=2):

                send_reminder_email(
                    "Fee Reminder - Smart Computer Institute",

                    f"""Dear {student.name},

                This is a reminder that your course fee payment is due on {due}.

                Please make the payment at Smart Computer Institute on or before the due date.

                Smart Computer Institute
                """,

                    f"""
                <div style="margin:0;padding:30px 15px;background:#f4f7fb;font-family:Arial,sans-serif;">
                    <div style="max-width:600px;margin:auto;background:#ffffff;border-radius:12px;overflow:hidden;">

                        <div style="background:#1f5fbf;padding:24px;text-align:center;color:#ffffff;">
                            <div style="font-size:22px;font-weight:bold;">
                                SMART COMPUTER INSTITUTE
                            </div>
                            
                        </div>

                        <div style="padding:30px;">
                            <h2 style="margin:0 0 18px;color:#222;">
                                Fee Payment Reminder
                            </h2>

                            <p style="color:#444;font-size:15px;line-height:1.7;">
                                Dear <strong>{student.name}</strong>,
                            </p>

                            <p style="color:#555;font-size:15px;line-height:1.7;">
                                This is a friendly reminder that your course fee
                                payment is due on:
                            </p>

                            <div style="margin:24px 0;padding:18px;background:#f1f6ff;
                                        border:1px solid #d6e5ff;border-radius:8px;text-align:center;">
                                <div style="font-size:12px;color:#666;text-transform:uppercase;">
                                    Due Date
                                </div>

                                <div style="margin-top:7px;font-size:22px;
                                            font-weight:bold;color:#1f5fbf;">
                                    {due}
                                </div>
                            </div>

                            <p style="color:#555;font-size:15px;line-height:1.7;">
                                Please make the payment at
                                <strong>Smart Computer Institute</strong>
                                on or before the due date.
                            </p>

                            <p style="margin-top:25px;color:#555;font-size:14px;">
                                Thank you for your cooperation.
                            </p>
                        </div>

                        <div style="background:#f7f8fa;border-top:1px solid #eee;
                                    padding:18px;text-align:center;">
                            <div style="font-weight:bold;color:#333;font-size:14px;">
                                Smart Computer Institute
                            </div>
                            <div style="margin-top:5px;color:#888;font-size:12px;">
                                This is an automated fee reminder.
                            </div>
                        </div>

                    </div>
                </div>
                """,

                    student.email,
                )

            # =========================
            # LATE REMINDERS (5 DAYS)
            # =========================

            if due <= today <= due + timedelta(days=5):

                send_reminder_email(
                    "Payment Pending - Smart Computer Institute",

                    f"""Dear {student.name},

                Your course fee payment due on {due} is still pending.

                Please complete the payment at Smart Computer Institute at your earliest convenience.

                Smart Computer Institute
                """,

                    f"""
                <div style="margin:0;padding:30px 15px;background:#f4f7fb;font-family:Arial,sans-serif;">
                    <div style="max-width:600px;margin:auto;background:#ffffff;border-radius:12px;overflow:hidden;">

                        <div style="background:#c62828;padding:24px;text-align:center;color:#ffffff;">
                            <div style="font-size:22px;font-weight:bold;">
                                SMART COMPUTER INSTITUTE
                            </div>
                            
                        </div>

                        <div style="padding:30px;">
                            <h2 style="margin:0 0 18px;color:#222;">
                                Payment Pending
                            </h2>

                            <p style="color:#444;font-size:15px;line-height:1.7;">
                                Dear <strong>{student.name}</strong>,
                            </p>

                            <p style="color:#555;font-size:15px;line-height:1.7;">
                                Your course fee payment due on
                                <strong>{due}</strong>
                                is still pending.
                            </p>

                            <div style="margin:24px 0;padding:18px;background:#fff5f5;
                                        border:1px solid #f0caca;border-radius:8px;text-align:center;">
                                <div style="font-size:12px;color:#777;text-transform:uppercase;">
                                    Payment Due Date
                                </div>

                                <div style="margin-top:7px;font-size:22px;
                                            font-weight:bold;color:#c62828;">
                                    {due}
                                </div>
                            </div>

                            <p style="color:#555;font-size:15px;line-height:1.7;">
                                Please visit
                                <strong>Smart Computer Institute</strong>
                                and complete your fee payment at your earliest convenience.
                            </p>

                            <p style="margin-top:25px;color:#555;font-size:14px;">
                                Thank you for your cooperation.
                            </p>
                        </div>

                        <div style="background:#f7f8fa;border-top:1px solid #eee;
                                    padding:18px;text-align:center;">
                            <div style="font-weight:bold;color:#333;font-size:14px;">
                                Smart Computer Institute
                            </div>
                            <div style="margin-top:5px;color:#888;font-size:12px;">
                                This is an automated fee reminder.
                            </div>
                        </div>

                    </div>
                </div>
                """,

                    student.email,
                )

        # =========================
        # BIRTHDAY REMINDERS
        # =========================

        students = StudentAdmission._base_manager.all()

        for student in students:

            if not student.email:
                continue

            if not student.dob:
                continue

            if (
                student.dob.month == today.month
                and student.dob.day == today.day
            ):
                send_birthday_email(student)


        self.stdout.write(
            self.style.SUCCESS("Reminder check completed")
        )