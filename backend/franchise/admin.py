# ===================== IMPORTS =====================
from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth import update_session_auth_hash
import random, json

from .models import Franchise, FranchiseAccount


# ===================== FORM =====================

class FranchiseForm(forms.ModelForm):

    username = forms.CharField(widget=forms.TextInput(attrs={
        "autocomplete": "new-username",
        "autocorrect": "off",
        "spellcheck": "false"
    }))

    password = forms.CharField(required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    class Meta:
        model = Franchise
        fields = (
            "manager_name","passport_photo","id_proof_number",
            "institute_name","trade_license_number","institute_location",
            "id_proof_file", "signature","email","username","password", 
            "student_id_part1",
            "student_id_part2",
            "student_id_part3",
        )

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if self.instance.pk and not username:
            return self.instance.user.username

        if self.instance.pk and self.instance.user:
            if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
                raise forms.ValidationError("Username exists")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Username exists")

        return username
    def clean(self):

        cleaned_data = super().clean()

        verified = False

        request = getattr(
            self.__class__,
            "request",
            None
        )

        if request:

            verified = request.session.get(
                "email_verified",
                False
            )

        # Fields that never need OTP
        ignore_fields = [

            "password",
            "username",

        ]

        changed = False

        # ================= EDIT PAGE =================

        if self.instance and self.instance.pk:

            for field in self.changed_data:

                if field not in ignore_fields:

                    changed = True
                    break

        # ================= ADD PAGE =================

        else:

            for field, value in cleaned_data.items():

                if (

                    field not in ignore_fields
                    and value

                ):

                    changed = True
                    break

        # Save state for save_model()
        self._otp_required_for_save = changed

        if changed and not verified:

            raise forms.ValidationError(

                "Verify OTP before saving changes."

            )

        return cleaned_data

    def save(self, commit=True):
        franchise = super().save(commit=False)
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if commit:
            franchise.save()

            if franchise.user:
                user = franchise.user
                if username and username != user.username:
                    user.username = username
                user.save()
            else:
                user = User.objects.create_user(
                    username=username,
                    email=franchise.email,
                    password=password,
                    is_staff=True
                )
                franchise.user = user
                franchise.save()

        return franchise


# ===================== ADMIN =====================

from django.utils.html import format_html



@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    form = FranchiseForm

    def get_form(self, request, obj=None, **kwargs):

        kwargs["form"] = self.form

        Form = super().get_form(
            request,
            obj,
            **kwargs
        )

        # attach request safely
        Form.request = request

        # preload username on edit page
        old_init = Form.__init__

        def new_init(
            self,
            *args,
            **form_kwargs
        ):

            old_init(
                self,
                *args,
                **form_kwargs
            )

            if (
                self.instance
                and self.instance.pk
                and self.instance.user
                and "username" in self.fields
            ):

                self.fields[
                    "username"
                ].initial = (
                    self.instance.user.username
                )

        Form.__init__ = new_init

        return Form


    fields = (
        "manager_name",
        "passport_photo",
        "id_proof_number",
        "institute_name",
        "trade_license_number",
        "institute_location",
        "id_proof_file",
        "signature",
        "email",
        "username",
        "password",

        "student_id_combined",  # 👈 use this instead
    )

    readonly_fields = ("student_id_combined",)

    def student_id_combined(self, obj=None):
        return format_html(
            '<input type="text" name="student_id_part1" value="{}" style="width:60px;"> '
            '<input type="text" name="student_id_part2" value="{}" style="width:60px;"> '
            '<input type="text" name="student_id_part3" value="{}" style="width:80px;">',
            obj.student_id_part1 if obj else "MG",
            obj.student_id_part2 if obj else "SLG",
            obj.student_id_part3 if obj else "",
        )

    student_id_combined.short_description = "Student ID"


    list_display = (
        "manager_name",
        "institute_name",
        "id_proof_number",
        "get_username",
        "is_restricted_toggle",
    )

    class Media:
        css = {
            "all": ("admin/css/custom.css",)
        }
        js = (
            "js/image_preview.js",
            "franchise/js/restrict_instant.js",
        )

    def get_username(self, obj):
        return obj.user.username if obj.user else "-"
    get_username.short_description = "Username"

    # 🔥 KEEP YOUR DESIGN EXACT
    def is_restricted_toggle(self, obj):
        checked = "checked" if obj.is_restricted else ""
        return mark_safe(f'''
            <input type="checkbox" class="auto-toggle-restriction"
                   data-id="{obj.pk}" {checked}
                   style="width:20px;height:20px;cursor:pointer;">
        ''')
    is_restricted_toggle.short_description = "Is Restricted"

    # ================= URLS =================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ajax-toggle-restriction/<int:pk>/',
                 self.admin_site.admin_view(self.toggle_restriction_view),
                 name='ajax_toggle_restriction'),

            path('send-franchise-otp/',
                 self.admin_site.admin_view(self.send_franchise_otp_view),
                 name="send_franchise_otp"),

            path('verify-franchise-otp/',
                 self.admin_site.admin_view(self.verify_franchise_otp_view),
                 name="verify_franchise_otp"),
        ]
        return custom_urls + urls

    # ================= TOGGLE =================
    def toggle_restriction_view(self, request, pk):
        if request.method == "POST":
            try:
                obj = Franchise.objects.get(pk=pk)
                obj.is_restricted = not obj.is_restricted
                obj.save()

                return JsonResponse({
                    "status": "success",
                    "new_state": obj.is_restricted
                })

            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})

        return JsonResponse({"status": "error"})

    # ================= OTP =================
    def send_franchise_otp_view(self, request):
        email = request.GET.get("email")
        otp = str(random.randint(100000, 999999))

        request.session["franchise_email_otp"] = otp

        send_mail(
            "Email Verification",
            f"Your OTP is {otp}",
            "smartcomputerins2022@gmail.com",
            [email],
        )
        return JsonResponse({"status": "sent"})

    def verify_franchise_otp_view(self, request):
        data = json.loads(request.body)
        if data.get("otp") == request.session.get("franchise_email_otp"):
            request.session["email_verified"] = True
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "failed"})

    # ================= SAVE =================
    def save_model(self, request, obj, form, change):

        # ================= STUDENT ID SETTINGS =================
        # Save custom Student ID prefix + starting number

        obj.student_id_part1 = (
            request.POST.get(
                "student_id_part1"
            ) or "MG"
        )

        obj.student_id_part2 = (
            request.POST.get(
                "student_id_part2"
            ) or "SLG"
        )

        obj.student_id_part3 = (
            str(
                request.POST.get(
                    "student_id_part3"
                ) or "1"
            ).zfill(4)
        )

        # ================= EXISTING LOGIC =================

        username = form.cleaned_data.get(
            "username"
        )

        password = form.cleaned_data.get(
            "password"
        )

        if obj.user:

            user = obj.user

            if username:
                user.username = username
            if obj.email:
                user.email = obj.email
            # password only = no OTP needed
            if password:
                user.set_password(password)

            user.save()

        else:

            user = User.objects.create_user(
                username=username,
                email=obj.email,
                password=password,
                is_staff=True
            )

            obj.user = user

        super().save_model(
            request,
            obj,
            form,
            change
        )

        # ================= OTP CLEANUP =================

        if getattr(
            form,
            "_otp_required_for_save",
            False
        ):

            request.session.pop(
                "email_verified",
                None
            )

            request.session.modified = True


# ===================== ACCOUNT =====================

@admin.register(FranchiseAccount)
class FranchiseAccountAdmin(admin.ModelAdmin):

    change_list_template = (
        "admin/access_portal.html"
    )

    list_display = (
        "franchise",
    )

    # ================= SHOW MODULE =================

    def has_module_permission(
        self,
        request
    ):
        return request.user.is_staff

    def has_view_permission(
        self,
        request,
        obj=None
    ):
        return request.user.is_staff

    def has_add_permission(
        self,
        request
    ):
        return request.user.is_staff

    def has_change_permission(
        self,
        request,
        obj=None
    ):
        return request.user.is_staff

    # ================= FILTER =================

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
            franchise__user=request.user
        )

    # ================= ACCESS SETTINGS =================

    def access_settings(
        self,
        request
    ):

        if request.method == "POST":

            if (
                "change_username"
                in request.POST
            ):

                request.user.username = (
                    request.POST.get(
                        "username"
                    )
                )

                request.user.save()

            if (
                "change_password"
                in request.POST
            ):

                request.user.set_password(
                    request.POST.get(
                        "password"
                    )
                )

                request.user.save()

                update_session_auth_hash(
                    request,
                    request.user
                )

        return render(
            request,
            "admin/access_portal.html",
            {
                "username":
                request.user.username,

                "email":
                request.user.email,
            }
        )

# ===================== OTP GLOBAL =====================

@login_required
def send_account_change_otp(request):
    otp = str(random.randint(100000, 999999))
    request.session["account_change_otp"] = otp

    send_mail(
        "Account Change OTP",
        f"OTP: {otp}",
        "smartcomputerins2022@gmail.com",
        [request.user.email],
    )

    return JsonResponse({"status": "sent"})


@login_required
def verify_account_change(request):

    otp = request.POST.get("otp")

    if otp != request.session.get("account_change_otp"):
        return JsonResponse({"status": "invalid"})

    user = request.user

    if request.POST.get("username"):
        user.username = request.POST.get("username")

    if request.POST.get("password"):
        user.set_password(request.POST.get("password"))
        user.save()
        update_session_auth_hash(request, user)

    return JsonResponse({"status": "updated"})