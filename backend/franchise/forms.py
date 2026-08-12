from django import forms
from .models import Franchise
from django.contrib.auth.models import User

class FranchiseForm(forms.ModelForm):

    username = forms.CharField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    email = forms.EmailField(required=True)

    email_verified_flag = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Franchise
        fields = "__all__"


    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop("request", None)

        super().__init__(*args, **kwargs)

        verified = False

        # If editing existing object
        if self.instance and self.instance.pk:
            verified = self.instance.email_verified

        # If OTP verified in this session
        if self.request and self.request.session.get("email_verified"):
            verified = True

        self.fields["email_verified_flag"].initial = str(verified)

        # 🔥 Keep only first label
        self.fields["student_id_part1"].label = "Student ID"
        self.fields["student_id_part2"].label = ""
        self.fields["student_id_part3"].label = ""
        if (
            self.instance
            and self.instance.pk
            and self.instance.user
        ):
            self.fields["username"].initial = (
                self.instance.user.username
            )
   


    def clean(self):

        cleaned_data = super().clean()

        verified = False

        if self.request:
            verified = self.request.session.get(
                "email_verified",
                False
            )

        # password only can bypass OTP
        ignore_fields = [
            "password",
            "email_verified_flag"
        ]

        changed = False

        # Edit page
        if self.instance and self.instance.pk:

            for field in self.changed_data:

                if field not in ignore_fields:

                    changed = True
                    break

        # Add page
        else:

            for field, value in cleaned_data.items():

                if (
                    field not in ignore_fields
                    and value
                ):

                    changed = True
                    break

        # remember if OTP was used
        self._otp_required_for_save = changed

        if changed and not verified:

            raise forms.ValidationError(
                "Verify OTP before saving changes."
            )
        self._otp_required_for_save = changed
        return cleaned_data


def consume_otp(self):

    if (
        self.request
        and getattr(
            self,
            "_otp_required_for_save",
            False
        )
    ):

        self.request.session.pop(
            "email_verified",
            None
        )

        self.request.session.modified = True



class FranchiseAccessForm(forms.Form):

    new_email = forms.EmailField(required=False)
    new_username = forms.CharField(required=False)

    current_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )

    def clean_new_username(self):
        username = self.cleaned_data.get("new_username")

        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Username already exists.")

        return username
    
    def clean(self):

        cleaned_data = super().clean()

        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")

        if new_password and not current_password:
            raise forms.ValidationError(
                "Enter current password to change password."
            )

        return cleaned_data

from django import forms
from .models import Franchise


