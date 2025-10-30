from django.contrib import admin
from .models import Building, Floor, Room, Equipment, MaintenanceRequest
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from .models import RoomBooking

# Bộ lọc phân cấp cho RoomBooking
class RoomBookingBuildingFilter(SimpleListFilter):
    title = 'Tòa nhà'
    parameter_name = 'booking_building'

    def lookups(self, request, model_admin):
        buildings = Building.objects.all()
        return [(b.id, b.name) for b in buildings]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room__floor__building_id=self.value())
        return queryset

class RoomBookingFloorFilter(SimpleListFilter):
    title = 'Tầng'
    parameter_name = 'booking_floor'

    def lookups(self, request, model_admin):
        building_id = request.GET.get('booking_building')
        if building_id:
            floors = Floor.objects.filter(building_id=building_id)
            return [(f.id, f.name) for f in floors]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room__floor_id=self.value())
        return queryset

class RoomBookingRoomFilter(SimpleListFilter):
    title = 'Phòng'
    parameter_name = 'booking_room'

    def lookups(self, request, model_admin):
        floor_id = request.GET.get('booking_floor')
        if floor_id:
            rooms = Room.objects.filter(floor_id=floor_id)
            return [(r.id, r.name) for r in rooms]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room_id=self.value())
        return queryset

# Bộ lọc phân cấp cho Equipment
class EquipmentBuildingFilter(SimpleListFilter):
    title = 'Tòa nhà'
    parameter_name = 'building'

    def lookups(self, request, model_admin):
        buildings = Building.objects.all()
        return [(b.id, b.name) for b in buildings]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room__floor__building_id=self.value())
        return queryset

class EquipmentFloorFilter(SimpleListFilter):
    title = 'Tầng'
    parameter_name = 'floor'

    def lookups(self, request, model_admin):
        building_id = request.GET.get('building')
        if building_id:
            floors = Floor.objects.filter(building_id=building_id)
            return [(f.id, f.name) for f in floors]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room__floor_id=self.value())
        return queryset

class EquipmentRoomFilter(SimpleListFilter):
    title = 'Phòng'
    parameter_name = 'room'

    def lookups(self, request, model_admin):
        floor_id = request.GET.get('floor')
        if floor_id:
            rooms = Room.objects.filter(floor_id=floor_id)
            return [(r.id, r.name) for r in rooms]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room_id=self.value())
        return queryset

# Bộ lọc phân cấp cho Rooms
class RoomBuildingFilter(SimpleListFilter):
    title = 'Tòa nhà'
    parameter_name = 'building'

    def lookups(self, request, model_admin):
        buildings = Building.objects.all()
        return [(b.id, b.name) for b in buildings]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(floor__building_id=self.value())
        return queryset
    
class RoomFloorFilter(SimpleListFilter):
    title = 'Tầng'
    parameter_name = 'floor'

    def lookups(self, request, model_admin):
        building_id = request.GET.get('building')
        if building_id:
            floors = Floor.objects.filter(building_id=building_id)
            return [(f.id, f.name) for f in floors]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(floor_id=self.value())
        return queryset

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('building', 'number', 'name')
    list_filter = ('building',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('floor', 'code', 'name', 'status')
    list_filter = [
        RoomBuildingFilter, 
        RoomFloorFilter,
        'status'
    ]
    search_fields = ('name', 'code')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'room', 'status')
    list_filter = [
        EquipmentBuildingFilter, 
        EquipmentFloorFilter, 
        EquipmentRoomFilter,
        'status'
    ]
    search_fields = ('code', 'name')
    actions = ['copy_to_room']

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('copy-to-room/', self.admin_site.admin_view(self.copy_to_room_view), name='equipment_copy_to_room'),
        ]
        return custom + urls

    def copy_to_room(self, request, queryset):
        ids = ','.join(str(i) for i in queryset.values_list('pk', flat=True))
        return redirect(f'copy-to-room/?ids={ids}')

    copy_to_room.short_description = 'Copy selected equipment to another room'

    def copy_to_room_view(self, request):
        ids = request.GET.get('ids', '')
        if not ids:
            messages.error(request, 'No equipment selected.')
            return redirect('..')
        pks = [int(i) for i in ids.split(',') if i.isdigit()]
        equipments = Equipment.objects.filter(pk__in=pks)

        if request.method == 'POST':
            room_id = request.POST.get('room')
            room = get_object_or_404(Room, pk=room_id)
            created = 0
            renamed = 0
            from django.db import IntegrityError, transaction

            for eq in equipments:
                base_code = eq.code
                new_code = base_code
                suffix = 1
                while Equipment.objects.filter(room=room, code=new_code).exists():
                    suffix += 1
                    new_code = f"{base_code}-copy" if suffix == 2 else f"{base_code}-copy-{suffix-1}"

                try:
                    with transaction.atomic():
                        Equipment.objects.create(
                            room=room,
                            code=new_code,
                            name=eq.name,
                            description=eq.description,
                            status=eq.status,
                        )
                    created += 1
                    if new_code != base_code:
                        renamed += 1
                except IntegrityError:
                    messages.warning(request, f'Skipped equipment {eq} due to a uniqueness conflict.')

            msg = f'Created {created} copies in room {room}.'
            if renamed:
                msg += f' ({renamed} were renamed to avoid duplicates)'
            messages.success(request, msg)
            return redirect('..')

        rooms = Room.objects.select_related('floor__building').all().order_by('floor__building__name', 'floor__number', 'code')
        context = dict(
            self.admin_site.each_context(request),
            equipments=equipments,
            rooms=rooms,
            opts=self.model._meta,
        )
        return render(request, 'admin/core/equipment_copy_to_room.html', context)

class EquipmentStatusFilter(SimpleListFilter):
    title = 'Trạng thái thiết bị'
    parameter_name = 'equipment_status'

    def lookups(self, request, model_admin):
        return (
            (Equipment.STATUS_READY, 'Sẵn sàng'),
            (Equipment.STATUS_MAINT, 'Đang bảo trì'),
            (Equipment.STATUS_BROKEN, 'Đã hỏng'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        if queryset.model == Equipment:
            return queryset.filter(status=val)
        if queryset.model.__name__ == 'Room':
            return queryset.filter(equipments__status=val).distinct()
        return queryset

# Add the filter to the registered admins: Room and Equipment
try:
    RoomAdmin.list_filter = tuple(list(RoomAdmin.list_filter) + [EquipmentStatusFilter])
    # EquipmentAdmin.list_filter = tuple([EquipmentStatusFilter] + list(EquipmentAdmin.list_filter))
except Exception:
    pass

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'equipment__room__floor__building')
    search_fields = ('equipment__name', 'description')
    
    def save_model(self, request, obj, form, change):
        """Ensure equipment status stays in sync when admin edits a maintenance request."""
        super().save_model(request, obj, form, change)
        # If the maintenance request has an equipment, update its status based on request status
        try:
            eq = obj.equipment
            if not eq:
                return
            if obj.status == MaintenanceRequest.STATUS_DONE:
                eq.status = Equipment.STATUS_READY
            else:
                # For PENDING or IN_PROGRESS, mark equipment as under maintenance
                eq.status = Equipment.STATUS_MAINT
            eq.save()
        except Exception:
            # don't break admin if something odd happens
            pass

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'purpose', 'start_time', 'end_time', 'status', 'created_at']
    list_filter = [RoomBookingBuildingFilter, RoomBookingFloorFilter, RoomBookingRoomFilter, 'status', 'start_time', 'created_at']
    search_fields = ['room__name', 'user__username', 'purpose']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin đặt phòng', {
            'fields': ('room', 'user', 'purpose')
        }),
        ('Thời gian', {
            'fields': ('start_time', 'end_time')
        }),
        ('Trạng thái', {
            'fields': ('status',)
        }),
        ('Thời gian hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )