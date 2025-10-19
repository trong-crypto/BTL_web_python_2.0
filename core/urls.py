from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/<int:pk>/update/', views.maintenance_update, name='maintenance_update'),
    path('register/', views.register, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/assign/', views.assign_role, name='assign_role'),
]
