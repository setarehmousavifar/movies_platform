from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Profile, Review, Subscription

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    email = forms.EmailField(required=True, label='Email Address')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'username': 'Username',
            'phone_number': 'Phone Number',
        }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise forms.ValidationError('Email is required.')
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password(
                password1,
                user=User(**{k: self.data.get(k) for k in ('username', 'email')}),
            )
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Password and Confirm Password must be the same.')
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'profile_picture': 'Profile Picture',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        profile, _ = Profile.objects.get_or_create(user=user)
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
        labels = {'rating': 'Rating', 'review_text': 'Review Text'}
        widgets = {'rating': forms.NumberInput(attrs={'min': 1, 'max': 10})}

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 1 or rating > 10:
            raise forms.ValidationError('Rating must be between 1 and 10.')
        return rating


class ReplyForm(forms.Form):
    """Nested reply stored as a child Review (Phase 1 — single threading model)."""

    reply_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label='Reply Text',
    )


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['subscription_type', 'end_date']
        labels = {
            'subscription_type': 'Subscription Type',
            'end_date': 'End Date',
        }
        widgets = {
            'subscription_type': forms.Select(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
