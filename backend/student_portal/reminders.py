from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from .models import Fee, AutomationLog
from django.db.models import Sum


def run_fee_reminders():

    today = timezone.now().date()

    log, created = AutomationLog.objects.get_or_create(id=1)

    if log.last_run == today:
        return

    fees = Fee._base_manager.select_related(
        "enrollment__student",
        "enrollment__course"
    ).filter(
        fee_type="MONTHLY"
    )

    processed_enrollments = set()

    for fee in fees:

        enrollment = fee.enrollment
        student = enrollment.student

        # prevent duplicate reminder
        if enrollment.id in processed_enrollments:
            continue

        processed_enrollments.add(
            enrollment.id
        )

        # Skip long leave
        if (
            student.leave_start and
            student.leave_until
        ):

            leave_days = (
                student.leave_until -
                student.leave_start
            ).days + 1

            if (
                leave_days >= 20 and
                student.leave_start <= today <= student.leave_until
            ):
                continue

        if not student.email:
            continue

        due = fee.due_date

        if not due:
            continue

        total_paid = Fee._base_manager.filter(
            enrollment=enrollment,
            fee_type="MONTHLY"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        if total_paid >= enrollment.monthly_fee:
            continue

        days_left = (
            due - today
        ).days

        last_fine = Fee._base_manager.filter(
            enrollment=enrollment,
            fee_type="MONTHLY",
            payment_date__lt=due
        ).order_by(
            "-payment_date"
        ).values_list(
            "fine",
            flat=True
        ).first() or 0

        monthly_fee = enrollment.monthly_fee
        total_payable = monthly_fee + last_fine

        last_payment_date = due + timedelta(days=5)

        due_date_text = due.strftime("%d %B %Y")
        last_date_text = last_payment_date.strftime("%d %B %Y")

        student_code = student.student_id
        course_code = enrollment.course.code

        # ---------------- REMINDER EMAIL ----------------

        message = f"""
<!DOCTYPE html>
<html>

<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">

<div style="max-width:600px;margin:30px auto;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">

<div style="background:#244b6b;padding:18px;text-align:center;color:white;">
<h2 style="margin:0;">Smart Computer Institute</h2>

<p style="margin-top:5px;font-size:13px;">
Monthly Fee Reminder
</p>
</div>


<div style="padding:25px;color:#333;line-height:1.8;">

<p>Hello <b>{student.name}</b>,</p>

<p>
This is a friendly reminder regarding your upcoming monthly fee payment.
</p>

<div style="background:#f8fafc;border-left:4px solid #244b6b;padding:15px;border-radius:8px;">

<b>Student ID:</b> {student_code}<br>
<b>Course Code:</b> {course_code}<br><br>

<b>Monthly Fee:</b> ₹{monthly_fee}<br>
<b>Previous Fine:</b> ₹{last_fine}<br>
<b>Total Payable:</b> ₹{total_payable}<br><br>

<b>Due Date:</b> {due_date_text}<br>
<b>Days Remaining:</b> {days_left}

</div>

<div style="margin-top:20px;padding:14px;background:#fff8e6;border-radius:8px;border:1px solid #ffe08a;">

⚠ Please complete payment before
<b>{last_date_text}</b>
to avoid late fine charges.

</div>

<p style="margin-top:25px;">
Payment can be made at the institute office.
</p>

<hr>

<div style="font-size:13px;color:#777;text-align:center;">
Thank you<br>
Smart Computer Institute
</div>

</div>
</div>
</body>
</html>
"""

        # reminder 4 days before due
        if 0 <= days_left <= 4:

            email = EmailMultiAlternatives(
                f"Fee Reminder - {student_code}",
                "",
                "settings.DEFAULT_FROM_EMAIL",
                [student.email]
            )

            email.attach_alternative(
                message,
                "text/html"
            )

            email.send()

        # ------------ LATE FINE EMAIL ------------

        elif days_left < 0:

            late_days = abs(days_left)

            fine = late_days * 5

            fine_message = f"""
        <!DOCTYPE html>
        <html>

        <body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">

        <div style="max-width:600px;margin:30px auto;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">

        <div style="background:#8b1e1e;padding:18px;text-align:center;color:white;">
        <h2 style="margin:0;">Smart Computer Institute</h2>

        <p style="margin-top:5px;font-size:13px;">
        Late Fee Notice
        </p>
        </div>


        <div style="padding:25px;color:#333;line-height:1.8;">

        <p>Hello <b>{student.name}</b>,</p>

        <p>
        Your payment due date has passed.
        Please complete payment immediately.
        </p>

        <div style="background:#fff5f5;border-left:4px solid #8b1e1e;padding:15px;border-radius:8px;">

        <b>Student ID:</b> {student_code}<br>
        <b>Course Code:</b> {course_code}<br><br>

        <b>Monthly Fee:</b> ₹{monthly_fee}<br>
        <b>Current Fine:</b> ₹{fine}<br><br>

        <b>Fine Rule:</b> ₹5/day<br>
        <b>Late Days:</b> {late_days}

        </div>

        <div style="margin-top:20px;padding:14px;background:#fff0f0;border-radius:8px;border:1px solid #ffbdbd;">

        ⚠ Fine has started and increases by
        <b>₹5 every day</b>
        until payment is completed.

        </div>

        <p style="margin-top:25px;">
        Please visit the institute office and complete payment.
        </p>

        <hr>

        <div style="font-size:13px;color:#777;text-align:center;">
        Thank you<br>
        Smart Computer Institute
        </div>

        </div>
        </div>
        </body>
        </html>
        """

            email = EmailMultiAlternatives(
                f"Late Fee Notice - {student_code}",
                "",
                "settings.DEFAULT_FROM_EMAIL",
                [student.email]
            )

            email.attach_alternative(
                fine_message,
                "text/html"
            )

            email.send()

    log.last_run = today
    log.save()