# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


# ------------------------------------------
# Registration Form
# ------------------------------------------
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


# ------------------------------------------
# Avatar-only Form (KEEPING this for dashboard changes)
# ------------------------------------------
class AvatarForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']


# ------------------------------------------
# ⭐ NEW PROFILE EDIT FORM
# ------------------------------------------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "full_name",
            "email",
            "phone",
            "passion",
            "goal",
            "github",
            "linkedin",
            "avatar",
            "cover_photo",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "input"}),
            "email": forms.EmailInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input"}),
            "passion": forms.TextInput(attrs={"class": "input"}),
            "goal": forms.TextInput(attrs={"class": "input"}),
            "github": forms.URLInput(attrs={"class": "input"}),
            "linkedin": forms.URLInput(attrs={"class": "input"}),
        }
