from django.core.management.base import BaseCommand
from django.utils import timezone

from management_portal.models import Notice
from student_portal.models import StudentAdmission
from student_portal.notifications import send_student_email


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        now = timezone.now()

        notices = Notice.objects.filter(is_sent=False)

        for notice in notices:

            # ✅ SEND IF:
            # - no scheduled time OR
            # - scheduled time reached
            if not notice.scheduled_time or notice.scheduled_time <= now:

                if notice.students.exists():
                    students = notice.students.all()
                else:
                    student_manager = getattr(
                        StudentAdmission,
                        "original_objects",
                        StudentAdmission._base_manager
                    )
                    students = student_manager.filter(
                        is_active=True,
                        course_completed=False
                    )

                count = 0

                for student in students:
                    if student.email:

                        send_student_email(
                            student=student,
                            subject=notice.title,
                            template="emails/notice.html",
                            context={
                                "student": student,
                                "notice": notice
                            }
                        )

                        count += 1

                # ✅ mark as sent
                notice.is_sent = True
                notice.sent_at = now
                notice.save()

                print(f"✅ Sent: {notice.title} → {count} students")
