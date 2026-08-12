import threading

from django.utils import timezone
from .models import Notice
from student_portal.models import StudentAdmission
from student_portal.notifications import send_student_email


_scheduled_notice_lock = threading.Lock()


def run_scheduled_notices():
    if not _scheduled_notice_lock.acquire(blocking=False):
        return

    try:
        now = timezone.now()

        notices = Notice.objects.filter(
            is_sent=False,
            scheduled_time__isnull=False,
            scheduled_time__lte=now
        )

        for notice in notices:

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

            sent_count = 0

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

                    sent_count += 1

            notice.is_sent = True
            notice.sent_at = now

            notice.save(
                update_fields=[
                    "is_sent",
                    "sent_at"
                ]
            )

            print(
                f"Scheduled notice sent: {notice.title} ({sent_count} students)"
            )

    except Exception as e:
        print("Notice scheduler error:", e)

    finally:
        _scheduled_notice_lock.release()
