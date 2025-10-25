from django import forms
from .models import Building, Floor, Room, Equipment, MaintenanceRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['code', 'name', 'description']


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['building', 'number', 'name']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['floor', 'code', 'name']


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['room', 'code', 'name', 'description', 'status']


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['equipment', 'description']


class MaintenanceUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['status', 'note']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
