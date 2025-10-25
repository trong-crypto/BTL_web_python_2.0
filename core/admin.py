from django.contrib import admin
from .models import Building, Floor, Room, Equipment, MaintenanceRequest
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages



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
    list_display = ('floor', 'code', 'name')
    list_filter = ('floor__building',)
   


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'room', 'status')
    list_filter = ('status', 'room__floor__building')
    search_fields = ('code', 'name')
    actions = ['copy_to_room' ]
    

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('copy-to-room/', self.admin_site.admin_view(self.copy_to_room_view), name='equipment_copy_to_room'),
        ]
        return custom + urls

    def copy_to_room(self, request, queryset):
        # redirect to intermediate view with selected ids
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
                # attempt to create with same code; if conflict, try to generate a unique code
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
                    # If we still hit an integrity error, skip this item and continue
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

    


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'equipment__room__floor__building')
    search_fields = ('equipment__name', 'description')
