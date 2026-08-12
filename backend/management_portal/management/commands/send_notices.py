from django.core.management.base import BaseCommand
from student_portal.models import StudentAdmission
from student_portal.notifications import send_student_email


class Command(BaseCommand):
    help = "Send notices to all students"

    def handle(self, *args, **kwargs):

        students = StudentAdmission.objects.all()

        count = 0

        for student in students:
            print("EMAIL:", student.email)

            if student.email:
                send_student_email(
                    student=student,
                    subject="📢 Notice",
                    template="emails/notice.html",
                    context={
                        "student": student,
                        "notice": {
                            "title": "Test Notice",
                            "body": "This is a test"
                        }
                    }
                )

                print("SENT TO:", student.email)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Sent to {count} students"))