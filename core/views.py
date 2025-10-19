from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Asset, MaintenanceRequest
from .forms import AssetForm, MaintenanceRequestForm, MaintenanceUpdateForm
from .forms import RegistrationForm
from django.contrib.auth.models import Group, User
from django.contrib import messages


def is_admin(user):
    return user.is_superuser


def index(request):
    return redirect('dashboard')


@login_required
def dashboard(request):
    total_assets = Asset.objects.count()
    assets_maint = Asset.objects.filter(status=Asset.STATUS_MAINT).count()
    pending_requests = MaintenanceRequest.objects.filter(status=MaintenanceRequest.STATUS_PENDING).count()

    # Data for chart
    status_counts = {
        'ready': Asset.objects.filter(status=Asset.STATUS_READY).count(),
        'maint': Asset.objects.filter(status=Asset.STATUS_MAINT).count(),
        'broken': Asset.objects.filter(status=Asset.STATUS_BROKEN).count(),
    }

    context = {
        'total_assets': total_assets,
        'assets_maint': assets_maint,
        'pending_requests': pending_requests,
        'status_counts': status_counts,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'core/asset_list.html', {'assets': assets})


@login_required
@user_passes_test(is_admin)
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm()
    return render(request, 'core/asset_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'core/asset_form.html', {'form': form, 'asset': asset})


@login_required
@user_passes_test(is_admin)
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        return redirect('asset_list')
    return render(request, 'core/asset_confirm_delete.html', {'asset': asset})


@login_required
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.created_by = request.user
            req.save()
            # mark asset status to maintenance
            asset = req.asset
            asset.status = Asset.STATUS_MAINT
            asset.save()
            return redirect('maintenance_list')
    else:
        form = MaintenanceRequestForm()
    return render(request, 'core/maintenance_form.html', {'form': form})


@login_required
def maintenance_list(request):
    requests = MaintenanceRequest.objects.select_related('asset', 'created_by').all().order_by('-created_at')
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
                asset = req.asset
                asset.status = Asset.STATUS_READY
                asset.save()
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
