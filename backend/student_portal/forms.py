# from django import forms
# from .models import Fee
# from .models import StudentAdmission
# from .widgets import SimpleFileInput
# from datetime import date
# from django.core.exceptions import ValidationError
# from django.contrib.admin.widgets import AdminDateWidget

# from django import forms
# from datetime import date
# from django.core.exceptions import ValidationError
# from .models import StudentAdmission

# class FeeForm(forms.ModelForm):
#     class Meta:
#         model = Fee
#         fields = "__all__"
#         widgets = {
#             "timestamp": forms.TextInput(attrs={"class": "flatpickr"}),
#         }
# # class StudentAdmissionForm(forms.ModelForm):

# #     class Meta:
# #         model = StudentAdmission
# #         fields = "__all__"
# #         widgets = {
# #             "passport_photo": SimpleFileInput,
# #             "last_qualification_file": SimpleFileInput,
# #             "document_file": SimpleFileInput,
# #         }

# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)

# #         # Only course fields editable in upgrade
# #         editable_fields = [
# #             "course",
# #             "course_type",
# #             "course_duration",
# #             "class_time",
# #             "class_day",
# #         ]

# #         for name, field in self.fields.items():
# #             if name not in editable_fields:
# #                 field.widget.attrs["readonly"] = True
# #                 field.widget.attrs["disabled"] = True
# #                 field.widget.attrs["style"] = "background:#f5f5f5;"



# class StudentAdmissionForm(forms.ModelForm):

#     class Meta:
#         model = StudentAdmission
#         fields = "__all__"
#         widgets = {
#             "dob": forms.DateInput(attrs={"type": "date"}),
#             "admission_date": forms.DateInput(attrs={"type": "date"}),
#         }

#     # =========================
#     # DOB VALIDATION
#     # =========================
#     def clean_dob(self):
#         dob = self.cleaned_data.get("dob")

#         if dob and dob > date.today():
#             raise ValidationError("DOB cannot be future date.")

#         return dob

#     # =========================
#     # ADMISSION DATE VALIDATION
#     # =========================
#     def clean_admission_date(self):
#         adate = self.cleaned_data.get("admission_date")

#         if adate and adate > date.today():
#             raise ValidationError("Admission date cannot be future.")

#         return adate
    
#     def clean_phone(self):
#         phone = self.cleaned_data.get("phone")

#         if phone:
#             if not phone.isdigit():
#                 raise ValidationError("Digits only.")

#             if len(phone) != 10:
#                 raise ValidationError("Must be 10 digits.")

#         return phone
    
#     def clean_document_number(self):
#         doc_type = self.cleaned_data.get("document_type")
#         number = self.cleaned_data.get("document_number")

#         if doc_type == "AADHAAR":
#             if not number:
#                 raise ValidationError("Aadhaar number is required.")

#             if not number.isdigit():
#                 raise ValidationError("Aadhaar must contain only digits.")

#             if len(number) != 12:
#                 raise ValidationError("Aadhaar must be exactly 12 digits.")

#         return number


    

#     def clean_receipt_no(self):
#         receipt = self.cleaned_data.get("receipt_no")

#         if receipt:
#             if not receipt.isdigit():
#                 raise ValidationError("Receipt number must contain only numbers.")

#         return receipt
    

    
from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from .models import Fee, StudentAdmission


# =========================
# FEE FORM
# =========================
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = "__all__"
        widgets = {
            "timestamp": forms.TextInput(attrs={"class": "flatpickr"}),
        }


# =========================
# STUDENT ADMISSION FORM
# =========================
class StudentAdmissionForm(forms.ModelForm):

    class Meta:
        model = StudentAdmission
        fields = "__all__"
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "admission_date": forms.DateInput(attrs={"type": "date"}),
        }

    # -------------------------
    # DOB VALIDATION
    # -------------------------
    def clean_dob(self):
        dob = self.cleaned_data.get("dob")

        if dob and dob > date.today():
            raise ValidationError("DOB cannot be a future date.")

        return dob

    # -------------------------
    # ADMISSION DATE VALIDATION
    # -------------------------
    def clean_admission_date(self):
        adate = self.cleaned_data.get("admission_date")

        if adate and adate > date.today():
            raise ValidationError("Admission date cannot be future.")

        return adate

    # -------------------------
    # PHONE VALIDATION
    # -------------------------
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if phone:
            if not phone.isdigit():
                raise ValidationError("Phone number must contain digits only.")

            if len(phone) != 10:
                raise ValidationError("Phone number must be exactly 10 digits.")

            # Prevent duplicate phone (excluding self during edit)
            # if StudentAdmission.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            #     raise ValidationError("This phone number is already registered.")

        return phone

    # -------------------------
    # RECEIPT NUMBER VALIDATION
    # -------------------------
    def clean_receipt_no(self):
        receipt = self.cleaned_data.get("receipt_no")

        if receipt:
            if not receipt.isdigit():
                raise ValidationError("Receipt number must contain only numbers.")

        return receipt

    # -------------------------
    # MULTI-FIELD VALIDATION
    # -------------------------
    # def clean(self):
    #     cleaned_data = super().clean()
    #     doc_type = cleaned_data.get("document_type")
    #     number = cleaned_data.get("document_number")

    #     # Only validate when Aadhaar selected
    #     if doc_type and doc_type.upper() == "AADHAAR":

    #         # Required check
    #         if not number:
    #             self.add_error("document_number", "Aadhaar number is required.")
    #             return cleaned_data

    #         # Strip spaces (important)
    #         number = str(number).strip()

    #         # Numeric check
    #         if not number.isdigit():
    #             self.add_error("document_number", "Aadhaar must contain digits only.")
    #             return cleaned_data

    #         # Length check
    #         if len(number) != 12:
    #             self.add_error("document_number", "Aadhaar must be exactly 12 digits.")
    #             return cleaned_data

    #         # 🔥 Duplicate check (Aadhaar only)
    #         exists = StudentAdmission.objects.filter(
    #             document_type="AADHAAR",
    #             document_number=number
    #         ).exclude(pk=self.instance.pk).exists()

    #         if exists:
    #             self.add_error(
    #                 "document_number",
    #                 "This Aadhaar number is already registered."
    #             )

    #     return cleaned_data

