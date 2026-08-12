"""
Forms for Computer Training Institute Portal
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Student, Course, BatchDay, BatchTiming
# from franchise.models import Branch   # Branch moved to franchise app


# ======================================
# TIME DROPDOWN LIST (7 AM to 10 PM, 30 min gap)
# ======================================
TIME_CHOICES = [
    ("07:00", "07:00"),
    ("07:30", "07:30"),
    ("08:00", "08:00"),
    ("08:30", "08:30"),
    ("09:00", "09:00"),
    ("09:30", "09:30"),
    ("10:00", "10:00"),
    ("10:30", "10:30"),
    ("11:00", "11:00"),
    ("11:30", "11:30"),
    ("12:00", "12:00"),
    ("12:30", "12:30"),
    ("01:00", "01:00"),
    ("01:30", "01:30"),
    ("02:00", "02:00"),
    ("02:30", "02:30"),
    ("03:00", "03:00"),
    ("03:30", "03:30"),
    ("04:00", "04:00"),
    ("04:30", "04:30"),
    ("05:00", "05:00"),
    ("05:30", "05:30"),
    ("06:00", "06:00"),
    ("06:30", "06:30"),
    ("07:00", "07:00"),
    ("07:30", "07:30"),
    ("08:00", "08:00"),
    ("08:30", "08:30"),
    ("09:00", "09:00"),
    ("09:30", "09:30"),
    ("10:00", "10:00"),
]


# ======================================
# PUBLIC ADMISSION FORM
# ======================================
class AdmissionForm(forms.Form):

    # User fields
    first_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))


    # Student fields
    guardian_name = forms.CharField(max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    date_of_birth = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + list(Student.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    phone = forms.CharField(max_length=17, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    qualification = forms.CharField(max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    address = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        required=True,
        empty_label="Select Course",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # branch = forms.ModelChoiceField(
    #     queryset=Branch.objects.all(),
    #     required=False,
    #     empty_label="Select Branch",
    #     widget=forms.Select(attrs={'class': 'form-select'})
    # )

    batch_days = forms.ModelMultipleChoiceField(
        queryset=BatchDay.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    batch_timing = forms.ModelChoiceField(
        queryset=BatchTiming.objects.filter(is_active=True),
        required=False,
        empty_label="Select Batch Timing",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    receipt_number = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    admission_date = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))


    # -------- VALIDATION --------
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email


    # -------- SAVE STUDENT + USER --------
    def save(self):
        data = self.cleaned_data

        # Username generator
        base = data["email"].split("@")[0]
        username = base
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{i}"
            i += 1

        # Create User
        user = User.objects.create_user(
            username=username,
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=None
        )
        user.set_unusable_password()
        user.save()

        # Create Student
        student = Student.objects.create(
            user=user,
            guardian_name=data.get("guardian_name"),
            date_of_birth=data.get("date_of_birth"),
            gender=data.get("gender"),
            phone=data.get("phone"),
            qualification=data.get("qualification"),
            address=data.get("address"),
            course=data.get("course"),
            batch_timing=data.get("batch_timing"),
            receipt_number=data.get("receipt_number"),
            admission_date=data.get("admission_date"),
        )

        if data.get("batch_days"):
            student.batch_days.set(data["batch_days"])

        return student



# ======================================
# ADMIN STUDENT FORM
# ======================================
class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"
        widgets = {
            "admission_date": forms.DateInput(attrs={"type": "date"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }



# ======================================
# BATCH TIMING ADMIN FORM
# ======================================
class BatchTimingAdminForm(forms.ModelForm):
    class Meta:
        model = BatchTiming
        fields = "__all__"
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }
