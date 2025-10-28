from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Building, Floor, Room, Equipment, MaintenanceRequest
from .forms import BuildingForm, FloorForm, RoomForm, EquipmentForm, MaintenanceRequestForm, MaintenanceUpdateForm
from .forms import RegistrationForm
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    """Redirect superusers straight to the Django admin after login."""

    def get_success_url(self):
        # If user is superuser, go to admin index; otherwise use default behavior
        if self.request.user.is_active and self.request.user.is_superuser:
            return '/admin/'
        return super().get_success_url()


def is_admin(user):
    return user.is_superuser


def index(request):
    return redirect('dashboard')


@login_required
def dashboard(request):
    total_assets = Equipment.objects.count()
    assets_maint = Equipment.objects.filter(status=Equipment.STATUS_MAINT).count()
    pending_requests = MaintenanceRequest.objects.filter(status=MaintenanceRequest.STATUS_PENDING).count()

    # Data for chart
    status_counts = {
        'ready': Equipment.objects.filter(status=Equipment.STATUS_READY).count(),
        'maint': Equipment.objects.filter(status=Equipment.STATUS_MAINT).count(),
        'broken': Equipment.objects.filter(status=Equipment.STATUS_BROKEN).count(),
    }

    context = {
        'total_assets': total_assets,
        'assets_maint': assets_maint,
        'pending_requests': pending_requests,
        'status_counts': status_counts,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def building_list(request):
    buildings = Building.objects.all()
    return render(request, 'core/building_list.html', {'buildings': buildings})


@login_required
@user_passes_test(is_admin)
def building_create(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('building_list')
    else:
        form = BuildingForm()
    return render(request, 'core/building_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def building_edit(request, pk):
    building = get_object_or_404(Building, pk=pk)
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            return redirect('building_list')
    else:
        form = BuildingForm(instance=building)
    return render(request, 'core/building_form.html', {'form': form, 'building': building})


@login_required
@user_passes_test(is_admin)
def building_delete(request, pk):
    building = get_object_or_404(Building, pk=pk)
    if request.method == 'POST':
        building.delete()
        return redirect('building_list')
    return render(request, 'core/building_confirm_delete.html', {'building': building})


@login_required
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.created_by = request.user
            req.save()
            # mark equipment status to maintenance
            equipment = req.equipment
            # If the user clicked the "broken" button, mark equipment as broken;
            # otherwise mark it as under maintenance.
            if request.POST.get('broken'):
                equipment.status = Equipment.STATUS_BROKEN
            else:
                equipment.status = Equipment.STATUS_MAINT
            equipment.save()
            return redirect('maintenance_list')
    else:
        form = MaintenanceRequestForm()
    buildings = Building.objects.all()
    return render(request, 'core/maintenance_form.html', {'form': form, 'buildings': buildings})


def api_floors(request):
    building_id = request.GET.get('building')
    if not building_id:
        return JsonResponse({'error': 'missing building id'}, status=400)
    floors = Floor.objects.filter(building_id=building_id).order_by('number').values('id', 'number', 'name')
    return JsonResponse(list(floors), safe=False)


def api_rooms(request):
    floor_id = request.GET.get('floor')
    if not floor_id:
        return JsonResponse({'error': 'missing floor id'}, status=400)
    rooms = Room.objects.filter(floor_id=floor_id).values('id', 'code', 'name')
    return JsonResponse(list(rooms), safe=False)


def api_equipments(request):
    room_id = request.GET.get('room')
    if not room_id:
        return JsonResponse({'error': 'missing room id'}, status=400)
    equipments = Equipment.objects.filter(room_id=room_id).values('id', 'code', 'name', 'status')
    return JsonResponse(list(equipments), safe=False)


@login_required
def building_detail(request, pk):
    building = get_object_or_404(Building, pk=pk)
    floors = building.floors.all()
    return render(request, 'core/building_detail.html', {'building': building, 'floors': floors})


@login_required
@user_passes_test(is_admin)
def floor_create(request, building_pk):
    building = get_object_or_404(Building, pk=building_pk)
    if request.method == 'POST':
        form = FloorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('building_detail', pk=building_pk)
    else:
        form = FloorForm(initial={'building': building})
    return render(request, 'core/floor_form.html', {'form': form, 'building': building})


@login_required
@user_passes_test(is_admin)
def floor_edit(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    if request.method == 'POST':
        form = FloorForm(request.POST, instance=floor)
        if form.is_valid():
            form.save()
            return redirect('building_detail', pk=floor.building.pk)
    else:
        form = FloorForm(instance=floor)
    return render(request, 'core/floor_form.html', {'form': form, 'building': floor.building, 'floor': floor})


@login_required
@user_passes_test(is_admin)
def floor_delete(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    building_pk = floor.building.pk
    if request.method == 'POST':
        floor.delete()
        return redirect('building_detail', pk=building_pk)
    return render(request, 'core/floor_confirm_delete.html', {'floor': floor})


@login_required
def room_list(request, floor_pk):
    floor = get_object_or_404(Floor, pk=floor_pk)
    rooms = floor.rooms.all()
    return render(request, 'core/room_list.html', {'floor': floor, 'rooms': rooms})


@login_required
@user_passes_test(is_admin)
def room_create(request, floor_pk):
    floor = get_object_or_404(Floor, pk=floor_pk)
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list', floor_pk=floor_pk)
    else:
        form = RoomForm(initial={'floor': floor})
    return render(request, 'core/room_form.html', {'form': form, 'floor': floor})


@login_required
@user_passes_test(is_admin)
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_list', floor_pk=room.floor.pk)
    else:
        form = RoomForm(instance=room)
    return render(request, 'core/room_form.html', {'form': form, 'floor': room.floor, 'room': room})


@login_required
@user_passes_test(is_admin)
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    floor_pk = room.floor.pk
    if request.method == 'POST':
        room.delete()
        return redirect('room_list', floor_pk=floor_pk)
    return render(request, 'core/room_confirm_delete.html', {'room': room})


@login_required
def equipment_list(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    equipments = room.equipments.all()
    return render(request, 'core/equipment_list.html', {'room': room, 'equipments': equipments})


@login_required
@user_passes_test(is_admin)
def equipment_create(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment_list', room_pk=room_pk)
    else:
        form = EquipmentForm(initial={'room': room})
    return render(request, 'core/equipment_form.html', {'form': form, 'room': room})


@login_required
@user_passes_test(is_admin)
def equipment_edit(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=eq)
        if form.is_valid():
            form.save()
            return redirect('equipment_list', room_pk=eq.room.pk)
    else:
        form = EquipmentForm(instance=eq)
    return render(request, 'core/equipment_form.html', {'form': form, 'room': eq.room, 'equipment': eq})


@login_required
@user_passes_test(is_admin)
def equipment_delete(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    room_pk = eq.room.pk
    if request.method == 'POST':
        eq.delete()
        return redirect('equipment_list', room_pk=room_pk)
    return render(request, 'core/equipment_confirm_delete.html', {'equipment': eq})


@login_required
def maintenance_list(request):
    requests = MaintenanceRequest.objects.select_related('equipment__room__floor__building', 'created_by').all().order_by('-created_at')
    return render(request, 'core/maintenance_list.html', {'requests': requests})


@login_required
@user_passes_test(is_admin)
def maintenance_update(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        form = MaintenanceUpdateForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            # if marked done, optionally update asset status
            if req.status == MaintenanceRequest.STATUS_DONE:
                equipment = req.equipment
                equipment.status = Equipment.STATUS_READY
                equipment.save()
            return redirect('maintenance_list')
    else:
        form = MaintenanceUpdateForm(instance=req)
    return render(request, 'core/maintenance_update.html', {'form': form, 'req': req})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # add to default 'User' group if exists
            try:
                grp = Group.objects.get(name='User')
                user.groups.add(grp)
            except Group.DoesNotExist:
                pass
            messages.success(request, 'Tài khoản đã được tạo. Vui lòng đăng nhập.')
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all().order_by('username')
    groups = Group.objects.all()
    return render(request, 'core/user_list.html', {'users': users, 'groups': groups})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def assign_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        role = request.POST.get('role')
        # remove from Admin/User groups and add accordingly
        admin_grp = Group.objects.filter(name='Admin').first()
        user_grp = Group.objects.filter(name='User').first()
        if admin_grp:
            user.groups.remove(admin_grp)
        if user_grp:
            user.groups.remove(user_grp)
        if role == 'Admin' and admin_grp:
            user.is_staff = True
            user.is_superuser = True
            user.groups.add(admin_grp)
        elif role == 'User' and user_grp:
            user.is_staff = False
            user.is_superuser = False
            user.groups.add(user_grp)
        user.save()
        messages.success(request, 'Đã cập nhật vai trò.')
        return redirect('user_list')
    return render(request, 'core/assign_role.html', {'user_obj': user})

#########################################test###########################


@login_required
def asset_hierarchy(request):
    """Hiển thị danh sách tòa nhà - giao diện người dùng cho tài sản"""
    buildings = Building.objects.all()
    return render(request, 'core/asset_buildings.html', {'buildings': buildings})

@login_required
def asset_building_detail(request, pk):
    """Hiển thị các tầng trong một tòa nhà"""
    building = get_object_or_404(Building, pk=pk)
    floors = building.floors.all().order_by('number')
    return render(request, 'core/asset_floors.html', {'building': building, 'floors': floors})

@login_required
def asset_floor_detail(request, pk):
    """Hiển thị các phòng trong một tầng"""
    floor = get_object_or_404(Floor, pk=pk)
    rooms = floor.rooms.all()
    return render(request, 'core/asset_rooms.html', {'floor': floor, 'rooms': rooms})

@login_required
def asset_room_detail(request, pk):
    """Hiển thị các thiết bị trong một phòng"""
    room = get_object_or_404(Room, pk=pk)
    equipments = room.equipments.all()
    return render(request, 'core/asset_equipment.html', {'room': room, 'equipments': equipments})
