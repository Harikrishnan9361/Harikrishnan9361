import re
from datetime import date
from decimal import Decimal
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from PIL import Image
from .models import Booking, UserProfile


def validate_image_file(image):
    """Validate uploaded image file size and content integrity with Pillow."""
    if not image:
        return image

    # Limit file size to 5MB
    max_size_mb = 5
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file size must not exceed {max_size_mb} MB.")

    try:
        # Verify image using Pillow
        img = Image.open(image)
        img.verify()
        # Reset file pointer after verify
        image.seek(0)
    except Exception:
        raise ValidationError("Invalid or corrupted image file format.")

    allowed_formats = ['JPEG', 'PNG', 'WEBP', 'JPG']
    try:
        img = Image.open(image)
        if img.format.upper() not in allowed_formats:
            raise ValidationError(f"Image format '{img.format}' is not supported. Use JPG, PNG, or WEBP.")
        image.seek(0)
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError("Could not process the uploaded image.")

    return image


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'auth-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'auth-input'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'auth-input'})
    )
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'auth-input', 'accept': 'image/*'})
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone', 'profile_photo']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            return validate_image_file(photo)
        return photo

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Split full name into first and last name
        names = self.cleaned_data['full_name'].strip().split(None, 1)
        user.first_name = names[0]
        user.last_name = names[1] if len(names) > 1 else ''
        
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone', '')
            if self.cleaned_data.get('profile_photo'):
                profile.profile_photo = self.cleaned_data['profile_photo']
            profile.save()
        return user


class BookingForm(forms.Form):
    customer_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Alex Morgan', 'class': 'form-field-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'e.g. alex@example.com', 'class': 'form-field-input'})
    )
    phone = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210', 'class': 'form-field-input'})
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City, State', 'class': 'form-field-input'})
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'e.g. Vegetarian meals, wheelchair access...', 'class': 'form-field-textarea'})
    )
    travel_date = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-field-input', 'id': 'travelDateInput'})
    )
    check_out_date = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-field-input', 'id': 'checkOutInput'})
    )
    num_travelers = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-field-input', 'id': 'numTravelers', 'min': '1', 'max': '50'})
    )
    hotel_type = forms.ChoiceField(
        choices=Booking.HOTEL_TYPES,
        initial='Standard',
        widget=forms.Select(attrs={'class': 'form-field-select', 'id': 'hotelType'})
    )
    transport = forms.ChoiceField(
        choices=Booking.TRANSPORT_TYPES,
        initial='Flight',
        widget=forms.Select(attrs={'class': 'form-field-select'})
    )

    def clean_travel_date(self):
        travel_date = self.cleaned_data.get('travel_date')
        if travel_date and travel_date < date.today():
            raise ValidationError("Check-in / travel date cannot be in the past.")
        return travel_date

    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        check_out_date = cleaned_data.get('check_out_date')

        if travel_date and check_out_date:
            if check_out_date <= travel_date:
                self.add_error('check_out_date', "Check-out date must be strictly after the check-in date.")
        return cleaned_data


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=25, required=False)
    profile_photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if self.user:
            existing = User.objects.filter(email__iexact=email).exclude(pk=self.user.pk)
            if existing.exists():
                raise ValidationError("This email is already in use by another account.")
        return email

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            return validate_image_file(photo)
        return photo


class PaymentProcessForm(forms.Form):
    PAYMENT_CHOICES = [
        ('Credit / Debit Card', 'Credit / Debit Card'),
        ('UPI / QR Payment', 'UPI / QR Payment'),
        ('Pay at Hotel', 'Pay at Hotel'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, required=True)
    vip_protection = forms.BooleanField(required=False)
