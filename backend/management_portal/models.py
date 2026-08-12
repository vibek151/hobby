from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from franchise.models import Franchise
from student_portal.models import Course
# NO "from .models import ..." here!

class StudentAdmission(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    course_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class Notice(models.Model):
    title = models.CharField(max_length=200)
    franchise = models.ForeignKey(
        Franchise,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    body = models.TextField()

    students = models.ManyToManyField(
        'StudentAdmission',
        blank=True,
        related_name='notices'
    )

    sender_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Smart Computer Institute"
    )

    scheduled_time = models.DateTimeField(
        null=True,
        blank=True
    )

    is_sent = models.BooleanField(
        default=False
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    progress = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = "Notice"  
        verbose_name_plural = "Notices"

    def __str__(self):
        return self.title

    @property
    def total_students_count(self):

        if self.students.exists():
            return self.students.count()

        return StudentAdmission.objects.filter(
            is_active=True,
            course_completed=False
        ).count()

    def clean(self):

        if not self.title.strip():
            raise ValidationError(
                "Title cannot be empty"
            )

        if not self.body.strip():
            raise ValidationError(
                "Body cannot be empty"
            )

        # block past date/time
        if self.scheduled_time and not self.is_sent:

            if self.scheduled_time < timezone.now():

                raise ValidationError({
                    "scheduled_time":
                    "Past date/time not allowed."
                })

    def save(
        self,
        *args,
        **kwargs
    ):

        self.full_clean()

        super().save(
            *args,
            **kwargs
        )

class NoticeHidden(models.Model):

    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE
    )

    franchise_user = models.CharField(
        max_length=100
    )


class Exam(models.Model):

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    exam_name = models.CharField(
        max_length=100
    )

    total_marks = models.IntegerField(
        default=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.course} - {self.exam_name}"
    

class StudentMarks(models.Model):

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    student = models.ForeignKey(
        "student_portal.StudentAdmission",
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    marks = models.IntegerField(
        verbose_name="Marks Obtained"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "student",
            "exam"
        )
        verbose_name = "Student mark"
        verbose_name_plural = "Student marks"


    def __str__(self):

        return (
            f"{self.student} - "
            f"{self.exam} - "
            f"{self.marks}"
        )
    
    def clean(self):

        if (
            self.exam and
            self.marks > self.exam.total_marks
        ):

            raise ValidationError({
                "marks":
                f"Marks obtained cannot be greater than total marks ({self.exam.total_marks})"
            })


    def save(
        self,
        *args,
        **kwargs
    ):

        self.full_clean()

        super().save(
            *args,
            **kwargs
        )



from website_portal.models import WebsiteCourse


class Lead(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("CONTACTED", "Contacted"),
        ("FOLLOW_UP", "Follow Up"),
        ("ADMITTED", "Admitted"),
        ("REJECTED", "Rejected"),
    ]

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    course = models.ForeignKey(
        WebsiteCourse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    qualification = models.CharField(max_length=100, blank=True)

    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"