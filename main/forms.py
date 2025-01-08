from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="تأیید رمز عبور")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        labels = {
            'username': "نام کاربری",
            'email': "ایمیل",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("رمز عبور و تأیید رمز عبور باید یکسان باشند.")

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'phone_number']
        labels = {
            'username': "نام کاربری",
            'email': "ایمیل",
            'profile_picture': "عکس پروفایل",
            'phone_number': "شماره تلفن",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        labels = {
            'rating': "امتیاز",
            'review_text': "متن نقد",
        }
