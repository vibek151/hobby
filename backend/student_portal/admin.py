from .models import Fee, get_safe_date
from django.db.models import Sum
from django import forms
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.conf import settings
from .models import CourseUpgrade
import os
from django.http import JsonResponse
from simple_history.admin import SimpleHistoryAdmin
from django.db import models
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect # Add HttpResponseRedirect here
from django.db.models import IntegerField
from django.db.models.functions import Cast, Substr
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib import admin
from django.db.models import Sum, F
from django.utils.html import format_html
from django.urls import reverse
from .models import PaymentHistory, Fee
from django.shortcuts import render
from .models import PaymentHistory, Fee, StudentAdmission, CourseEnrollment, CourseUpgrade
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
# from .models import BatchList, BatchListStudent
from django.db.models import Count
from django.db import transaction
from core.utils.email_tasks import send_certificate_email_async
# from .models import BatchListView
from .models import BatchTiming
from .models import BatchListView
from django.db.models.signals import post_delete
from .models import restore_student_after_upgrade_delete
from .models import (
    StudentAdmission,
    PaymentHistory,
    Course,
    BatchDay,
    BatchTiming,
    Fee,
    Certificate,
)
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os
from django.conf import settings
from .models import Notice, StudentAdmission
from .notifications import send_student_email
from django.utils import timezone
from student_portal.signals import admission_email_signal
from django.contrib.auth.models import User, Group
admin.site.unregister(User)
admin.site.unregister(Group)
from .models import BatchDay
from reportlab.pdfbase.pdfmetrics import stringWidth

def draw_wrapped_text(p, text, x, y, max_width, line_height=14):
    words = text.split()
    line = ""

    for word in words:
        test_line = line + word + " "
        if stringWidth(test_line, "Helvetica", 11) < max_width:
            line = test_line
        else:
            p.drawString(x, y, line)
            y -= line_height
            line = word + " "

    if line:
        p.drawString(x, y, line)
        y -= line_height

    return y


from django import forms

class FranchiseRequiredForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.request and self.request.user.is_superuser:
            if not cleaned_data.get("franchise"):
                self.add_error("franchise", "Please select a franchise.")

        return cleaned_data


class FranchiseAdmin(admin.ModelAdmin):
    form = FranchiseRequiredForm
    # allow franchise login
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        class RequestForm(form):
            def __init__(self_inner, *args, **kw):
                kw["request"] = request
                super().__init__(*args, **kw)

        return RequestForm
    
    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # If NOT superuser → remove full Franchise section
        if not request.user.is_superuser:
            new_fieldsets = []

            for name, opts in fieldsets:
                # Skip the entire "Franchise Info" section
                if name == "Franchise Info":
                    continue

                new_fieldsets.append((name, opts))

            return new_fieldsets

        return fieldsets



    # 🔹 filter data by franchise
    # filter data by franchise
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        franchise = getattr(request.user, "franchise", None)

        if franchise:
            return qs.filter(franchise=franchise)

        return qs.none()
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # This line physically hides the franchise selector from your screen
            fields = [f for f in fields if f != 'franchise']
        return fields

    # 🔹 auto assign franchise on save
    def save_model(self, request, obj, form, change):

        if not request.user.is_superuser:
            franchise = getattr(request.user, "franchise", None)

            if franchise:
                obj.franchise = franchise

        super().save_model(request, obj, form, change)

    def history_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)

        history = list(obj.history.all().order_by("-history_date"))

        action_list = []

        for i, current in enumerate(history):
            previous = history[i + 1] if i + 1 < len(history) else None

            changes = []

            if current.history_type == "+":
                changes.append("Initial record created")

            elif previous:
                for field in current._meta.fields:
                    name = field.name

                    if name in [
                        "id",
                        "history_id",
                        "history_date",
                        "history_type"
                    ]:
                        continue

                    old = getattr(previous, name, None)
                    new = getattr(current, name, None)

                    if str(old) != str(new):
                        label = name.replace("_", " ").title()
                        changes.append(f"{label}: {old} → {new}")

            action_list.append({
                "history_date": current.history_date,
                "history_user": current.history_user or request.user,
                "history_type": current.history_type,
                "tooltip": "\n".join(changes),
            })

        return render(
            request,
            "admin/object_history.html",
            {
                **self.admin_site.each_context(request),
                "action_list": action_list,
                "object": obj,
                "original": obj,
                "opts": self.model._meta,
                "request": request,
            }
        )





class BatchListAdminView(FranchiseAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("batch-list/", self.admin_site.admin_view(self.batch_list_view))
        ]
        return custom_urls + urls

    def batch_list_view(self, request):
        batches = (
            StudentAdmission.objects
            .values("class_day", "class_timing")
            .annotate(total=Count("id"))
            .order_by("class_day", "class_timing")
        )

        context = dict(
            self.admin_site.each_context(request),
            batches=batches,
        )

        return render(request, "admin/batch_list.html", context)


# ======================================================
# STUDENT ADMISSION ADMIN
# ======================================================
# class BatchListStudentInline(admin.TabularInline):
#     model = BatchListStudent
#     extra = 1


# class BatchListAdmin(FranchiseAdmin):
#     list_display = ("days", "start_time", "end_time")
#     inlines = [BatchListStudentInline]


# admin.site.register(BatchList, BatchListAdmin)



class StudentAdmissionForm(FranchiseRequiredForm):
    class Meta:
        model = StudentAdmission
        fields = "__all__"
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "course_duration": forms.NumberInput(attrs={"readonly": "readonly"}),
            "monthly_fee": forms.NumberInput(attrs={"readonly": "readonly"}),
            "admission_amount": forms.NumberInput(attrs={"readonly": "readonly"}),
            "final_amount": forms.NumberInput(attrs={"readonly": "readonly"}),
            "student_id": forms.TextInput(attrs={"type": "text"}),
            "admission_date": forms.DateInput(attrs={"type": "date"}),
        }

    



    def __init__(self, *args, **kwargs):
        # This line is critical; it must come first to load the data
        super().__init__(*args, **kwargs)
        
        # 1. Ensure 'is_active' is not mandatory
        if "is_active" in self.fields:
            self.fields["is_active"].required = False

        # 2. Fix the red error boxes for files when Editing/Upgrading
        # If we have a Primary Key (pk), the files already exist in the database.
        if self.instance and self.instance.pk:
            file_fields = ["passport_photo", "last_qualification_file", "document_file"]
            for field_name in file_fields:
                if field_name in self.fields:
                    self.fields[field_name].required = False
    
        
        if "student_id" in self.fields and not self.instance.pk:

            franchise = self.initial.get(
                "franchise"
            )

            if not franchise and hasattr(
                self,
                "request"
            ):
                franchise = getattr(
                    self.request.user,
                    "franchise",
                    None
                )

            if not franchise:

                BASE = 1
                prefix1 = "MG"
                prefix2 = "SLG"

            else:

                BASE = int(
                    franchise.student_id_part3 or 1
                )

                prefix1 = (
                    franchise.student_id_part1
                    or "MG"
                )

                prefix2 = (
                    franchise.student_id_part2
                    or "SLG"
                )

            numbers = []

            for s in StudentAdmission.objects.filter(
                franchise=franchise
            ):

                if s.student_id:

                    try:

                        numbers.append(
                            int(
                                s.student_id.split("/")[-1]
                            )
                        )

                    except:
                        pass

            max_num = (
                max(numbers)
                if numbers
                else BASE - 1
            )

            next_num = max(
                max_num + 1,
                BASE
            )

            self.fields["student_id"].initial = (
                f"{prefix1}/"
                f"{prefix2}/"
                f"{str(next_num).zfill(4)}"
            )
        

    def clean_student_id(self):

        sid = self.cleaned_data.get("student_id")

        franchise = self.cleaned_data.get(
            "franchise"
        )

        if not franchise and hasattr(
            self,
            "request"
        ):
            franchise = getattr(
                self.request.user,
                "franchise",
                None
            )

        # default fallback
        if not franchise:
            BASE = 1
            prefix1 = "MG"
            prefix2 = "SLG"

        else:

            BASE = int(
                franchise.student_id_part3 or 1
            )

            prefix1 = (
                franchise.student_id_part1
                or "MG"
            )

            prefix2 = (
                franchise.student_id_part2
                or "SLG"
            )

        numbers = []

        for s in StudentAdmission.objects.exclude(
            pk=self.instance.pk
        ).filter(
            franchise=franchise
        ):

            if s.student_id:

                try:
                    numbers.append(
                        int(
                            s.student_id
                            .split("/")[-1]
                        )
                    )

                except:
                    pass

        biggest = (
            max(numbers)
            if numbers
            else BASE - 1
        )

        next_allowed = biggest + 1

        # blank → auto assign
        if not sid:

            return (
                f"{prefix1}/"
                f"{prefix2}/"
                f"{str(next_allowed).zfill(4)}"
            )

        sid = str(sid).strip()

        if "/" in sid:
            sid = sid.split("/")[-1]

        if not sid.isdigit():
            raise forms.ValidationError(
                "Enter number only"
            )

        num = int(sid)

        # cannot skip
        if num > next_allowed:

            raise forms.ValidationError(
                f"You can only go up to "
                f"{next_allowed}"
            )

        # cannot go below base
        if num < BASE:

            raise forms.ValidationError(
                f"Minimum ID is "
                f"{BASE}"
            )

        final = (
            f"{prefix1}/"
            f"{prefix2}/"
            f"{str(num).zfill(4)}"
        )

        if StudentAdmission.objects.exclude(
            pk=self.instance.pk
        ).filter(
            student_id=final
        ).exists():

            raise forms.ValidationError(
                "Student ID already exists"
            )

        return final


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     if "student_id" in self.fields and not self.instance.pk:
    #         last = StudentAdmission.objects.order_by("-id").first()

    #         if last and last.student_id:
    #             num = int(last.student_id.split("/")[-1]) + 1
    #         else:
    #             num = 1

    #         self.fields["student_id"].initial = f"MG/SLG/{num}"

   

    # =========================
    # NAME → Auto Capitalize
    # =========================
    def clean_name(self):
        name = self.cleaned_data.get("name")

        if not name:
            return name

        return name.title()


    def clean_guardian_name(self):
        name = self.cleaned_data.get("guardian_name")

        if not name:
            return name

        return name.title()

    # =========================
    # DOB Validation
    # =========================
    def clean_dob(self):
        dob = self.cleaned_data.get("dob")

        if not dob:
            return dob

        today = date.today()

        # ❌ future DOB
        if dob > today:
            raise ValidationError("DOB cannot be in future.")

        # ❌ younger than 7
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        if age < 7:
            raise ValidationError("Student must be at least 7 years old.")

        return dob

    # =========================
    # PHONE → 10 digit numeric
    # =========================
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone.isdigit():
            raise ValidationError("Phone must be numeric.")

        if len(phone) != 10:
            raise ValidationError("Phone must be exactly 10 digits.")

        return phone

    # =========================
    # FILE TYPE VALIDATION
    # =========================
    def clean_last_qualification_file(self):
        file = self.cleaned_data.get("last_qualification_file")

        if file:
            ext = file.name.split(".")[-1].lower()
            if ext not in ["jpg", "jpeg", "png", "pdf"]:
                raise ValidationError(
                    "Only JPG, PNG or PDF allowed."
                )

        return file

    def clean_document_file(self):
        file = self.cleaned_data.get("document_file")

        if file:
            ext = file.name.split(".")[-1].lower()
            if ext not in ["jpg", "jpeg", "png", "pdf"]:
                raise ValidationError(
                    "Only JPG, PNG or PDF allowed."
                )

        return file

    # =========================
    # AADHAR VALIDATION
    # =========================
    def clean_document_number(self):
        doc_type = self.cleaned_data.get("document_type")
        number = self.cleaned_data.get("document_number")

        if doc_type and doc_type.upper() == "AADHAAR":

            if not number:
                raise ValidationError("Aadhaar number is required.")

            number = str(number).strip()

            if not number.isdigit():
                raise ValidationError("Aadhaar must be numeric.")

            if len(number) != 12:
                raise ValidationError("Aadhaar must be 12 digits.")

            # 🔥 DUPLICATE CHECK
            exists = StudentAdmission.objects.filter(
                document_type="AADHAAR",
                document_number=number,
                # is_deleted=False  # 🔥 ignore deleted students
            ).exclude(pk=self.instance.pk).exists()

            if exists:
                raise ValidationError(
                    "This Aadhaar number is already registered."
                )

        return number


    # =========================
    # RECEIPT NUMBER
    # =========================
    def clean_receipt_no(self):
        receipt = self.cleaned_data.get("receipt_no")

        if receipt and not receipt.isdigit():
            raise ValidationError(
                "Receipt number must be numeric."
            )

        return receipt

    # =========================
    # ADMISSION DATE
    # =========================
    def clean_admission_date(self):
        adate = self.cleaned_data.get("admission_date")

        if adate and adate > date.today():
            raise ValidationError(
                "Admission date cannot be future date."
            )

        return adate




@admin.register(StudentAdmission)
class StudentAdmissionAdmin(FranchiseAdmin, SimpleHistoryAdmin):
 
    form = StudentAdmissionForm
    readonly_fields = () 
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk:
            certificate_exists = obj.certificate_set.filter(
                completed_course_id=obj.course_id
            ).exists()

            if certificate_exists:
                return self.readonly_fields + ("course",)

        return self.readonly_fields
  
    actions = [
        "restore_students",
        "safe_delete_students",
    ]
    
    def get_actions(self, request):
        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions
    
    def restore_students(self, request, queryset):
        # Flips the switch back to active
        queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, "Selected students have been restored.")
    
    restore_students.short_description = "Restore selected students"

    form = StudentAdmissionForm
    list_display = ('name', 'student_id', 'course', 'footprint'
                    # 'is_deleted'
                    )
    
    # ADD THIS LINE BELOW
    # list_filter = ('is_deleted',) 
    filter_horizontal = ("class_day",)
    # actions = ['restore_students']

    class Media:
        css = {
        "all": ("admin/file_preview.css",
                "https://cdn.jsdelivr.net/npm/litepicker/dist/css/litepicker.css",
                )
        }
        js = ("admin/course_autofill.js",
                "admin/upgrade_autofill.js",
                'js/admin_upgrade.js',
                "admin/file_preview.js",
                'admin/js/admin_upgrade.js',
                "admin/input_restrict.js",
            #  'admin/js/student_upgrade.js',
                "https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js",
                "admin/js/calendar.js",
                "admin/js/batch_capacity.js",
              )

    readonly_fields = (
        # "student_id",
        "course_completed",
        "fees_history",
        "is_active",
        # "final_amount",
        # "monthly_fee",
        # "course_duration",
        "passport_preview",
        "qualification_preview",
        "document_preview",
        # "admission_amount",
    )

    list_display = (
        'name',
        'student_id',
        'course',
        'course_completed_display',
        'status_tag',
        'is_active',
        'upgrade_button',
        'add_payment_button',   # 👈 add this
        'download_pdf',
        'report_button',
        'resend_mail_button',
        'last_modified_by',  # 👈 Add this for Step 3 transparency
    )
    
    def course_completed_display(self, obj):
        return obj.course_completed

    course_completed_display.boolean = True
    course_completed_display.short_description = "Course Completed"

    list_filter = (
        'course',
        'class_day',
        'class_time',
        'is_active',
        'is_freezed',        # 👈 ADD THIS
        'course_completed',  # 👈 ADD THIS
    )

    def last_modified_by(self, obj):
        # This pulls from the simple-history records
        last_history = obj.history.first()
        if last_history and last_history.history_user:
            return f"{last_history.history_user} ({last_history.history_date.strftime('%d-%m %H:%M')})"
        return "Original"

    last_modified_by.short_description = "Footprint"

    def upgrade_button(self, obj):

        if not obj.course_completed:
            return format_html(
                '<img src="/static/admin/img/icon-no.svg" alt="False">'
            )

        return format_html(
            '<a class="button" href="{}">Upgrade</a>',
            reverse("admin:student_portal_courseupgrade_add") + f"?student={obj.id}"
        )

    def passport_preview(self, obj):
        if obj.passport_photo:
            return format_html(
                '<a href="{}" target="_blank">👁 View uploaded</a>',
                obj.passport_photo.url
            )
        return "No file"

    def qualification_preview(self, obj):
        if obj.last_qualification_file:
            return format_html(
                '<a href="{}" target="_blank">👁 View uploaded</a>',
                obj.last_qualification_file.url
            )
        return "No file"

    def document_preview(self, obj):
        if obj.document_file:
            return format_html(
                '<a href="{}" target="_blank">👁 View uploaded</a>',
                obj.document_file.url
            )
        return "No file"



    upgrade_button.short_description = "Upgrade"
    search_fields = ("name", "=student_id", "=phone", "=document_number")
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        query = request.GET.get("q")
        match_field = None

        if query:
            qs = super().get_queryset(request)

            if qs.exists():
                obj = qs.first()

                if obj.document_number == query:
                    match_field = "Aadhaar Number"

                elif obj.phone == query:
                    match_field = "Phone Number"

                elif obj.student_id == query:
                    match_field = "Student ID"

                elif query.lower() in obj.name.lower():
                    match_field = "Name"

        extra_context["search_match_field"] = match_field

        return super().changelist_view(request, extra_context=extra_context)

    fieldsets = (
        ("Franchise Info", {
            "fields": ("franchise",),   # 🔥 MUST BE HERE
        }),
    
        

        ("Personal Details", {
            "fields": (
                "name",
                "guardian_name",
                "dob",
                "phone",
                "email",
                "gender",
                "qualification",
                "address",
            )
        }),
        ("Documents & Uploads", {
            "fields": (
                "passport_photo",
                "last_qualification_file",
                "document_type",
                "document_number",
                "document_file",
            )
        }),
        ("Course Information", {
            "fields": (
                "course",
                "course_type",
                "course_duration",
                "class_time",
                "class_day",
            )
        }),
        ("Fees & Payment", {
            "fields": (
                "monthly_fee",
                "admission_amount",
                "discount_percent",
                "advance_fees",
                "final_amount",
                "receipt_no",
                "admission_date",
                "admission_pay_via",
                
            )
        }),
        ("System Details", {
            "classes": ("collapse",),
            "fields": (
                
                "student_id",
                "is_active",
                "is_suspended",
                "leave_start",
                "leave_until",
                "course_completed",
                'is_freezed',
                "fees_history",
            ),
        }),
    )
    def student_id_display(self, obj):
        if obj and obj.student_id:
            return obj.student_id
        
        # For upgrade/add page
        sid = getattr(self, "_upgrade_student_id", None)
        return sid or "-"
        
    student_id_display.short_description = "Student id"

    def report_button(self, obj):
        url = reverse("admin:student_report", args=[obj.id])
        return format_html(
            '<a class="button" target="_blank" href="{}">📄 Report</a>',
            url
        )
    report_button.short_description = "Report"
    from django.http import JsonResponse

    def get_student_data(self, request):
        student_id = request.GET.get("student_id")

        student = StudentAdmission.objects.filter(pk=student_id).first()

        if not student:
            return JsonResponse({"error": "Student not found"}, status=404)

        return JsonResponse({
            "course": student.course_id,
        })
    # ================= FEES HISTORY TABLE =================
    def fees_history(self, obj):
        if not obj.pk:
            return "Save student first."

        html = "<table border='1' style='border-collapse:collapse; width:100%;'>"
        html += "<tr><th>Date</th><th>Amount</th><th>Receipt</th><th>Method</th></tr>"

        # Loop through all enrollments of this student
        enrollments = obj.enrollments.all()

        for enrollment in enrollments:
            fees = enrollment.payments.all().order_by("payment_date")

            for f in fees:
                html += (
                    f"<tr>"
                    f"<td>{f.payment_date}</td>"
                    f"<td>Rs. {f.amount}</td>"
                    f"<td>{f.receipt_no}</td>"
                    f"<td>{f.pay_via}</td>"
                    f"</tr>"
                )

        return format_html(html + "</table>")
    # ================= PDF BUTTON =================
    def download_pdf(self, obj):
        url = reverse("admin:student_pdf", args=[obj.id])
        return format_html('<a class="button" href="{}">PDF</a>', url)

    download_pdf.short_description = "Form"
    # ================= URLS =================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "resend-mail/<int:student_id>/",
                self.admin_site.admin_view(
                    self.resend_admission_mail
                ),
                name="resend_admission_mail",
            ),
            path("download-pdf/<int:student_id>/",
                 self.admin_site.admin_view(self.generate_pdf),
                 name="student_pdf"),
            path("get-course-data/",
                 self.admin_site.admin_view(self.get_course_data),
                 name="get_course_data"),
            path(
                "get-student-data/",
                self.admin_site.admin_view(self.get_student_data),
                name="get_student_data",
            ),
            
            path(
                "student-report/<int:student_id>/",
                self.admin_site.admin_view(self.student_report),
                name="student_report",
                ),
            path(
                "check-batch-capacity/",
                self.admin_site.admin_view(self.check_batch_capacity),
                name="check_batch_capacity",
            ),
        ]
        return custom_urls + urls
    

    def check_batch_capacity(self, request):

        class_time_id = request.GET.get("class_time")
        batch_day_id = request.GET.get("batch_day")

        count = (
            StudentAdmission._base_manager
            .filter(
                class_time_id=class_time_id,
                class_day__id=batch_day_id
            )
            .distinct()
            .count()
        )

        capacity = int(request.GET.get("capacity", 1))

        available_seats = capacity - count

        return JsonResponse({
            "full": available_seats <= 0,
            "available_seats": available_seats,
            "count": count,
            "capacity": capacity,
        })
    
    
    def student_report(self, request, student_id):

        student = StudentAdmission.objects.get(id=student_id)

        # All enrollments (old + new)
        enrollments = CourseEnrollment.objects.filter(
            student=student
        ).select_related("course")

        course_data = []
        overall_paid = 0
        overall_fine = 0

        for enrollment in enrollments:

            payments = Fee.objects.filter(
                enrollment=enrollment
            ).order_by("payment_date")

            total_paid = payments.aggregate(
                total=Sum("amount")
            )["total"] or 0

            total_fine = payments.aggregate(
                total=Sum("fine")
            )["total"] or 0

            remaining = (enrollment.total_fee or 0) - total_paid

            overall_paid += total_paid
            overall_fine += total_fine

            course_data.append({
                "course": enrollment.course,
                "payments": payments,
                "total_paid": total_paid,
                "total_fine": total_fine,
                "remaining": remaining,
                "is_active": enrollment.is_active,
            })

        certificates = Certificate.objects.filter(student=student)

        context = {
            "student": student,
            "course_data": course_data,
            "certificates": certificates,
            "overall_paid": overall_paid,
            "overall_fine": overall_fine,
            "grand_total": overall_paid + overall_fine,
        }

        return render(request, "admin/student_report.html", context)

    def status_tag(self, obj):
        if obj.is_freezed:
            return format_html('<span style="color:#6c757d;">🔒 Freezed</span>')
        elif obj.course_completed:
            return format_html('<span style="color:#28a745;">✔ Completed</span>')
        return format_html('<span style="color:#007bff;">Active</span>')

    status_tag.short_description = "Status"


    def get_student_data(self, request):
        sid = request.GET.get("student_id")

        try:
            s = StudentAdmission.objects.get(id=sid)

            return JsonResponse({
                "student_id": s.student_id,
                "name": s.name,
                "guardian_name": s.guardian_name,
                "phone": s.phone,
                "dob": s.dob,
                "gender": s.gender,
                "qualification": s.qualification,
                "address": s.address,
            })
        except:
            return JsonResponse({})
    # ================= AJAX COURSE DATA =================
    def get_course_data(self, request):
        course_id = request.GET.get("course_id")
        try:
            course = Course.objects.get(id=course_id)
            return JsonResponse({
                "duration": course.duration,
                "admission_fee": float(course.admission_fee or 0),
                "monthly_fee": float(course.monthly_fee or 0),
                "total_fees": float(course.total_fees or 0),
            })
        except:
            return JsonResponse({}, status=404)
    
    # ================= PDF GENERATOR =================
    def generate_pdf(self, request, student_id):
            print("ADMIN PDF FUNCTION CALLED")
            print("Student ID =", student_id)
            from django.shortcuts import get_object_or_404

            student = StudentAdmission._base_manager.get(id=student_id)


            
            # Check for previous courses (Completed upgrades)
            prev_course = None

            previous_admissions = StudentAdmission.objects.filter(
                student_id=student.student_id
            ).exclude(id=student.id)

            for admission in previous_admissions:
                if admission.course_completed:
                    prev_course = admission
                    break

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{student.name}.pdf"'
            p = canvas.Canvas(response, pagesize=A4)
            width, height = A4
            page_number = 1
            # Logo & Branding
            logo_path = os.path.join(settings.BASE_DIR, "student_portal/static/logo.jpg")
            if os.path.exists(logo_path):
                p.drawImage(logo_path, 40, height-90, width=70, height=70)

            p.setFont("Helvetica-Bold", 24)
            p.drawCentredString(width/2 + 33, height-40, "SMART COMPUTER INSTITUTE")
            p.setFont("Helvetica", 11)
            p.drawCentredString(width-157, height-60, "Build Skills, Build Futures.....")
            p.line(120, height-80, 550, height-80)

            p.setFont("Helvetica-Bold", 16)
            p.drawCentredString(width/2, height-100, "ADMISSION FORM")

            # Watermark Section
            if os.path.exists(logo_path):
                p.saveState()
                p.setFillAlpha(0.1)
                p.drawImage(logo_path, (width - 300) / 2, (height - 300) / 2 + 50, width=300, height=300, mask='auto', preserveAspectRatio=True)
                p.restoreState()

            # Passport Photo
            if student.passport_photo:
                try:
                    p.rect(width - 155, height - 240, 100, 120)
                    p.drawImage(student.passport_photo.path, width - 155, height - 240, width=100, height=120)
                except: pass
            
            y = height-145
            p.setFont("Helvetica-Bold", 13); p.drawString(40, y, "PERSONAL DETAILS"); y -= 20
            p.setFont("Helvetica", 11)
            details = [
                f"Student ID : {student.student_id}",
                f"Name : {student.name}",
                f"Guardian Name : {student.guardian_name}",
                f"DOB : {student.dob}",
                f"Phone : {student.phone}",
                f"Email : {student.email}",
                f"Qualification : {student.qualification}",
                f"Gender : {student.gender}",
                f"Admission Date : {student.admission_date.strftime('%d-%m-%Y') if student.admission_date else '-'}",
                f"Document No.:{student.document_number}",
                f"Address : {student.address}",
            ]
            for line in details:
                y = draw_wrapped_text(p, line, 50, y, 450)

            # Previous Course Logic
            if prev_course:
                y -= 10; p.setFont("Helvetica-Bold", 13); p.drawString(40, y, "PREVIOUS COURSE RECORD"); y -= 20
                p.setFont("Helvetica", 11)
                cert = Certificate.objects.filter(enrollment__student=prev_course).first()
                p.drawString(50, y, f"Course: {prev_course.course}"); y -= 18
                p.drawString(50, y, f"Certificate No: {getattr(cert, 'certificate_no', 'N/A')}"); y -= 18
                p.drawString(50, y, f"Marksheet No: {getattr(cert, 'marksheet_no', 'N/A')}"); y -= 25

            # Course Details
            y -= 10; p.setFont("Helvetica-Bold", 13); p.drawString(40, y, "COURSE DETAILS"); y -= 20
            p.setFont("Helvetica", 11)
            student = StudentAdmission._base_manager.prefetch_related(
                "class_day"
            ).get(id=student.id)

            print("CLASS DAYS =", list(student.class_day.all()))

            days = ", ".join(
                BatchDay._base_manager.filter(
                    studentadmission=student
                ).values_list(
                    "day",
                    flat=True
                )
            ) or "-"
            
            c_info = [
                    f"Course : {student.course.code} - {student.course.name}", 
                    f"Type : {student.course_type}", 
                    f"Duration : {student.course_duration} Months",
                    f"Batch Days : {days}",
                    f"Batch Time : {student.class_time}"
                    ]
            for line in c_info: p.drawString(50, y, line); y -= 18

            # Payment Details
            y -= 10; p.setFont("Helvetica-Bold", 13); p.drawString(40, y, "PAYMENT DETAILS"); y -= 20
            p.setFont("Helvetica", 11)
            p_info = [f"Receipt No : {student.receipt_no}", f"Admission Fee : Rs. {student.admission_amount}", f"Discount (%) : {student.discount_percent}", f"Final Amount : Rs. {student.final_amount}", f"Monthly Fee : Rs. {student.monthly_fee}"]
            for line in p_info: p.drawString(50, y, line); y -= 18

            # Rules
            y -= 10; p.setFont("Helvetica-Bold", 13); p.drawString(40, y, "RULES & REGULATIONS"); y -= 20
            p.setFont("Helvetica", 10)
            rules = [
                    "1. Student ID card must be carried during class.", 
                    "2. Arrive on time; repeated lateness affects attendance.", 
                    "3. Study materials are for personal use only.", 
                    "4. Inform  the office before taking long leave.",
                    "5. Institute may revise rules and enforce discipline."
                    ]
            for rule in rules: p.drawString(50, y, rule); y -= 15


            signature_path = None

            franchise = getattr(student, "franchise", None)

            if franchise and franchise.signature:
                try:
                    signature_path = franchise.signature.path
                except:
                    signature_path = None

            if signature_path and os.path.exists(signature_path):
                try:
                    # Fixed signature size
                    signature_width = 150
                    signature_height = 50

                    # Position
                    signature_x = width - 190
                    signature_y = 65

                    p.drawImage(
                        signature_path,
                        signature_x,
                        signature_y,
                        width=signature_width,
                        height=signature_height,
                        mask='auto'
                    )

                except Exception as e:
                    print("Signature draw error:", e)


            # Signature & Footer
            # p.drawRightString(width-40, footer_y - -15, "Authorized Signatory")
            p.line(width - 200, 65, width - 50, 65)
            p.setFont("Helvetica-Oblique", 11)
            p.drawRightString(width - 50, 55, "Authorized Signatory")
        

            timestamp = datetime.now().strftime("%d-%m-%Y | %I:%M %p")

            p.setFont("Helvetica", 9)
            p.drawString(40, 45, f"Generated on: {timestamp}")

            p.setStrokeColorRGB(0, 0, 0); p.line(40, 35, 550, 35)
            p.setFont("Helvetica", 9); p.saveState(); p.setFillAlpha(0.6)
            p.drawString(40, 25, "SMART COMPUTER INSTITUTE"); p.restoreState()
            p.drawRightString(550, 25, f"Page | {page_number}")
            page_number += 1
            
            p.showPage(); p.save()
            return response

    def save_model(self, request, obj, form, change):

        is_upgrade = request.GET.get("upgrade") and request.GET.get("student_id")

        # =========================
        # COURSE CALCULATION
        # =========================
        if obj.course:
            obj.admission_amount = obj.course.admission_fee or 0

            base_duration = obj.course.duration or 0
            base_monthly = obj.course.monthly_fee or 0

            if obj.course_type == "TYPE 2":
                obj.course_duration = int(base_duration / 2)
                obj.monthly_fee = base_monthly * 2
            else:
                obj.course_duration = base_duration
                obj.monthly_fee = base_monthly

            adm_amt = float(obj.admission_amount or 0)
            disc_percent = float(obj.discount_percent or 0)
            adv_fees = float(obj.advance_fees or 0)

            after_discount = adm_amt - (adm_amt * (disc_percent / 100))
            obj.final_amount = after_discount - adv_fees

        # 🔥 If upgrade, force new object BEFORE save
        if is_upgrade:
            obj.pk = None
            obj._state.adding = True

        # Save once
        super().save_model(request, obj, form, change)

        # 🔥 After saving new record → mark old inactive
        if is_upgrade:
            old = StudentAdmission.objects.get(id=request.GET.get("student_id"))
            old.is_active = False
            old.course_completed = True
            old.save(update_fields=["is_active", "course_completed"])
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        # Only run in upgrade mode
        if request.GET.get("upgrade") and request.GET.get("student_id"):

            sid = request.GET.get("student_id")

            try:
                old = StudentAdmission.objects.get(id=sid)

                # ===============================
                # Copy ONLY personal information
                # ===============================
                initial.update({
                    "student_id": old.student_id,
                    "name": old.name,
                    "guardian_name": old.guardian_name,
                    "dob": old.dob,
                    "phone": old.phone,
                    "gender": old.gender,
                    "qualification": old.qualification,
                    "address": old.address,

                    # Documents
                    "passport_photo": old.passport_photo,
                    "last_qualification_file": old.last_qualification_file,
                    "document_type": old.document_type,
                    "document_number": old.document_number,
                    "document_file": old.document_file,

                    # Keep same batch timing (optional)
                    "class_day": old.class_day,
                    "class_time": old.class_time,
                })

               

            except StudentAdmission.DoesNotExist:
                pass

        return initial
    
    

    def add_payment_button(self, obj):

        # Get active enrollment
        enrollment = obj.enrollments.filter(is_active=True).first()

        if not enrollment:
            return "-"

        # Calculate total monthly paid
        total_paid = (
            enrollment.payments
            .filter(fee_type="MONTHLY")
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        remaining = enrollment.total_fee - total_paid

        # If fully paid
        if remaining <= 0:
            return format_html(
                '<span style="color:green; font-weight:bold;">Fully Paid ✓</span>'
            )

        # Otherwise show button
        url = reverse("admin:student_portal_fee_add") + f"?student={obj.id}"
        return format_html('<a class="button" href="{}">Add Payment</a>', url)
    
    from django.contrib import messages

    def delete_queryset(self, request, queryset):

        blocked = queryset.filter(certificate__isnull=False).distinct()

        if blocked.exists():
            self.message_user(
                request,
                "One or more selected students cannot be deleted because certificates have already been issued.",
                level=messages.ERROR,
            )

            queryset = queryset.exclude(pk__in=blocked)

        for obj in queryset:
            self.delete_model(request, obj)
        

    def delete_model(self, request, obj):
        print("DELETE MODEL CALLED")
        # 🚫 Block deletion if certificate exists
        if obj.certificate_set.exists():
            self.message_user(
                request,
                "This student cannot be deleted because a certificate has already been issued.",
                level=messages.ERROR,
            )
            return

        # 🔥 temporarily disconnect signal
        post_delete.disconnect(
            restore_student_after_upgrade_delete,
            sender=CourseEnrollment
        )

        try:

            # delete certificates
            for cert in obj.certificate_set.all():
                cert.delete(bypass_lock=True)

            # delete enrollments directly
            obj.enrollments.all().delete()

            # finally delete student
            obj.delete()

        finally:

            # reconnect signal
            post_delete.connect(
                restore_student_after_upgrade_delete,
                sender=CourseEnrollment
            )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "course":
            kwargs["queryset"] = Course.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def resend_mail_button(self, obj):

        url = reverse(
            "admin:resend_admission_mail",
            args=[obj.id]
        )

        return format_html(
            '<a class="button" href="{}">📧 Send Again</a>',
            url
        )

    resend_mail_button.short_description = "Mail"
    from django.contrib import messages
    from django.contrib.admin import action

    @action(description="Delete selected student admissions")
    def safe_delete_students(self, request, queryset):

        deleted = 0

        for obj in queryset:

            if obj.certificate_set.exists():
                self.message_user(
                    request,
                    f"{obj.name} cannot be deleted because a certificate has already been issued.",
                    messages.ERROR,
                )
                continue

            self.delete_model(request, obj)
            deleted += 1

        if deleted:
            self.message_user(
                request,
                f"Successfully deleted {deleted} student admission(s).",
                messages.SUCCESS,
            )

    def resend_admission_mail(
        self,
        request,
        student_id
    ):

        student = StudentAdmission.objects.get(
            id=student_id
        )
        # trigger existing signal again
        admission_email_signal(
            sender=StudentAdmission,
            instance=student,
            created=True
        )

        self.message_user(
            request,
            "Admission mail sent again."
        )

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "/admin/"
            )
        )




    ordering = ["-id"]



@admin.register(CourseUpgrade)
class CourseUpgradeAdmin(FranchiseAdmin, SimpleHistoryAdmin):

    list_display = ("student", "old_course", "new_course", "start_date")

    class Media:
        js = ("admin/js/student_admission.js",
              'admin/js/ctrl_save.js',
              )

    # 🔒 Hide Add button
    def has_add_permission(self, request):
        return request.user.is_staff

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        student_id = request.GET.get("student")

        if student_id:
            student = StudentAdmission.objects.filter(pk=student_id).first()
            if student:
                form.base_fields["student"].initial = student
                form.base_fields["old_course"].initial = student.course

                form.base_fields["student"].disabled = True
                form.base_fields["old_course"].disabled = True

        return form
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]  # disable bulk delete
        return actions
    
    def has_delete_permission(self, request, obj=None):
        return True

    def delete_model(self, request, obj):
        obj.delete()  # ensure model.delete() runs




# ======================================================
# OTHER ADMINS - Ensure (FranchiseAdmin) is present
# ======================================================

@admin.register(Course)
class CourseAdmin(FranchiseAdmin, SimpleHistoryAdmin):
    list_display = ('code', 'name', 'total_fees', 'duration', 'monthly_fee')
    # filter_horizontal = ("exams",)


from datetime import datetime
@admin.register(Fee)
class FeeAdmin(FranchiseAdmin, SimpleHistoryAdmin):
    exclude = (
        "generated_fee",
        "remaining_fee",
        "remaining_fine",
        "generated_fine",
        "generated_total",
    )
    readonly_fields = ("fee_type",)
    autocomplete_fields = ["enrollment"]
    list_display = (
        "get_student",
        "enrollment",
        "amount",
        "receipt_no",
        "payment_date",
        "fee_type_display",
        "total_amount",
        "waive_fine",
        "last_modified_by",
    )
    
    actions = ["safe_delete"]



    def last_modified_by(self, obj):
        # Fetch the most recent entry from the history table
        last_history = obj.history.first() 
        if last_history and last_history.history_user:
            # Returns: "Ironman (24-04 17:30)"
            return f"{last_history.history_user} ({last_history.history_date.strftime('%d-%m %H:%M')})"
        return "Original Record"

    # Sets the column header in the Admin UI
    last_modified_by.short_description = "Footprint (Who & When)"

    def fee_type_display(self, obj):
        return obj.fee_type
    fee_type_display.short_description = "Type"

    def get_student(self, obj):
        return obj.enrollment.student.name
    get_student.short_description = "Student"
    def has_delete_permission(self, request, obj=None):
        return True
    # def save(self, *args, **kwargs):
    #     self.total_amount = (self.amount or 0) + (self.fine or 0)
    #     super().save(*args, **kwargs)

    # ----------------------------
    # CUSTOM ADMIN URLS
    # ----------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "get-monthly-fee/",
                self.admin_site.admin_view(self.get_monthly_fee),
                name="get_monthly_fee",
            ),
        ]
        return custom_urls + urls

    def get_actions(self, request):
        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    # ----------------------------
    # SAVE MODEL (certificate sync)
    # ----------------------------
    def save_model(self, request, obj, form, change):

        # =========================================
        # 🔒 WAIVE LOCK LOGIC (NEW - SAFE MERGE)
        # =========================================
        if change:  # editing existing record
            old_obj = obj.__class__.objects.get(pk=obj.pk)

            if old_obj.waive_fine and not obj.waive_fine:
                
                messages.error(request, "Waived fine cannot be reverted once applied.")

                # 🔁 restore original state
                obj.waive_fine = True
                obj.fine = 0

        # =========================================
        # 🔢 AUTO GENERATE RECEIPT NUMBER (UNCHANGED)
        # =========================================
        if obj.receipt_no is None or str(obj.receipt_no).strip() == "":
            
            last_fee = Fee.objects.order_by("-id").first()

            if last_fee and str(last_fee.receipt_no).isdigit():
                new_number = int(last_fee.receipt_no) + 1
            else:
                new_number = 1

            obj.receipt_no = str(new_number)

        # =========================================
        # 🚫 VALIDATION (UNCHANGED)
        # =========================================
        if not str(obj.receipt_no).isdigit():
            messages.error(request, "Receipt number must contain only digits (0-9).")
            return

        # =========================================
        # 💰 ENSURE WAIVE EFFECT (NEW - IMPORTANT)
        # =========================================
        if obj.waive_fine:
            obj.fine = 0

        # =========================================
        # ✅ SAVE (UNCHANGED POSITION)
        # =========================================
        super().save_model(request, obj, form, change)
        # =========================================
        # 📊 YOUR EXISTING LOGIC (UNCHANGED)
        # =========================================
        enrollment = obj.enrollment

        total_paid = (
            Fee.objects
            .filter(enrollment=enrollment, fee_type="MONTHLY")
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        remaining = enrollment.total_fee - total_paid

        certificates = Certificate.objects.filter(
            student=enrollment.student,
            completed_course=enrollment.course
        )

        for cert in certificates:

            cert.is_published = (
                remaining == 0
                and cert.check_exam_completion()
            )

            if cert.is_published and not cert.published_at:
                cert.published_at = timezone.now()

            if not cert.is_published:
                cert.published_at = None

            cert.save(update_fields=[
                "is_published",
                "published_at",
            ])

    # =========================================
    # 🔒 MOVE THIS OUTSIDE (IMPORTANT FIX)
    # =========================================
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [
                "fee_type",
                "waive_fine",
                "receipt_no",
                "enrollment",
                
            ]
        return ["fee_type"]
            
    
    # ----------------------------
    # 🔒 SAFE DELETE ACTION
    # ----------------------------
    @admin.action(description="Delete selected fees")
    def safe_delete(self, request, queryset):

        for obj in queryset:
            student = obj.enrollment.student

            # 🚫 Block admission delete
            if obj.fee_type == "ADMISSION":
                self.message_user(
                    request,
                    "⚠️ Admission fee is restricted. To remove it, delete the Student Admission instead.",
                    level=messages.ERROR
                )
                return

            # 🔒 Block old course delete
            if student.course != obj.enrollment.course:

                cert_exists = Certificate.objects.filter(
                    student=student,
                    completed_course=obj.enrollment.course
                ).exists()

                if cert_exists:
                    self.message_user(
                        request,
                        f"Payment (Receipt No: {obj.receipt_no}) cannot be deleted because the course is completed and locked.",
                        level=messages.ERROR
                    )
                    return

        for obj in queryset:
            obj.delete()

        self.message_user(
            request,
            f"Successfully deleted {queryset.count()} fee(s).",
            level=messages.SUCCESS
        )

    # ----------------------------
    # DELETE BUTTON CONTROL
    # ----------------------------
    # def has_delete_permission(self, request, obj=None):

    #     if obj is None:
    #         return True

    #     if obj.fee_type == "ADMISSION":
    #         return False

    #     if obj.enrollment and obj.enrollment.student.course != obj.enrollment.course:
    #         return False

    #     return True

    # ----------------------------
    # DELETE SINGLE OBJECT
    # ----------------------------
    def delete_model(self, request, obj):

        student = obj.enrollment.student

        if obj.fee_type == "ADMISSION":
            messages.error(
                request,
                "⚠️ Admission fee is restricted. To remove it, delete the Student Admission instead."
            )
            return

        if student.course != obj.enrollment.course:

            cert_exists = Certificate.objects.filter(
                student=student,
                completed_course=obj.enrollment.course
            ).exists()

            if cert_exists:
                messages.error(
                    request,
                    "Cannot delete payment. This course is already completed and locked."
                )
                return

        super().delete_model(request, obj)

    # ----------------------------
    # DELETE BULK (ADMIN)
    # ----------------------------
    def delete_queryset(self, request, queryset):

        blocked = False

        for obj in queryset:
            student = obj.enrollment.student

            # 🚫 Admission block
            if obj.fee_type == "ADMISSION":
                messages.error(
                    request,
                    "⚠️ Admission fee is restricted. To remove it, delete the Student Admission instead."
                )
                blocked = True

            # 🔒 Course lock block
            elif student.course != obj.enrollment.course:

                cert_exists = Certificate.objects.filter(
                    student=student,
                    completed_course=obj.enrollment.course
                ).exists()

                if cert_exists:
                    messages.error(
                        request,
                        f"Cannot delete payment {obj.receipt_no}. Course is locked."
                    )
                    blocked = True

        # ❌ If ANY blocked → STOP ALL DELETE
        if blocked:
            return

        # ✅ Only delete if everything is safe
        super().delete_queryset(request, queryset)

    # ----------------------------
    # AJAX: GET MONTHLY FEE
    # ----------------------------

    def get_monthly_fee(self, request):

        from datetime import datetime
        from django.utils import timezone
        from student_portal.fee_engine import calculate_student_dues

        enrollment_id = request.GET.get("enrollment_id")

        try:

            enrollment = CourseEnrollment.objects.get(
                id=enrollment_id
            )

            payment_date = request.GET.get(
                "payment_date"
            )

            if payment_date:

                today = datetime.strptime(
                    payment_date,
                    "%Y-%m-%d"
                ).date()

            else:

                today = timezone.now().date()

            data = calculate_student_dues(
                enrollment,
                today
            )

            return JsonResponse({

                "monthly_fee": float(
                    data["amount"]
                ),

                "fine": float(
                    data["fine"]
                ),

                "due_date":
                data["due_date"].strftime(
                    "%Y-%m-%d"
                ),

                "pending_months":
                data["pending_months"]

            })

        except CourseEnrollment.DoesNotExist:

            return JsonResponse(
                {"error":"Not found"},
                status=404
            )
        
    
    # ----------------------------
    # AUTO SELECT ENROLLMENT
    # ----------------------------
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        student_id = request.GET.get("student")

        if student_id:
            latest_enrollment = CourseEnrollment.objects.filter(
                student_id=student_id
            ).order_by("-admission_date").first()

            if latest_enrollment:
                initial["enrollment"] = latest_enrollment.id

                # Leave amount & due_date empty
                # JS autofill + AJAX will calculate correctly

        return initial

    # ----------------------------
    # ENROLLMENT DROPDOWN
    # ----------------------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enrollment":
            kwargs["queryset"] = CourseEnrollment.objects.select_related(
                "student", "course"
            ).all().order_by("-admission_date")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)



    # ----------------------------
    # INCLUDE JS
    # ----------------------------
    class Media:
        js = (
            "admin/js/fee_autofill.js",
            "admin/js/fee_enrollment_autofill.js",
            "admin/js/waive_fine.js",
        )






from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect

from .utils.certificate_email import send_certificate_email

@admin.register(Certificate)
class CertificateAdmin(FranchiseAdmin, SimpleHistoryAdmin):
    list_display = (
        "student",
        "completed_course",
        "end_date",
        "certificate_no",
        "marksheet_no",
        "upload_date",
        "published_at",
        "published_status",
        "email_sent",
        "resend_button",
    )
    actions = ["delete_selected_custom"]
    exclude = ("is_published", "certificate_prefix")
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "completed_course":
            student_id = request.GET.get("student")
            if student_id:
                kwargs["queryset"] = Course.objects.filter(
                    studentadmission__student_id=student_id
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    # readonly_fields = ("is_published",)
    def published_status(self, obj):
        return obj.is_published

    published_status.boolean = True
    published_status.short_description = "Is Published"

    from django.utils import timezone
    from django.utils.html import format_html

    def resend_button(self, obj):
        return format_html(
            '<a class="button" href="resend-email/{}/">Send Again</a>',
            obj.id
        )
    resend_button.short_description = "Resend Email"
    from django.urls import path
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        for cert in qs:

            enrollment = CourseEnrollment.objects.filter(
                student=cert.student,
                course=cert.completed_course,
                is_active=True
            ).first()

            if not enrollment:
                continue

            total_paid = (
                Fee.objects.filter(
                    enrollment=enrollment,
                    fee_type="MONTHLY"
                ).aggregate(total=Sum("amount"))["total"] or 0
            )

            remaining_fee = enrollment.total_fee - total_paid

            latest_fee = Fee.objects.filter(
                enrollment=enrollment
            ).order_by("-id").first()

            remaining_fine = latest_fee.remaining_fine if latest_fee else 0

            new_status = (
                remaining_fee == 0
                and remaining_fine == 0
                and cert.check_exam_completion()
            )

            if cert.is_published != new_status:
                cert.is_published = new_status
                cert.save(update_fields=["is_published"])

        return qs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'resend-email/<int:pk>/',
                self.admin_site.admin_view(self.resend_email)
            ),
        ]
        return custom_urls + urls

       # ⚠️ adjust if needed

    def resend_email(self, request, pk):

        obj = Certificate.objects.get(pk=pk)

        enrollment = CourseEnrollment.objects.filter(
            student=obj.student,
            course=obj.completed_course
        ).first()

        if enrollment:

            total_paid = (
                Fee.objects.filter(
                    enrollment=enrollment,
                    fee_type="MONTHLY"
                ).aggregate(
                    total=Sum("amount")
                )["total"] or 0
            )

            total_fine_paid = (
                Fee.objects.filter(
                    enrollment=enrollment
                ).aggregate(
                    total=Sum("fine")
                )["total"] or 0
            )

            remaining_fee = (
                enrollment.total_fee - total_paid
            )

            latest_fee = Fee.objects.filter(
                enrollment=enrollment
            ).order_by("-id").first()

            remaining_fine = 0

            if latest_fee:
                remaining_fine = (
                    latest_fee.remaining_fine or 0
                )

            if (
                remaining_fee > 0
                or remaining_fine > 0
            ):

                messages.error(

                    request,

                    f"Student still has pending dues. Remaining Fee: ₹{remaining_fee}, Remaining Fine: ₹{remaining_fine}"

                )

                return redirect(
                    request.META.get(
                        "HTTP_REFERER"
                    )
                )

        send_certificate_email(
            obj,
            force=True
        )

        messages.success(
            request,
            "✅ Email sent again successfully."
        )

        return redirect(
            request.META.get(
                "HTTP_REFERER"
            )
        )

    from student_portal.utils.certificate_email import send_certificate_email

    def save_model(self, request, obj, form, change):

        student = obj.student

        enrollment = CourseEnrollment.objects.filter(
            student=student,
            course=obj.completed_course,
            is_active=True
        ).first()

        if not enrollment:
            obj.is_published = False
            obj.published_at = None
            student.course_completed = False
            messages.error(request, "No active enrollment found.")

        else:

            total_paid = (
                Fee.objects
                .filter(
                    enrollment=enrollment,
                    fee_type="MONTHLY"
                )
                .aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

            remaining_fee = (
                enrollment.total_fee
                - total_paid
            )

            latest_fee = Fee.objects.filter(
                enrollment=enrollment
            ).order_by("-id").first()

            remaining_fine = 0

            if latest_fee:
                remaining_fine = (
                    latest_fee.remaining_fine or 0
                )
            exams_completed = obj.check_exam_completion()
            if (
                remaining_fee > 0
                or remaining_fine > 0
                or not exams_completed
            ):

                obj.is_published = False
                obj.published_at = None

                student.course_completed = False

                messages.warning(

                    request,

                    f"""Certificate uploaded but NOT published.

                Remaining Fee: ₹{remaining_fee}

                Remaining Fine: ₹{remaining_fine}

                
                """
                )

            else:

                obj.is_published = True

                if not obj.published_at:
                    obj.published_at = timezone.now()

                student.course_completed = True

                messages.success(
                    request,
                    "Certificate published successfully."
                )

                student.save(update_fields=["course_completed"])

        # ✅ SAVE FIRST (IMPORTANT)
        print("BEFORE SAVE:", obj.is_published)

        super().save_model(request, obj, form, change)

        print("AFTER SAVE:", obj.is_published)

        # 🔥 ADD THIS BLOCK (THIS IS THE FIX)
        # if obj.is_published and not obj.email_sent:
        #     try:
        #         send_certificate_email(obj)
        #     except Exception as e:
        #         print("❌ Email failed:", e)

        # from core.utils.email_tasks import send_certificate_email_async

        if obj.is_published and not obj.email_sent:
            db_alias = obj._state.db  # 🔥 IMPORTANT
            transaction.on_commit(
                lambda: send_certificate_email_async(obj.id, obj.franchise)
            )

    def get_fields(self, request, obj=None):

        fields = [
            "franchise",
            "student",
            "completed_course",
            "end_date",
            "certificate_no",
            "certificate_file",
            "marksheet_no",
            "marksheet_file",
        ]

        if obj:
            fields += ["email_sent", "email_error"]

        # 🔥 Remove franchise field for franchise users
        if not request.user.is_superuser:
            fields.remove("franchise")

        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("email_sent", "email_error")
        return ()

    def delete_selected_custom(self, request, queryset):
        from django.core.exceptions import ValidationError

        errors = []
        deleted = 0

        for obj in queryset:
            try:
                obj.delete()
                deleted += 1
            except ValidationError as e:
                errors.extend(e.messages)

        # 🔴 If ANY error → show ONLY error
        if errors:
            for err in errors:
                messages.error(request, err)
            return

        # ✅ Only success if no errors at all
        if deleted:
            messages.success(request, f"Successfully deleted {deleted} certificate(s).")


    def get_actions(self, request):
        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions



@admin.register(BatchDay)
class BatchDayAdmin(FranchiseAdmin, SimpleHistoryAdmin):
    pass



@admin.register(BatchTiming)
class BatchTimingAdmin(FranchiseAdmin, SimpleHistoryAdmin):
    pass

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(FranchiseAdmin):

    list_display = (
        "student_link",
        "name",
        "get_course",
        "get_course_fee",
        "get_total_paid",
        "get_remaining_fees",
        "get_all_receipts",
        "statement_button",
    )

    search_fields = ("name", "student_id")


    def get_course(self, obj):
        if obj.course:
            return obj.course.name
        return "-"
    get_course.short_description = "Course"


    def get_course_fee(self, obj):
        if obj.course:
            return f"Rs. {obj.course.total_fees}"
        return "-"
    get_course_fee.short_description = "Course Fees"


    # 🔒 Read only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # ✅ Total Paid
    

    list_display_links = None


    def student_link(self, obj):
        url = reverse(
            "admin:student_portal_paymenthistory_statement",
            args=[obj.id]
        )
        return format_html('<a href="{}">{}</a>', url, obj.student_id)

    student_link.short_description = "Student ID"


    def get_total_paid(self, obj):

        from .models import CourseEnrollment, Fee

        # obj IS the student (because proxy)
        student = obj

        # Get active enrollment
        enrollment = CourseEnrollment.objects.filter(
            student=student,
            is_active=True
        ).first()

        if not enrollment:
            return "Rs. 0"

        total = (
            Fee.objects
            .filter(enrollment=enrollment, fee_type="MONTHLY")
            .aggregate(total=Sum("amount"))
        )["total"] or 0

        return f"Rs. {total}"

    get_total_paid.short_description = "Total Paid (Monthly Only)"



    def get_remaining_fees(self, obj):
        from .models import CourseEnrollment, Fee

        student = obj

        # Get active enrollment
        enrollment = CourseEnrollment.objects.filter(
            student=student,
            is_active=True
        ).first()

        if not enrollment:
            return "Rs. 0"

        total_paid = (
            Fee.objects
            .filter(enrollment=enrollment, fee_type="MONTHLY")
            .aggregate(total=Sum("amount"))
        )["total"] or 0

        remaining = (enrollment.total_fee or 0) - total_paid

        return f"Rs. {remaining}"
        
    get_remaining_fees.short_description = "Remaining Fees"



    # ✅ All Receipts
    def get_all_receipts(self, obj):
        receipts = Fee.objects.filter(
            enrollment__student=obj
        ).values_list("receipt_no", flat=True)

        return ", ".join(receipts) if receipts else "No Receipts"

    get_all_receipts.short_description = "Receipts"

    # ✅ Statement Button

    def statement_button(self, obj):
        url = reverse(
            "admin:student_portal_paymenthistory_statement",
            args=[obj.id]
        ) + "?download=pdf"

        return format_html(
            '<a class="button" href="{}">Statement</a>',
            url
        )

    # 🔥 REGISTER CUSTOM ADMIN URL
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "statement/<int:student_id>/",
                self.admin_site.admin_view(self.student_fee_statement),
                name="student_portal_paymenthistory_statement",
            ),
        ]
        return custom_urls + urls

    # 🔥 Statement View
    def student_fee_statement(self, request, student_id):

        student = StudentAdmission.objects.get(id=student_id)

        admissions = StudentAdmission.objects.filter(
            student_id=student.student_id
        ).order_by("id")

        # 🔥 BUILD DATA FOR HTML
        course_data = []

        for admission in admissions:
            enrollments = CourseEnrollment.objects.filter(student=admission)

            # 🔥 GET ALL PAYMENTS
            all_payments = Fee.objects.filter(
                enrollment__in=enrollments
            ).order_by("payment_date")

            # ✅ SPLIT PAYMENTS
            admission_payments = all_payments.filter(fee_type="ADMISSION")
            course_payments = all_payments.exclude(fee_type="ADMISSION")

            # ✅ CALCULATIONS (ONLY COURSE FEES)
            total_paid = sum(p.amount or 0 for p in course_payments)
            total_fine = sum(p.fine or 0 for p in course_payments)
            # ✅ CALCULATE WAIVED FINE
            # ✅ CALCULATE WAIVED PROPERLY (PDF PART)
            total_waived = 0

            for p in course_payments:
                if p.waive_fine:
                    if p.waive_fine is True:
                        waived = p.fine or 0
                    else:
                        waived = p.waive_fine or 0
                else:
                    waived = 0

                total_waived += waived

            net_fine = total_fine - total_waived


            course_fee = admission.course.total_fees or 0

            course_data.append({
                "course": admission.course,
                "enrollment": admission,

                # 🔥 EXISTING
                "admission_payments": admission_payments,
                "payments": course_payments,

                "total_paid": total_paid,
                "total_fine": total_fine,

                # ✅ ADD THESE TWO
                "total_waived": total_waived,
                "net_fine": net_fine,

                # ✅ KEEP
                "remaining": course_fee - total_paid,
                "is_active": admission == admissions.last(),
            })

        overall_paid = sum(item["total_paid"] for item in course_data)
        overall_fine = sum(item["total_fine"] for item in course_data)

        context = {
            "student": student,
            "course_data": course_data,
            "overall_paid": overall_paid,
            "overall_fine": overall_fine,
            "grand_total": overall_paid + overall_fine,
        }

        # ✅ HTML VIEW (Student ID click)
        if request.GET.get("download") != "pdf":
            return render(
                request,
                "student_portal/student_statement.html",
                context
            )
        # p.showPage()
        # ================= PDF (NO CHANGE BELOW) =================

        # ================= PDF =================

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Statement_{student.student_id}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        logo_path = os.path.join(settings.BASE_DIR, "student_portal/static/logo.jpg")

        page_number = 1

        for admission in admissions:

            y = height - 120

            # ✅ VERY IMPORTANT (define here)
            enrollments = CourseEnrollment.objects.filter(student=admission)

            admission_fees = Fee.objects.filter(
                enrollment__in=enrollments,
                fee_type="ADMISSION"
            ).order_by("payment_date")

            course_fees = Fee.objects.filter(
                enrollment__in=enrollments
            ).exclude(fee_type="ADMISSION").order_by("payment_date")

            # ================= HEADER =================
            if os.path.exists(logo_path):
                p.drawImage(logo_path, 40, height-90, width=60, height=60)

            p.setFont("Helvetica-Bold", 18)
            p.drawCentredString(width/2, height-40, "SMART COMPUTER INSTITUTE")

            p.setFont("Helvetica", 10)
            p.drawCentredString(width/2, height-55, "Build Skills, Build Futures.....")

            p.line(110, height-70, width-40, height-70)

            p.setFont("Helvetica-Bold", 14)
            p.drawCentredString(width/2, height-90, "Payment Statement")

            # ================= STUDENT PHOTO =================
            photo_path = None

            if admission.passport_photo:
                photo_path = os.path.join(settings.MEDIA_ROOT, str(admission.passport_photo))

            if photo_path and os.path.exists(photo_path):
                p.drawImage(
                    photo_path,
                    width - 120,   # right side
                    height - 210,  # adjust vertical
                    width=80,
                    height=100
                )



            # ================= STUDENT DETAILS =================
            p.setFont("Helvetica-Bold", 12)
            p.drawString(40, y, "STUDENT DETAILS")
            y -= 20

            p.setFont("Helvetica", 10)

            status = "Current Course" if admission == admissions.last() else "Previous Course (Upgraded)"

            details = [
                f"Status: {status}",
                f"Student ID: {admission.student_id}",
                f"Name: {admission.name}",
                f"Course: {admission.course.name}",
                f"Admission Date: {admission.admission_date}",
                f"Course Type: {admission.course_type}",
                f"Total Course Fee: Rs. {admission.course.total_fees}",
            ]

            for line in details:
                p.drawString(40, y, line)
                y -= 15

            y -= 10

            # ================= ADMISSION TABLE =================
            p.setFont("Helvetica-Bold", 12)
            p.drawString(40, y, "Admission Payment")
            y -= 15

            admission_data = [["Sl No", "Date", "Receipt No", "Type", "Amount", "Discount", "Final Amount"]]

            for i, fee in enumerate(admission_fees, start=1):

                amount = fee.amount or 0

                discount = admission.discount_percent or 0

                discount_amount = (amount * discount / 100) if discount else 0
                final_amount = amount - discount_amount

                admission_data.append([
                    i,
                    str(fee.payment_date),
                    fee.receipt_no,
                    fee.fee_type,
                    f"Rs. {amount:.2f}",
                    f"{int(discount)}%" if discount else "-",
                    f"Rs. {final_amount:.2f}",
                ])

            if len(admission_data) == 1:
                admission_data.append(["-", "-", "No Admission Payment"])

            admission_table = Table(admission_data, colWidths=[40, 70, 70, 70, 70, 70, 80])
            admission_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))

            admission_table.wrapOn(p, width - 80, height)
            table_height = admission_table._height
            admission_table.drawOn(p, 40, y - table_height)

            y = y - table_height - 25

            # ================= COURSE TABLE =================
            p.setFont("Helvetica-Bold", 12)
            p.drawString(40, y, "Course Payments")
            y -= 15

            data = [["Sl No", "Due Date", "Receipt No", "Payment Date", "Fine", "Waive Fine", "Amount"]]

            total_received = 0
            total_fine = 0
            total_waived = 0

            for i, fee in enumerate(course_fees, start=1):

                total_received += fee.amount or 0
                total_fine += fee.fine or 0

                # ✅ waive display
                if fee.waive_fine:
                    if fee.waive_fine is True:
                        waived = fee.fine or 0
                        waive_display = f"Rs. {fee.fine}"
                    else:
                        waived = fee.waive_fine or 0
                        waive_display = f"Rs. {fee.waive_fine}"
                else:
                    waived = 0
                    waive_display = "-"

                total_waived += waived

                data.append([
                    i,
                    str(fee.due_date),
                    fee.receipt_no,
                    str(fee.payment_date),
                    f"Rs. {fee.fine or 0}",
                    waive_display,
                    f"Rs. {fee.amount or 0}",
                ])

            table = Table(data, colWidths=[40, 70, 70, 70, 50, 60, 70], repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))

            table.wrapOn(p, width - 80, height)
            table_height = table._height
            table.drawOn(p, 40, y - table_height)

            y = y - table_height - 25

            # ================= SUMMARY =================
            net_fine = total_fine - total_waived
            total_course_fee = admission.course.total_fees or 0

            p.setFont("Helvetica-Bold", 11)

            p.drawString(40, y, f"Total Received: Rs. {total_received}")
            y -= 15

            if total_waived == 0:
                fine_text = f"Total Fine: Rs. {total_fine:.2f}"
            elif total_waived == total_fine:
                fine_text = f"Total Fine: Rs. {total_fine:.2f} (Fully Waived)"
            else:
                fine_text = f"Total Fine: Rs. {net_fine:.2f} (Rs. {total_waived:.2f} Waived)"

            p.drawString(40, y, fine_text)
            y -= 15

            remaining = total_course_fee + net_fine - total_received
            p.drawString(40, y, f"Remaining: Rs. {remaining}")

            # ================= FOOTER =================
            signature_path = None

            franchise = getattr(student, "franchise", None)

            if franchise and franchise.signature:
                try:
                    signature_path = franchise.signature.path
                except:
                    signature_path = None

            if signature_path and os.path.exists(signature_path):
                try:
                    from PIL import Image

                    img = Image.open(signature_path)
                    orig_w, orig_h = img.size

                    target_w = 140
                    scale = target_w / orig_w
                    new_h = orig_h * scale

                    p.drawImage(
                        signature_path,
                        width - 190,
                        -10 - new_h + 5,   # 👈 aligned just above your line
                        width=target_w,
                        preserveAspectRatio=True,
                        mask='auto'
                    )

                except Exception as e:
                    print("Signature draw error:", e)


            # Signature & Footer
            # p.drawRightString(width-40, footer_y - -15, "Authorized Signatory")
            p.line(width - 200, 65, width - 50, 65)
            p.setFont("Helvetica-Oblique", 11)
            p.drawRightString(width - 50, 55, "Authorized Signatory")
        

            timestamp = datetime.now().strftime("%d-%m-%Y | %I:%M %p")

            p.setFont("Helvetica", 9)
            p.drawString(40, 45, f"Generated on: {timestamp}")

            p.setStrokeColorRGB(0, 0, 0); p.line(40, 35, 550, 35)
            p.setFont("Helvetica", 9); p.saveState(); p.setFillAlpha(0.6)
            p.drawString(40, 25, "SMART COMPUTER INSTITUTE"); p.restoreState()
            p.drawRightString(550, 25, f"Page | {page_number}")
            page_number += 1
            
            p.showPage()
            # ; p.save()
            # return response

        p.save()
        return response
            

# @admin.register(StudentAdmission)
# class StudentAdmissionAdmin(FranchiseAdmin):
#     list_display = ("student_name", "course", "class_day", "class_timing")
#     list_filter = ("class_day", "class_timing")

# class BatchList(StudentAdmission):
#     class Meta:
#         proxy = True
#         verbose_name = "Batch List"
#         verbose_name_plural = "Batch Lists"

from .models import BatchTiming, StudentAdmission

@admin.register(BatchListView)
class BatchListAdmin(FranchiseAdmin):

    change_list_template = "admin/student_portal/batchlistview/batch_list.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        franchise = getattr(request.user, "franchise", None)

        if franchise:
            return qs.filter(franchise=franchise)

        return qs.none()

    def changelist_view(self, request, extra_context=None):

        count = int(request.GET.get("count", 6))

        days = BatchDay.objects.all().order_by("id")
        times = BatchTiming.objects.all().order_by("id")

        students = {}

        for d in days:
            students[d.id] = {}

            for t in times:
                students[d.id][t.id] = StudentAdmission.objects.filter(
                    class_day=d,
                    class_time=t,
                    is_active=True,
                    is_freezed=False,        # 👈 add this
                    course_completed=False
                ).order_by("student_id")

        context = {
            **self.admin_site.each_context(request),
            "days": days,
            "times": times,
            "students": students,
            "count": count,
            "range": range(1, count + 1),
        }

        return render(
            request,
            "admin/student_portal/batchlistview/batch_list.html",
            context
        )
    
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

class CustomAdminSite(admin.AdminSite):
    site_header = "Admin Panel"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path('change-email/', self.admin_view(self.change_email))
        ]

        return custom_urls + urls

    def change_email(self, request):
        return redirect('/franchiseaccount/')  # your page


admin_site = CustomAdminSite(name='custom_admin')

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(FranchiseAdmin, SimpleHistoryAdmin):

    search_fields = [
        "student__name",
        "student__student_id",
        "course__name",
    ]

    def has_module_permission(self, request):
        return False