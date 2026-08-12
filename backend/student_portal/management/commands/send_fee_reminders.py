from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from student_portal.models import Fee


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

                send_mail(
                    "Fee Reminder - Smart Computer Institute",
                    f"""
Dear {student.name},

This is a reminder that your course fee payment
is due on {due}.

Please make the payment on time.

Smart Computer Institute
""",
                    "smartcomputerinstitute@gmail.com",
                    [student.email],
                    fail_silently=True,
                )

            # =========================
            # LATE REMINDERS (5 DAYS)
            # =========================
            if due <= today <= due + timedelta(days=5):

                send_mail(
                    "Payment Pending - Smart Computer Institute",
                    f"""
Dear {student.name},

Your course fee payment due on {due}
is still pending.

Please complete your payment as soon as possible.

Smart Computer Institute
""",
                    "smartcomputerinstitute@gmail.com",
                    [student.email],
                    fail_silently=True,
                )

        self.stdout.write(self.style.SUCCESS("Reminder check completed"))