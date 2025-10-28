from django import forms
from .models import Building, Floor, Room, Equipment, MaintenanceRequest, RoomBooking  # THÊM RoomBooking
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
        fields = ['floor', 'code', 'name', 'status']  # THÊM status


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


class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ['purpose', 'start_time', 'end_time']
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Nhập mục đích sử dụng phòng...'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'purpose': 'Mục đích sử dụng',
            'start_time': 'Thời gian bắt đầu',
            'end_time': 'Thời gian kết thúc',
        }


class RoomStatusForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['status']
        labels = {
            'status': 'Trạng thái phòng',
        }