from django import forms
from .models import Asset, MaintenanceRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['code', 'name', 'description', 'location', 'status']


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['asset', 'description']


class MaintenanceUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['status', 'note']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
