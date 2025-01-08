from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        labels = {
            'username': "Username",
            'email': "Email",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password must be the same.")

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'phone_number']
        labels = {
            'username': "Username",
            'email': "Email",
            'profile_picture': "Profile Picture",
            'phone_number': "Phone Number",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        labels = {
            'rating': "Rating",
            'review_text': "Review Text",
        }
