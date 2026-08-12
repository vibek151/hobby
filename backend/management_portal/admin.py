
from urllib import request
from .models import NoticeHidden
from django.contrib import admin
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import path, reverse
import threading
from django.db.models import Q
from .models import Notice
from student_portal.models import StudentAdmission
from student_portal.notifications import send_student_email
from concurrent.futures import ThreadPoolExecutor
from django.utils.html import format_html
from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Exam, StudentMarks
from django.http import JsonResponse
from django.urls import path
# ================= BACKGROUND FUNCTION =================


def send_notice_async(notice):

    # Decide recipients
    if notice.students.exists():

        recipients = notice.students.all()

    elif notice.franchise:

        # Superuser selected a franchise
        # OR franchise user (franchise assigned automatically)
        recipients = StudentAdmission._base_manager.filter(
            franchise=notice.franchise
        )

    else:

        # Superuser left franchise blank
        recipients = StudentAdmission._base_manager.all()

    # Email sending
    def send_email(student):

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

    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        executor.map(
            send_email,
            recipients
        )

    notice.is_sent = True
    notice.sent_at = timezone.now()

    notice.save(
        update_fields=[
            "is_sent",
            "sent_at"
        ]
    )
class NoticeForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        required=False,
        input_formats=[
            "%Y-%m-%d %I:%M %p",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ],
        widget=forms.DateTimeInput(
            format="%Y-%m-%d %I:%M %p",
            attrs={
                "class": "flatpickr"
            }
        )
    )

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")

        if data is not None and "students" in data:
            data = data.copy()

            if hasattr(data, "getlist") and hasattr(data, "setlist"):
                students = [value for value in data.getlist("students") if value]
                data.setlist("students", students)
            elif not isinstance(data.get("students"), (list, tuple)):
                student = data.get("students")
                data["students"] = [student] if student else []

            kwargs["data"] = data

        super().__init__(*args, **kwargs)

    class Meta:
        model = Notice
        fields = "__all__"

    def clean(self):

        cleaned_data = super().clean()

        # Franchise users don't need to select a franchise.
        if self.instance.pk:
            return cleaned_data

        return cleaned_data


# ================= ADMIN CONFIG =================

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "show_sent_time",
        "show_scheduled_time",
        "send_status",
        "delete_notice",
        "sent_by",
    )



    change_form_template = "admin/notice_form.html"
    fields = (
        "franchise",
        ("title", "students"),
        "body",
        "scheduled_time",
        "sent_at",
        "is_sent",
    )
    readonly_fields = ("is_sent", "sent_at")
    actions = ["delete_selected"]
    form = NoticeForm
    # 👇 ADD ONLY THIS BLOCK
    def get_form(self, request, obj=None, **kwargs):

        form = super().get_form(
            request,
            obj,
            **kwargs
        )

        # hide for franchise accounts
        if not request.user.is_superuser:

            if "franchise" in form.base_fields:
                del form.base_fields["franchise"]

        # edit page lock
        if obj:

            readonly = [
                "title",
                "students",
                "body",
            ]

            for field in readonly:

                if field in form.base_fields:
                    form.base_fields[field].disabled = True

        return form
    





    
    search_fields = (
        "title",
        "created_at",
        "scheduled_time",
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        if request.user.is_superuser:

            obj.sender_id = "superuser"

            # Franchise may be blank.
            obj.franchise = form.cleaned_data.get("franchise")

        else:

            obj.sender_id = request.user.username

            obj.franchise = request.user.franchise

        super().save_model(
            request,
            obj,
            form,
            change
        )

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        hidden_ids = NoticeHidden.objects.filter(
            franchise_user=request.user.username
        ).values_list(
            "notice_id",
            flat=True
        )

        return qs.exclude(
            id__in=hidden_ids
        ).filter(
            Q(sender_id=request.user.username) |
            Q(sender_id="superuser")
        )
    
    def delete_model(
        self,
        request,
        obj
    ):

        # Superuser = real delete
        if request.user.is_superuser:

            super().delete_model(
                request,
                obj
            )

            return

        # Franchise own notice = real delete
        if obj.sender_id == request.user.username:

            super().delete_model(
                request,
                obj
            )

            return

        # Superuser notice = hide only
        NoticeHidden.objects.get_or_create(
            notice=obj,
            franchise_user=request.user.username
        )

    

    def response_change(
        self,
        request,
        obj
    ):

        # remove all success messages
        list(messages.get_messages(request))

        return HttpResponseRedirect(
            "/admin/management_portal/notice/"
        )


    def render_change_form(
        self,
        request,
        context,
        *args,
        **kwargs
    ):

        context["subtitle"] = ""

        return super().render_change_form(
            request,
            context,
            *args,
            **kwargs
        )

    def has_delete_permission(
        self,
        request,
        obj=None
    ):

        if obj is None:
            return True

        # Superuser
        if request.user.is_superuser:

            # can delete any pending notice
            return True

        # Franchise

        # own notice
        if obj.sender_id == request.user.username:
            return True

        # superuser notice
        if obj.sender_id == "superuser":
            return True

        return False



    def sent_by(self, obj):

        request = getattr(
            self,
            "request",
            None
        )

        if not request:
            return "-"

        sender = str(obj.sender_id).strip()

        # SUPERUSER VIEW
        if request.user.is_superuser:

            # own notice
            if sender == "superuser":
                return "👤 You"

            # franchise notice
            return f"🏢 {sender}"

        # FRANCHISE VIEW
        else:

            # own notice
            if sender == request.user.username:
                return "👤 You"

            # notice from superuser
            if sender == "superuser":
                return "⭐ Superuser"

            return f"🏢 {sender}"


    def changelist_view(
        self,
        request,
        extra_context=None
    ):

        self.request = request

        return super().changelist_view(
            request,
            extra_context=extra_context
        )

    def get_list_display(self, request):
        return (
            "title",
            "show_sent_time",
            "show_scheduled_time",
            "send_status",
            "delete_notice",
            "sent_by",
        )


    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    # ✅ Show only incomplete students in selection
    
    def show_scheduled_time(self, obj):

        if (
            obj.scheduled_time and
            obj.created_at and
            obj.scheduled_time > obj.created_at
        ):

            return timezone.localtime(
                obj.scheduled_time
            ).strftime(
                "%d-%m-%Y %I:%M %p"
            )

        return "-"

    show_scheduled_time.short_description = "Scheduled"
    show_scheduled_time.admin_order_field = "scheduled_time"

    def show_sent_time(self, obj):

        if obj.created_at:
            return timezone.localtime(
                obj.created_at
            ).strftime(
                "%d-%m-%Y %I:%M %p"
            )

        return "-"

 
    show_sent_time.short_description = "Sent Time"
   
    show_sent_time.admin_order_field = "sent_at"

    def show_rescheduled(self, obj):

        return "-"

    show_rescheduled.short_description = "Rescheduled"

    def send_status(self, obj):

        return "✓ Sent" if obj.is_sent else "⏳ Pending"

    send_status.short_description = "Status"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "students":

            qs = StudentAdmission.objects.filter(course_completed=False)

            if request.resolver_match.kwargs.get("object_id"):
                obj_id = request.resolver_match.kwargs.get("object_id")
                notice = Notice.objects.get(pk=obj_id)

                qs = StudentAdmission.objects.filter(
                    Q(course_completed=False) |
                    Q(id__in=notice.students.values_list("id", flat=True))
                )

            kwargs["queryset"] = qs

        return super().formfield_for_manytomany(db_field, request, **kwargs)
    def delete_notice(self, obj):

        if not obj.is_sent:

            return format_html(
                '<a style="color:red;font-weight:bold;" href="/admin/management_portal/notice/{}/delete/">🗑 Delete</a>',
                obj.id
            )

        return "-"

    # delete_notice.short_description = "Delete"
    # ================= SINGLE SEND =================
    def send_notice(self, request, pk):
        notice = Notice.objects.get(pk=pk)

        if notice.is_sent:
            self.message_user(request, "This notice has already been sent.")
            return redirect("admin:management_portal_notice_changelist")

        if notice.scheduled_time and notice.scheduled_time > timezone.now():
            self.message_user(request, "Notice saved and will be sent at the scheduled time.")
            return redirect("admin:management_portal_notice_changelist")

        # 🔥 Run sending in background
        threading.Thread(
            target=send_notice_async,
            args=(notice,),
            daemon=True
        ).start()

        # ⚡ Instant redirect
        self.message_user(request, "Notice is being sent in background.")
        return redirect("admin:management_portal_notice_changelist")

    # ================= CUSTOM URL =================
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "send/<int:pk>/",
                self.admin_site.admin_view(self.send_notice),
                name="management_portal_notice_send"
            ),
        ]
        return custom + urls

    # ================= BULK ACTION =================
    def send_to_all_incomplete(self, request, queryset):
        total = 0

        for notice in queryset:
            if notice.is_sent:
                continue

            # 🔥 Background send
            threading.Thread(
                target=send_notice_async,
                args=(notice,),
                daemon=True
            ).start()
            total += 1

        self.message_user(request, f"{total} notices are being sent in background.")

    # ================= REDIRECT AFTER SAVE =================
    def should_send_now(self, obj):
        return not obj.scheduled_time or obj.scheduled_time <= timezone.now()

    def response_add(self, request, obj, post_url_continue=None):
        if "_save" in request.POST:
            if not self.should_send_now(obj):
                self.message_user(request, "Notice saved and will be sent at the scheduled time.")
                return redirect("admin:management_portal_notice_changelist")

            return redirect(reverse('admin:management_portal_notice_send', args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if "_save" in request.POST:
            if not self.should_send_now(obj):
                self.message_user(request, "Notice saved and will be sent at the scheduled time.")
                return redirect("admin:management_portal_notice_changelist")

            return redirect(reverse('admin:management_portal_notice_send', args=[obj.pk]))
        return super().response_change(request, obj)

    class Media:

        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css",
            )
        }

        js = (
            "https://cdn.jsdelivr.net/npm/flatpickr",
            "admin/js/notice_timepicker.js",
        )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "exam_name",
        "franchise",
        "total_marks",
    )


    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff


    search_fields = (
        "exam_name",
    )


    def get_queryset(
        self,
        request
    ):

        qs = super().get_queryset(
            request
        )

        if request.user.is_superuser:
            return qs

        return qs.filter(
            franchise=request.user.franchise
        )


    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        if not request.user.is_superuser:

            obj.franchise = (
                request.user.franchise
            )

        super().save_model(
            request,
            obj,
            form,
            change
        )


    def get_form(
        self,
        request,
        obj=None,
        **kwargs
    ):

        form = super().get_form(
            request,
            obj,
            **kwargs
        )

        if (
            not request.user.is_superuser
            and
            "franchise" in form.base_fields
        ):

            del form.base_fields[
                "franchise"
            ]

        return form
    
@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "exam",
        "marks",
    )

    def get_form(
        self,
        request,
        obj=None,
        **kwargs
    ):

        form = super().get_form(
            request,
            obj,
            **kwargs
        )

        # Franchise user → hide field
        if not request.user.is_superuser:

            form.base_fields.pop(
                "franchise",
                None
            )

        return form

    def get_model_perms(
        self,
        request
    ):

        return {
            "add": True,
            "change": True,
            "delete": True,
            "view": True,
        }

    


    def get_urls(self):

        urls = super().get_urls()

        custom = [

            path(
                "students-by-franchise/",
                self.admin_site.admin_view(
                    self.students_by_franchise
                )
            ),
        ]

        return custom + urls


    def students_by_franchise(
        self,
        request
    ):

        franchise_id = request.GET.get(
            "franchise"
        )

        data = []

        students = StudentAdmission.objects.filter(
            franchise_id=franchise_id
        )

        for x in students:

            data.append({

                "id": x.id,
                "name": str(x)

            })

        return JsonResponse(
            data,
            safe=False
        )





    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        # franchise login
        if not request.user.is_superuser:

            obj.franchise = (
                request.user.franchise
            )

        # superuser uses selected franchise from form
        else:

            obj.franchise = form.cleaned_data.get(
                "franchise"
            )

        super().save_model(
            request,
            obj,
            form,
            change
        )

    def get_changeform_initial_data(
        self,
        request
    ):

        if not request.user.is_superuser:

            return {
                "franchise":
                request.user.franchise.id
            }

        return {}



    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        # STUDENTS
        if db_field.name == "student":

            qs = StudentAdmission.objects.all()

            if not request.user.is_superuser:

                qs = qs.filter(
                    franchise=request.user.franchise
                )

            kwargs["queryset"] = qs


        # EXAMS
        if db_field.name == "exam":

            qs = Exam.objects.all()

            if not request.user.is_superuser:

                qs = qs.filter(
                    franchise=request.user.franchise
                )

            kwargs["queryset"] = qs


        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


    def get_queryset(
        self,
        request
    ):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(
            request.user,
            "franchise"
        ):

            return qs.filter(
                franchise=request.user.franchise
            )

        return qs.none()
    
    def has_module_permission(
        self,
        request
    ):
        return True


    def has_view_permission(
        self,
        request,
        obj=None
    ):
        return True


    def has_add_permission(
        self,
        request
    ):
        return True


    def has_change_permission(
        self,
        request,
        obj=None
    ):
        return True
    
    def has_delete_permission(
        self,
        request,
        obj=None
    ):
        return True
    
    class Media:
        js = (
            "admin/js/student_marks.js",
        )


from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "course",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "course",
    )

    search_fields = (
        "name",
        "phone",
        "email",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )