from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .widgets import CustomClearableFileInput
from cloudinary.uploader import destroy as cloudinary_destroy


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=150, required=True, help_text='Required. Enter a valid email address.')
    is_passenger = forms.BooleanField(required=False, label='Are you a Passenger?')
    is_driver = forms.BooleanField(required=False, label='Are you a Driver?')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_passenger', 'is_driver', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        is_passenger = cleaned_data.get('is_passenger')
        is_driver = cleaned_data.get('is_driver')
        if is_passenger and is_driver:
            raise forms.ValidationError("Please select only one option: Passenger or Driver.")
        if not is_passenger and not is_driver:
            raise forms.ValidationError("Please select at least one option: Passenger or Driver.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = Profile.objects.create(user=user)
            profile.is_passenger = self.cleaned_data.get('is_passenger', False)
            profile.is_driver = self.cleaned_data.get('is_driver', False)
            profile.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'contact_number', 'TODA', 'TODA_number', 'license_plate_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.is_driver:
            self.fields['license_plate_number'].widget.attrs['data-uppercase'] = 'true'
        else:
            self.fields['TODA'].widget = forms.HiddenInput()
            self.fields['TODA_number'].widget = forms.HiddenInput()
            self.fields['license_plate_number'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            profile.profile_picture = profile_picture
        if commit:
            user = profile.user
            profile.first_name = user.first_name
            profile.last_name = user.last_name
            profile.email = user.email
            profile.save()
        return profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
