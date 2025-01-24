from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import User, Review, Profile, Subscription, DownloadLink

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password1', 'password2']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'username': 'Username',
            'phone_number': 'Phone Number',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password and Confirm Password must be the same.")

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
        labels = {
            'username': "Username",
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': "Email",
            'phone_number': 'Phone Number',
            'profile_picture': 'Profile Picture',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # بررسی یا ایجاد پروفایل
        profile, created = Profile.objects.get_or_create(user=user)
        # ذخیره فیلدهای دیگر
        profile.phone_number = self.cleaned_data.get('phone_number')
        if self.cleaned_data.get('profile_picture'):
            profile.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()  # ذخیره اطلاعات کاربر
            profile.save()  # ذخیره اطلاعات پروفایل
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        labels = {
            'rating': "Rating",
            'review_text': "Review Text",
        }


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['subscription_type', 'end_date']
        labels = {
            'subscription_type': 'Subscription Type',
            'end_date': 'End Date',
        }
