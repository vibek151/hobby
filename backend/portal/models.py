from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


# =========================
# DELETE OTP MODEL
# =========================
class DeleteOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300  # 5 minutes

    def __str__(self):
        return f"{self.user.username} - {self.otp}"


# =========================
# COURSE MODEL
# =========================
class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    duration = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================
# BATCH DAY MODEL
# =========================
class BatchDay(models.Model):
    name = models.CharField(max_length=60, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================
# BATCH TIMING MODEL
# =========================
class BatchTiming(models.Model):
    label = models.CharField(max_length=100)

    start_time = models.TimeField()
    start_period = models.CharField(max_length=2, choices=[("AM", "AM"), ("PM", "PM")], default="AM")

    end_time = models.TimeField()
    end_period = models.CharField(max_length=2, choices=[("AM", "AM"), ("PM", "PM")], default="AM")

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.label} ({self.start_time} {self.start_period} - {self.end_time} {self.end_period})"


# =========================
# STUDENT MODEL
# =========================
class Student(models.Model):

    student_name = models.CharField(max_length=200)
    course_completed = models.BooleanField(default=False)

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+?\d{9,15}$',
        message="Phone must be in +999999999 format."
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    # branch = models.ForeignKey("franchise.Branch", on_delete=models.PROTECT)
    batch_days = models.ManyToManyField(BatchDay, blank=True)
    batch_timing = models.ForeignKey(BatchTiming, on_delete=models.SET_NULL, null=True, blank=True)

    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ================= Student ID =================
    student_id = models.CharField(max_length=50, unique=True, editable=False)
    student_id_prefix = models.CharField(max_length=20, default="MG/SLG")
    student_id_number = models.PositiveIntegerField(null=True, editable=False)

    # ================= Certificate =================
    certificate_number = models.CharField(max_length=50, blank=True, null=True)
    marksheet_number = models.CharField(max_length=50, blank=True, null=True)
    certificate_pdf = models.FileField(upload_to="certificates/", blank=True, null=True)
    marksheet_pdf = models.FileField(upload_to="marksheets/", blank=True, null=True)

    # ================= SAVE LOGIC =================
    def save(self, *args, **kwargs):

        # Auto Student ID starting from 171
        if not self.student_id:
            prefix = self.student_id_prefix
            last = Student.objects.filter(student_id_prefix=prefix).order_by('-student_id_number').first()
            self.student_id_number = (last.student_id_number + 1) if last else 171
            self.student_id = f"{prefix}/{self.student_id_number}"

        # Auto course completed when certificate uploaded
        if self.pk:
            old = Student.objects.get(pk=self.pk)
            if not old.certificate_pdf and self.certificate_pdf:
                self.course_completed = True
        else:
            self.course_completed = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"


# =========================
# STUDENT PAYMENT MODEL
# =========================
class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("ONLINE", "Online"),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)

    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.student_name} - ₹{self.amount}"
from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name
