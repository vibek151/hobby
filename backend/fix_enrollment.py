import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "institute.settings")
django.setup()

from student_portal.models import CourseEnrollment, Fee

fees = Fee.objects.filter(enrollment__isnull=True)

print("Fixing", fees.count(), "fees...")

for fee in fees:
    student = fee.student

    enrollment, created = CourseEnrollment.objects.get_or_create(
        student=student,
        defaults={
            "course_name": student.course,
            "admission_date": student.admission_date,
            "total_fee": student.final_amount,
            "monthly_fee": student.monthly_fee,
            "duration": student.course_duration,
            "admission_fee": student.admission_amount,
            "is_active": True,
        }
    )

    fee.enrollment = enrollment
    fee.save()

print("Done.")