from django.contrib import admin
from .models import Asset, MaintenanceRequest


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'location', 'status')
    search_fields = ('code', 'name')
    list_filter = ('status',)


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'asset')
    search_fields = ('asset__name', 'description')
