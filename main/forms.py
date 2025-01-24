from django import forms
from .models import User, Review
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Profile

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
    phone_number = forms.CharField(max_length=15, required=False, label="Phone Number")
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': "Username",
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone_number = self.cleaned_data.get('phone_number')
        if self.cleaned_data.get('profile_picture'):
            profile.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()
            profile.save()
        return user



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        labels = {
            'rating': "Rating",
            'review_text': "Review Text",
        }
