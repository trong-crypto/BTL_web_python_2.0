from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('buildings/', RedirectView.as_view(pattern_name='asset_hierarchy', permanent=False), name='building_list'),
    
    path('buildings/create/', views.building_create, name='building_create'),
    path('buildings/<int:pk>/edit/', views.building_edit, name='building_edit'),
    path('buildings/<int:pk>/delete/', views.building_delete, name='building_delete'),
    path('buildings/<int:pk>/', views.building_detail, name='building_detail'),
    path('buildings/<int:building_pk>/floors/create/', views.floor_create, name='floor_create'),
    path('floors/<int:pk>/edit/', views.floor_edit, name='floor_edit'),
    path('floors/<int:pk>/delete/', views.floor_delete, name='floor_delete'),
    path('floors/<int:floor_pk>/rooms/', views.room_list, name='room_list'),
    path('floors/<int:floor_pk>/rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('rooms/<int:room_pk>/equipments/', views.equipment_list, name='equipment_list'),
    path('rooms/<int:room_pk>/equipments/create/', views.equipment_create, name='equipment_create'),
    path('equipments/<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('equipments/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    
    # CHỈ GIỮ LẠI 1 ĐƯỜNG DẪN DUY NHẤT
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/<int:pk>/update/', views.maintenance_update, name='maintenance_update'),
    
    # Đường dẫn mới cho tài sản - GIAO DIỆN MỚI
    path('assets/', views.asset_hierarchy, name='asset_hierarchy'),
    path('assets/building/<int:pk>/', views.asset_building_detail, name='asset_building_detail'),
    path('assets/floor/<int:pk>/', views.asset_floor_detail, name='asset_floor_detail'),
    path('assets/room/<int:pk>/', views.asset_room_detail, name='asset_room_detail'),
    
    # API endpoints for dependent selects
    path('api/floors/', views.api_floors, name='api_floors'),
    path('api/rooms/', views.api_rooms, name='api_rooms'),
    path('api/equipments/', views.api_equipments, name='api_equipments'),
    path('api/status_counts/', views.api_status_counts, name='api_status_counts'),
    path('register/', views.register, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/assign/', views.assign_role, name='assign_role'),

    # Room Booking URLs
    path('room/<int:room_pk>/booking/create/', views.room_booking_create, name='room_booking_create'),
    path('bookings/', views.room_booking_list, name='room_booking_list'),
    path('bookings/<int:pk>/update/', views.room_booking_update, name='room_booking_update'),
    path('room/<int:pk>/update-status/', views.update_room_status, name='update_room_status'),
]