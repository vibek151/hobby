from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction
from simple_history.models import HistoricalRecords
import calendar
from core.middleware import get_current_franchise
# from management_portal.models import Exam, StudentMarks
from django.apps import apps
# ================= COURSE =================

# Add this line below to fix the NameError:
from core.models import MultiTenantModel


class Course(MultiTenantModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    monthly_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        editable=False
    )
    
    duration = models.IntegerField(help_text="Duration in months")
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)
    # exams = models.ManyToManyField(
    #     "management_portal.Exam",
    #     blank=True,
    #     related_name="courses",
    # )
    history = HistoricalRecords()
    def save(self, *args, **kwargs):
        if self.duration and self.duration > 0:
            self.monthly_fee = Decimal(self.total_fees) / Decimal(self.duration)
        super().save(*args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form


    def __str__(self):
        # return f"{self.code} - {self.name}"
        return self.code


# ================= BATCH INFO =================
from django.contrib.auth.models import User

class BatchDay(MultiTenantModel):
    day = models.CharField(max_length=50)
    history = HistoricalRecords()
    def __str__(self):
        return self.day

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form

    class Meta:
        verbose_name = "Class day"
        verbose_name_plural = "Class days"

class BatchTiming(MultiTenantModel):
    time = models.CharField(max_length=50)
    history = HistoricalRecords()
    def __str__(self): return self.time

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form


    class Meta:
        verbose_name = "Class timing"
        verbose_name_plural = "Class timings"


# ================= STUDENT ADMISSION =================



def validate_passport_photo_size(value):
    if value and value.size > 200 * 1024:  # 200 KB
        raise ValidationError(
            "Passport photo must be 200 KB or smaller."
        )



class StudentAdmission(MultiTenantModel):

    # 
    @property
    def payment_progress(self):
        enrollment = CourseEnrollment.objects.filter(
            student=self,
            is_active=True
        ).first()

        if not enrollment:
            return 0

        total_paid = Fee.objects.filter(
            enrollment=enrollment,
            fee_type="MONTHLY"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_required = enrollment.monthly_fee * enrollment.duration

        return round((total_paid / total_required) * 100, 2) if total_required else 0
    

    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    course_completed = models.BooleanField(default=False)

    # Personal Details
    name = models.CharField(max_length=100)

    # 2. Receipt Validation
    
    @property
    def is_course_completed(self):

        # 1️⃣ Certificate must exist for CURRENT course
        cert = self.certificate_set.filter(
            completed_course=self.course
        ).first()

        if not cert or not cert.is_published:
            return False

        # 2️⃣ Get active enrollment for current course
        enrollment = self.enrollments.filter(
            course=self.course,
            is_active=True
        ).first()

        if not enrollment:
            return False

        # 3️⃣ Calculate total monthly paid
        total_paid = (
            enrollment.payments
            .filter(fee_type="MONTHLY")
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        # 4️⃣ Compare with total course fee
        if total_paid >= enrollment.total_fee:
            return True

        return False
    
    passport_photo = models.ImageField(
        upload_to="passport_photos/",
        null=True,
        validators=[validate_passport_photo_size]
    )
    guardian_name = models.CharField(max_length=100, null=True)
    dob = models.DateField(null=True)
    phone = models.CharField(max_length=10)
    email = models.EmailField(
        max_length=254,
        null=True,
        blank=True,
        help_text="Student email for payment reminders"
    )
    qualification = models.CharField(max_length=100, null=True)

    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    last_qualification_file = models.FileField(upload_to="last_qualification/", null=True)

    DOCUMENT_TYPE = [("AADHAAR", "Aadhaar"), ("OTHER", "Other")]
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE, blank=True, null=True)
    document_number = models.CharField(max_length=30, null=True)
    document_file = models.FileField(upload_to="documents/", null=True)
    address = models.TextField(null=True)

    # Course Details
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    TYPE_CHOICES = [("TYPE 1", "Type 1"), ("TYPE 2", "Type 2")]
    course_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="TYPE 1")
    course_duration = models.IntegerField(null=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class_day = models.ManyToManyField(BatchDay)
    class_time = models.ForeignKey(BatchTiming, on_delete=models.SET_NULL, null=True)

    # Payment Info
    admission_date = models.DateField(null=True)
    leave_start = models.DateField(null=True, blank=True)
    leave_until = models.DateField(null=True, blank=True)
    receipt_no = models.CharField(max_length=50, null=True)
    PAY_METHODS = [("CASH", "Cash"), ("ONLINE", "Online"), ("CARD", "Card")]
    admission_pay_via = models.CharField(max_length=10, choices=PAY_METHODS, default="CASH", blank=True, null=True)
    admission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_suspended = models.BooleanField(default=False)
    # suspension_reason = models.CharField(max_length=255, blank=True, null=True)
    is_freezed = models.BooleanField(default=False)
    history = HistoricalRecords()

    def clean(self):
        if self.receipt_no:
            fee_qs = Fee.objects.filter(receipt_no=self.receipt_no)

            if self.pk:
                fee_qs = fee_qs.exclude(enrollment__student=self)

            if fee_qs.exists():
                raise ValidationError({
                    "receipt_no": "This receipt number is already used."
                })
            
        if self.pk:

            old = StudentAdmission.objects.only(
                "course_id"
            ).get(
                pk=self.pk
            )

            if old.course_id != self.course_id:

                active_enrollment = (
                    CourseEnrollment.objects.filter(
                        student=self,
                        is_active=True
                    ).exists()
                )

                if active_enrollment:

                    raise ValidationError({
                        "course":
                        "You cannot change the course directly. Please use Course Upgrade."
                    })



    def save(self, *args, **kwargs):
        skip_enrollment_sync = kwargs.pop("_skip_enrollment_sync", False)
        from core.middleware import get_current_franchise

        if not self.franchise_id:
            franchise = get_current_franchise()

            if not franchise:
                raise ValidationError({
                    "franchise": "Franchise not found. Please login again."
                })

            self.franchise = franchise
        from_upgrade = kwargs.pop("from_upgrade", False)

        # block direct course change
 

        # 1. Student ID Logic
        # Student ID Logic
        if not self.student_id:

            franchise = self.franchise

            prefix1 = (
                franchise.student_id_part1
                or "MG"
            )

            prefix2 = (
                franchise.student_id_part2
                or "SLG"
            )

            BASE = int(
                franchise.student_id_part3 or 1
            )

            last = StudentAdmission.objects.filter(
                franchise=franchise
            ).exclude(
                student_id__isnull=True
            ).order_by("-id").first()

            if last and last.student_id:

                try:

                    last_num = int(
                        last.student_id
                        .split("/")[-1]
                    )

                    next_num = max(
                        last_num + 1,
                        BASE
                    )

                except:

                    next_num = BASE

            else:

                next_num = BASE

            self.student_id = (
                f"{prefix1}/"
                f"{prefix2}/"
                f"{str(next_num).zfill(4)}"
            )

        

        # 3. Course Logic
        if self.course:
            base_duration = self.course.duration or 0
            base_monthly = self.course.monthly_fee or 0

            if self.course_type == "TYPE 2":
                # Half duration, double monthly (same total fee)
                self.course_duration = base_duration // 2
                self.monthly_fee = base_monthly * 2
            else:
                self.course_duration = base_duration
                self.monthly_fee = base_monthly

            

        # 4. Calculation Logic
        adm_amt = Decimal(self.admission_amount or 0)
        disc = Decimal(self.discount_percent or 0)
        adv = Decimal(self.advance_fees or 0)
        discount_value = (adm_amt * disc) / Decimal(100)
        self.final_amount = adm_amt - discount_value + adv

        # ✅ THIS IS THE FIX
        super().save(*args, **kwargs)
        # 🔁 Sync active enrollment with updated course settings
        if not skip_enrollment_sync:

            active_enrollment = CourseEnrollment.objects.filter(
                student=self,
                is_active=True
            ).first()

            if active_enrollment:
                active_enrollment.monthly_fee = self.monthly_fee
                active_enrollment.duration = self.course_duration

                # 🔥 sync admission date too
                active_enrollment.admission_date = self.admission_date

                active_enrollment.save(
                    update_fields=[
                        "monthly_fee",
                        "duration",
                        "admission_date"
                    ]
                )

        # 6. FIX FOR IntegrityError: Use update_or_create
        # Your crash happened because get_or_create tried to INSERT a duplicate.
        # update_or_create will UPDATE the existing fee instead.
        if (
            not skip_enrollment_sync
            and not from_upgrade
            and not getattr(self, "_rollback_mode", False)
            and self.course
        ):
            enrollment = CourseEnrollment.objects.filter(
                student=self,   # IMPORTANT: use student correctly
                course=self.course
            ).first()

            if not enrollment:
                enrollment = CourseEnrollment.objects.create(
                    student=self,
                    course=self.course,
                    franchise=self.franchise,
                    admission_date=self.admission_date or timezone.now().date(),
                    total_fee=self.course.total_fees,
                    monthly_fee=self.monthly_fee,
                    duration=self.course_duration,
                    admission_fee=self.admission_amount,
                    is_active=True,
                )
            
            if self.admission_amount > 0 and self.receipt_no:

                discounted_admission = (
                Decimal(self.admission_amount or 0)
                - (
                    Decimal(self.admission_amount or 0)
                    * Decimal(self.discount_percent or 0)
                    / Decimal(100)
                )
            ).quantize(Decimal("0.01"))

            admission_fee = Fee.objects.filter(
                enrollment=enrollment,
                receipt_no=self.receipt_no,
                fee_type="ADMISSION",
            ).first()

            if admission_fee:
                admission_fee.amount = discounted_admission
                admission_fee.generated_fee = discounted_admission
                admission_fee.pay_via = self.admission_pay_via or "CASH"
                admission_fee.payment_date = (
                    self.admission_date or timezone.now().date()
                )
                admission_fee.franchise = self.franchise

                admission_fee.save(
                    _allow_admission_update=True
                )

            else:
                Fee.objects.create(
                    enrollment=enrollment,
                    receipt_no=self.receipt_no,
                    fee_type="ADMISSION",
                    amount=discounted_admission,
                    generated_fee=discounted_admission,
                    pay_via=self.admission_pay_via or "CASH",
                    payment_date=self.admission_date or timezone.now().date(),
                    franchise=self.franchise,
                )

            # =========================
            # COURSE ADVANCE PAYMENT
            # =========================
            if self.advance_fees and self.advance_fees > 0:

                Fee.objects.update_or_create(
                    receipt_no=self.receipt_no,
                    fee_type="ADVANCE",
                    enrollment=enrollment,
                    defaults={
                        "amount": self.advance_fees,
                        "pay_via": self.admission_pay_via or "CASH",
                        "payment_date": self.admission_date or timezone.now().date(),
                        "franchise": self.franchise,
                        "generated_fee": self.advance_fees,
                        "generated_fine": 0,
                        "fine": 0,
                        "total_amount": self.advance_fees,
                        "remaining_fee": 0,
                        "remaining_fine": 0,
                        "generated_total": self.advance_fees,
                    }
                )


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form
    
    def __str__(self):
        
        return f"{self.student_id} - {self.name}"
    
# ================= ENROLLMENT & FEES =================
class CourseEnrollment(MultiTenantModel):
    student = models.ForeignKey(StudentAdmission, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    admission_date = models.DateField()
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()
    def __str__(self):
        status = "Active" if self.is_active else "Closed"
        return f"{self.student.name} - {self.course.code} - {self.student.student_id} ({status})"
    

  

    def delete(self, *args, **kwargs):

        student = self.student
        previous_course = self.course

        super().delete(*args, **kwargs)

        # 🔥 After deleting upgrade → restore previous course
        last_enrollment = CourseEnrollment.objects.filter(
            student=student
        ).order_by("-id").first()

        if last_enrollment:
            student.course = last_enrollment.course
            student.is_active = True

            # 🔥 Recalculate completion
            total_paid = Fee.objects.filter(
                enrollment=last_enrollment,
                fee_type="MONTHLY"
            ).aggregate(total=Sum("amount"))["total"] or 0

            remaining = last_enrollment.total_fee - total_paid

            student.course_completed = (remaining == 0)

            if StudentAdmission.objects.filter(pk=student.pk).exists():
                student.save(
                    update_fields=["course", "is_active", "course_completed"],
                    _skip_enrollment_sync=True
                )

    
    class Meta:
        unique_together = ('student', 'course')

import calendar
from dateutil.relativedelta import relativedelta
from datetime import date

def get_safe_date(year, month, day):
    """Returns a valid date even if the day exceeds month length."""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))

class Fee(MultiTenantModel):
    PAYMENT_METHOD = [("CASH", "Cash"), ("ONLINE", "Online")]

    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    generated_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    generated_fine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    receipt_no = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="Receipt number must contain only digits (0-9)."
            )
        ]
    )

    pay_via = models.CharField(max_length=10, choices=PAYMENT_METHOD, default="CASH")
    payment_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    FEE_TYPE = [
        ("ADMISSION", "Admission"),
        ("MONTHLY", "Monthly"),
        ("ADVANCE", "Advance"),
    ]

    fee_type = models.CharField(max_length=20, choices=FEE_TYPE, default="MONTHLY")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Hidden carry-forward values
    remaining_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    remaining_fine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    generated_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    waive_fine = models.BooleanField(default=False)
    history = HistoricalRecords()
    # ================= SAVE =================
    
    from dateutil.relativedelta import relativedelta
    from django.utils import timezone
    from django.db import transaction
    # Ensure get_safe_date is either imported or defined in this file
    # from .utils import get_safe_date 

    def save(self, *args, **kwargs):
        allow_admission_update = kwargs.pop(
            "_allow_admission_update",
            False
        )

        self._allow_admission_update = allow_admission_update
        with transaction.atomic():
            # 1. Detect Fee Type
            is_admission = (
                self.fee_type != "ADVANCE"
                and self.enrollment.student.receipt_no
                and self.receipt_no == self.enrollment.student.receipt_no
            )
            if is_admission:
                self.fee_type = "ADMISSION"
                self.generated_fine = 0
                self.due_date = None

            elif self.fee_type == "ADVANCE":
                self.fee_type = "ADVANCE"
                self.generated_fine = 0
                self.due_date = None

            else:
                self.fee_type = "MONTHLY"
                # Crucial: Ensures calc_date is available for new creations
                calc_date = self.payment_date or timezone.now().date()
                admission_date = self.enrollment.admission_date
                admission_day = admission_date.day
                # 2. June is the First Payable Month (Admission May + 1)
                first_payable_month = admission_date + relativedelta(months=1)
                # 3. Monthly Dues (Strict Calendar Count)
                # This ensures June, July, August, and Sept (4 months) are counted
                # =========================================
                # Previous Monthly Payment
                # =========================================
                last_payment = Fee.objects.filter(
                    enrollment=self.enrollment,
                    fee_type="MONTHLY"
                ).exclude(pk=self.pk).order_by("-id").first()
                # =========================================
                # First Monthly Bill
                # =========================================
                if not last_payment:
                    if isinstance(calc_date, datetime):
                        calc_date = calc_date.date()
                    if calc_date < first_payable_month.replace(day=1):
                        pending_months = 0
                    else:
                        months_diff = (
                            (calc_date.year - first_payable_month.year) * 12
                            + (calc_date.month - first_payable_month.month)
                        )
                        pending_months = months_diff + 1

                    generated = (
                        (self.enrollment.monthly_fee or 0)
                        * max(0, pending_months)
                    )

                    self.generated_fee = min(
                        generated,
                        self.enrollment.total_fee
                    )
                # =========================================
                # Future Bills
                # =========================================
                # =========================================
                # Future Bills
                # =========================================
                # =========================================
                # Future Bills Correction
                # =========================================
                else:
                    # Calculate months difference between current entry date and last payment
                    months_diff = (
                        (calc_date.year - last_payment.payment_date.year) * 12
                        + (calc_date.month - last_payment.payment_date.month)
                    )

                    old_due = last_payment.remaining_fee or 0

                    # Total amount paid across previous history 
                    paid_total = (
                        Fee.objects.filter(
                            enrollment=self.enrollment,
                            fee_type="MONTHLY"
                        )
                        .exclude(pk=self.pk)
                        .aggregate(total=models.Sum("amount"))["total"]
                        or 0
                    )

                    remaining_course_fee = max(
                        0,
                        self.enrollment.total_fee - paid_total
                    )

                    # FIX: If it is a new month, allow generating a new monthly fee 
                    # even if an old debt exists, bounded by what's left of the total course fee
                    if months_diff > 0:
                        self.generated_fee = min(
                            self.enrollment.monthly_fee * months_diff,
                            remaining_course_fee - old_due
                        )
                    else:
                        self.generated_fee = 0
                # 4. Set Display Due Date (Current month's reference)
                # 4. Set Display Due Date

                if last_payment:

                    months_since_admission = (
                        (last_payment.payment_date.year - admission_date.year) * 12
                        + (last_payment.payment_date.month - admission_date.month)
                        + 1
                    )

                else:

                    months_since_admission = max(
                        1,
                        pending_months
                    )


                cycle_month = admission_date + relativedelta(
                    months=months_since_admission
                )

                cycle_anchor = get_safe_date(
                    cycle_month.year,
                    cycle_month.month,
                    admission_day
                )

                # try +5
                tentative_due = cycle_anchor + timedelta(days=5)

                # IMPORTANT:
                # use cycle_month month, not tentative month

                last_day = calendar.monthrange(
                    cycle_month.year,
                    cycle_month.month
                )[1]

                month_end = cycle_month.replace(
                    day=last_day
                )

                self.due_date = min(
                    tentative_due,
                    month_end
                )
                if self.waive_fine:
                    self.generated_fine = 0
                else:
                    first_payable_month = admission_date + relativedelta(months=1)
                    first_cycle_anchor = get_safe_date(first_payable_month.year, first_payable_month.month, admission_day)
                    # Grace period ends 7/6/2026, fine starts 8/6/2026
                    fine_start_date = (
                        first_cycle_anchor
                        + relativedelta(days=1)
                    ) 
                   # =========================================
                    # Fine Logic Rebuild
                    # =========================================

                    old_fee_due = (
                        last_payment.remaining_fee or 0
                    ) if last_payment else 0

                    old_fine_due = (
                        last_payment.remaining_fine or 0
                    ) if last_payment else 0

                    self.generated_fine = 0
                    from student_portal.fee_engine import calculate_student_dues

                    dues = calculate_student_dues(
                        self.enrollment,
                        calc_date
                    )

                    self.generated_fine = dues["fine"]
            # =========================================
            # Previous Remaining Balances
            # =========================================
            previous_due = Fee.objects.filter(
                enrollment=self.enrollment,
                fee_type="MONTHLY"
            ).exclude(
                pk=self.pk
            ).order_by("-id").first()

            if previous_due and (
                previous_due.remaining_fee == 0 and
                previous_due.remaining_fine == 0
                and previous_due.generated_fine == 0
            ):
                previous_due = None
            previous_fee_due = 0
            previous_fine_due = 0
            if previous_due:
                previous_fee_due = previous_due.remaining_fee or 0
                previous_fine_due = previous_due.remaining_fine or 0
            # =========================================
            # Current Bill Validation Guard
            # =========================================
            current_fee_total = (
                self.generated_fee or 0
            ) + previous_fee_due

            print(
                "generated_fine =", self.generated_fine,
                "| previous_fine_due =", previous_fine_due,
                "| current_fine_total =", (self.generated_fine or 0) + previous_fine_due
            )

            
            current_fine_total = (
                self.generated_fine or 0
            ) + previous_fine_due

            # =========================================
            # Grand Total
            # =========================================
            self.generated_total = current_fee_total + current_fine_total
            self.total_amount = (
                (self.amount or 0)
                + (self.fine or 0)
            )
            # =========================================
            # Separate Settlement
            # Fee + Fee
            # Fine + Fine
            # =========================================
            received_fee = self.amount or 0
            received_fine = self.fine or 0
            self.remaining_fee = max(
                0,
                current_fee_total - received_fee
            )
            print(
                "generated_fine:", self.generated_fine,
                "| previous_fine_due:", previous_fine_due,
                "| current_fine_total:", current_fine_total,
                "| received_fine:", received_fine
            )
            self.remaining_fine = max(
                0,
                current_fine_total - received_fine
            )
            # =========================================
            # Validation
            # =========================================

            try:
                self.full_clean()
            except ValidationError as e:
                raise ValidationError(e.message_dict)

            super().save(
                *args,
                **kwargs
            )
       


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form


    # ================= CLEAN =================
    def clean(self):

        super().clean()

        old = None

        if self.pk:
            old = Fee.objects.filter(
                pk=self.pk
            ).first()

        # ==========================
        # Block payment on inactive enrollment
        # ==========================

        if not self.pk and not self.enrollment.is_active:

            raise ValidationError(
                "This course has been upgraded. Payments are not allowed."
            )

        # ==========================
        # Admission fee lock
        # ==========================

        if (
            old
            and old.fee_type == "ADMISSION"
            and old.amount != self.amount
            and not getattr(
                self,
                "_allow_admission_update",
                False
            )
        ):
            raise ValidationError(
                "Admission fee cannot be modified."
            )

        # ==========================
        # Old course lock
        # ==========================

        if (
            old
            and self.enrollment.student.course
            != self.enrollment.course
        ):

            raise ValidationError(
                "Cannot modify payment. Course is locked."
            )

        # ==========================
        # Prevent empty monthly payment
        # ==========================

        if (

            self.fee_type == "MONTHLY"

            and (self.amount or 0) <= 0

            and (self.fine or 0) <= 0

            and not self.waive_fine

        ):

            raise ValidationError({

                "__all__":
                "Monthly payment cannot be saved with both Amount and Fine as 0"

            })

        # ==========================
        # Course total fee limit
        # ==========================

        if (
            self.fee_type == "MONTHLY"
            and (self.amount or 0) > 0
        ):

            paid_total = (
                Fee.objects.filter(
                    enrollment=self.enrollment,
                    fee_type__in=["MONTHLY", "ADVANCE"]
                )
                .exclude(pk=self.pk)
                .aggregate(
                    total=models.Sum("amount")
                )["total"]
                or 0
            )

            remaining_course_fee = max(
                0,
                float(self.enrollment.total_fee)
                - float(paid_total)
            )

            if float(self.amount) > remaining_course_fee:

                raise ValidationError({
                    "amount":
                    f"You can pay maximum ₹{remaining_course_fee:.2f}"
                })

        # ==========================
        # Fine validation
        # ==========================

        from student_portal.fee_engine import (
            calculate_student_dues
        )

        calc_date = (
            self.payment_date
            or timezone.now().date()
        )

        data = calculate_student_dues(
            self.enrollment,
            calc_date
        )

        current_fine_total = (
            data["fine"] or 0
        )

        entered_fine = Decimal(
            str(self.fine or 0)
        )

        if entered_fine > Decimal(
            str(current_fine_total)
        ):

            raise ValidationError({

                "fine":
                f"Fine payment exceeds current due ₹{current_fine_total}"

            })

    # ================= DELETE =================
    def delete(self, *args, **kwargs):

        bypass_lock = kwargs.pop("bypass_lock", False)

        enrollment = self.enrollment
        student = enrollment.student

        # 🔒 Block only manual delete
        if not bypass_lock:

            if student.course != enrollment.course:

                cert_exists = Certificate.objects.filter(
                    student=student,
                    completed_course=enrollment.course
                ).exists()

                if cert_exists:
                    raise ValidationError(
                        "Cannot delete payment. This course is already completed and locked."
                    )

        # =========================
        # Reset carry-forward
        # =========================

        super().delete(*args, **kwargs)

    # ================= META =================
    class Meta:
        indexes = [
            models.Index(fields=["enrollment"]),
            models.Index(fields=["receipt_no"]),
        ]

    # ================= STRING =================
    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.enrollment.student.name} - {self.receipt_no}"



# ================= CERTIFICATES =================
from django.db import models
from django.core.exceptions import ValidationError


# 1. Define the validator at the top of the file
def validate_file_size(value):
    # 2MB = 2 * 1024 * 1024 bytes
    limit = 2097152
    if value and hasattr(value, 'size') and value.size > limit:
        raise ValidationError(f"File too large. Size should not exceed 2MB.")
    return value

class Certificate(MultiTenantModel):
    student = models.ForeignKey(
        StudentAdmission,
        on_delete=models.CASCADE,
    )
    is_published = models.BooleanField(default=False)
    completed_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    end_date = models.DateField(
        null=True,
        blank=True
    )


    certificate_no = models.CharField(max_length=50)
    certificate_prefix = models.CharField(max_length=20, default="SCI/2026/")
    
    # 2. Apply the validator directly here
    certificate_file = models.FileField(
        upload_to="certificates/",
        validators=[validate_file_size]
    )
    
    marksheet_no = models.CharField(max_length=50, blank=True, null=True)
    
    # 3. Apply the validator here as well
    marksheet_file = models.FileField(
        upload_to="marksheets/", 
        blank=True, 
        null=True,
        validators=[validate_file_size]
    )
    
    upload_date = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    # ... rest of your methods (clean, save, delete) ...



    
    
    # ... rest of your model fields ...
    # 🔥 NEW FIELD (Frontend Visibility Control)
    # is_published = models.BooleanField(
    #     default=False,
    #     help_text="If unchecked, certificate will be stored but not visible on frontend."
    # )

    
    

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form

    def delete(self, *args, **kwargs):

        bypass_lock = kwargs.pop("bypass_lock", False)

        student = self.student
        completed_course = self.completed_course

        # 🔒 HARD LOCK only for manual delete
        if not bypass_lock:

            if student.course != completed_course:
                raise ValidationError(
                    "Cannot delete certificate. Student has already upgraded to another course."
                )

        # ✅ delete first
        super().delete(*args, **kwargs)

        # 🔥 recalculate safely
        enrollment = CourseEnrollment.objects.filter(
            student=student,
            course=completed_course
        ).first()

        if enrollment:

            total_paid = Fee.objects.filter(
                enrollment=enrollment,
                fee_type="MONTHLY"
            ).aggregate(total=Sum("amount"))["total"] or 0

            remaining = enrollment.total_fee - total_paid

            student.course_completed = (remaining == 0)

            if StudentAdmission.objects.filter(pk=student.pk).exists():
                student.save(update_fields=["course_completed"])

    def check_exam_completion(self):

        Exam = apps.get_model("management_portal", "Exam")
        StudentMarks = apps.get_model("management_portal", "StudentMarks")

        total_exams = Exam.objects.filter(
            course=self.completed_course
        ).count()

        completed_exams = StudentMarks.objects.filter(
            student=self.student,
            exam__course=self.completed_course
        ).count()

        return completed_exams == total_exams



    def clean(self):
        super().clean()
        
        Exam = apps.get_model("management_portal", "Exam")
        StudentMarks = apps.get_model("management_portal", "StudentMarks")
        if not self.completed_course:
            raise ValidationError("Please select a course.")
        # End date is required
        if not self.end_date:
            raise ValidationError(
                "Please select the course end date."
            )

        # End date cannot be before admission/upgrade date
        if self.end_date < self.student.admission_date:
            raise ValidationError(
                "End date cannot be earlier than the admission/upgrade date."
            )
        # 🔒 STRICT RULE
        if self.completed_course != self.student.course:
            raise ValidationError(
                f"Student is currently enrolled in {self.student.course.name}. "
                f"You cannot issue certificate for {self.completed_course.name}."
            )
        
        # Prevent duplicate certificate
        existing = Certificate.objects.filter(
            student=self.student,
            completed_course=self.completed_course
        )

        if self.pk:
            existing = existing.exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError(
                "Certificate for this course already exists."
            )
    

    




    def save(self, *args, **kwargs):

        # 🔥 NEVER use middleware here
        if not self.franchise_id:
            if self.student and self.student.franchise:
                self.franchise = self.student.franchise
            else:
                raise ValueError("❌ Franchise must be set from student")

        # Prefix logic (keep yours)
        PREFIX = "SCI/SLG/"
        if self.certificate_no:
            suffix = self.certificate_no.replace(PREFIX, "")
            self.certificate_no = f"{PREFIX}{suffix}"

        # ✅ SAVE FIRST
        super().save(*args, **kwargs)

        # 🔥 AUTO UPDATE STUDENT STATUS (ADD THIS)
        try:
            student = self.student

            if student:
                if self.is_published:
                    student.course_completed = True
                else:
                    student.course_completed = False

                student.save(update_fields=["course_completed"])

        except Exception as e:
            print("⚠️ Student update skipped:", e)
     

class IssuedCertificate(models.Model):
        # Certificate: Always required, always validated
        certificate_file = models.FileField(
            upload_to='certificates/', 
            validators=[validate_file_size]
        )
        
        # Marksheet: Optional, but IF present, it MUST be less than 2MB
        marksheet_file = models.FileField(
            upload_to='marksheets/', 
            validators=[validate_file_size], 
            null=True, 
            blank=True
        )
# ================= UPGRADES & PROXIES =================


class CourseUpgrade(MultiTenantModel):
    student = models.ForeignKey(
        StudentAdmission,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    old_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="old_upgrades")
    new_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="new_upgrades")

    course_type = models.CharField(
        max_length=10,
        choices=StudentAdmission.TYPE_CHOICES,
        default="TYPE 1"
    )
    course_duration = models.IntegerField(null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    class_day = models.ForeignKey(BatchDay, on_delete=models.SET_NULL, null=True)
    class_time = models.ForeignKey(BatchTiming, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    history = HistoricalRecords()
    def clean(self):
        if self.old_course and self.new_course:
            if self.old_course == self.new_course:
                raise ValidationError({
                    "new_course": "New course cannot be the same as old course."
                })

        # 🔥 1. Already completed check
        already_completed = Certificate.objects.filter(
            student=self.student,
            completed_course=self.new_course
        ).exists()

        if already_completed:
            raise ValidationError({
                "new_course": "This course is already completed by the student."
            })

        # 🔥 2. Already enrolled (optional but recommended)
        already_enrolled = CourseEnrollment.objects.filter(
            student=self.student,
            course=self.new_course,
            is_active=True
        ).exists()

        if already_enrolled:
            raise ValidationError({
                "new_course": "Student is already enrolled in this course."
            })
    
    def save(self, *args, **kwargs):
        print("UPGRADE SAVE TRIGGERED")
        is_new = self.pk is None

        self.full_clean()

        with transaction.atomic():

            # If creating new upgrade
            if is_new:

                # Store old course
                self.old_course = self.student.course

                super().save(*args, **kwargs)

                # Deactivate current enrollment
                CourseEnrollment.objects.filter(
                    student=self.student,
                    is_active=True
                ).update(is_active=False)

                base_duration = self.new_course.duration
                base_monthly = self.new_course.monthly_fee

                if self.course_type == "TYPE 2":
                    duration = base_duration // 2
                    monthly_fee = base_monthly * 2
                else:
                    duration = base_duration
                    monthly_fee = base_monthly

                # Update student
                self.student.course = self.new_course
                self.student.course_type = self.course_type
                self.student.course_duration = duration
                self.student.monthly_fee = monthly_fee
                self.student.is_active = True
                self.student.save(from_upgrade=True)

                # Create new enrollment
                CourseEnrollment.objects.create(
                    student=self.student,
                    franchise=self.franchise,
                    course=self.new_course,
                    admission_date=self.start_date,
                    total_fee=self.new_course.total_fees,
                    monthly_fee=monthly_fee,
                    duration=duration,
                    admission_fee=self.new_course.admission_fee,
                    is_active=True,
                )

            else:
                # Just normal save if editing
                super().save(*args, **kwargs)

    
  

    def delete(self, *args, **kwargs):
        print("ROLLBACK DELETE TRIGGERED")

        with transaction.atomic():

            student = self.student
            old_course = self.old_course
            new_course = self.new_course

            # Get enrollments
            new_enrollment = CourseEnrollment.objects.filter(
                student=student,
                course=new_course
            ).first()

            old_enrollment = CourseEnrollment.objects.filter(
                student=student,
                course=old_course
            ).order_by("-admission_date").first()

            # 🚫 Block if certificate exists for new course
            cert_exists = Certificate.objects.filter(
                student=student,
                completed_course=new_course
            ).exists()

            if cert_exists:
                raise ValidationError(
                    "Cannot reverse upgrade. Certificate already issued for upgraded course."
                )

            # 🚫 Block if monthly payments exist
            if new_enrollment:
                monthly_exists = Fee.objects.filter(
                    enrollment=new_enrollment,
                    fee_type="MONTHLY"
                ).exists()

                if monthly_exists:
                    raise ValidationError(
                        "Cannot reverse upgrade. Monthly payments already exist."
                    )

            # 🔁 Delete new enrollment
            if new_enrollment:
                new_enrollment.delete()

            # 🔁 Reactivate old enrollment
            if old_enrollment:
                old_enrollment.is_active = True
                old_enrollment.save()

                # ✅ SAFE ROLLBACK (THIS IS THE FIX)
                student._rollback_mode = True

                student.course = old_course
                student.course_duration = old_enrollment.duration
                student.monthly_fee = old_enrollment.monthly_fee
                student.is_active = True

                student.save(update_fields=[
                    "course",
                    "course_duration",
                    "monthly_fee",
                    "is_active",
                ])

                del student._rollback_mode

            super().delete(*args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            # hide franchise field for franchise users
            if 'franchise' in form.base_fields:
                form.base_fields['franchise'].widget = forms.HiddenInput()

        return form



    def __str__(self):
            return f"{self.student.name} upgraded from {self.old_course.name} to {self.new_course.name}"






class PaymentHistory(StudentAdmission):
    class Meta:
        proxy = True
        verbose_name = "Payment History"
        verbose_name_plural = "Payment Histories"

    

    
class BatchListView(StudentAdmission):
    class Meta:
        proxy = True
        verbose_name = "Batch List"
        verbose_name_plural = "Batch Lists"



class AutomationLog(models.Model):

    last_run = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Last reminder run: {self.last_run}"
    

class Notice(MultiTenantModel):
    title = models.CharField(max_length=200)
    
    # ✅ Add this line to create the database link
    students = models.ManyToManyField(StudentAdmission, blank=True, related_name="notices")
    body = models.TextField()
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models import Sum
@receiver(post_delete, sender=CourseEnrollment)
def restore_student_after_upgrade_delete(sender, instance, **kwargs):

    student = instance.student

    # 🔥 student already deleted
    if not StudentAdmission.objects.filter(pk=student.pk).exists():
        return

    # Get last remaining enrollment
    last_enrollment = CourseEnrollment.objects.filter(
        student=student
    ).order_by("-id").first()

    if last_enrollment:
        student.course = last_enrollment.course
        student.is_active = True

        total_paid = Fee.objects.filter(
            enrollment=last_enrollment,
            fee_type="MONTHLY"
        ).aggregate(total=Sum("amount"))["total"] or 0

        remaining = last_enrollment.total_fee - total_paid

        student.course_completed = (remaining == 0)

    else:
        # No enrollment left
        student.course_completed = False
        student.is_active = False

    student.save(
        update_fields=[
            "course",
            "is_active",
            "course_completed"
        ],
        _skip_enrollment_sync=True
    )