from django.db import models
from django.contrib.auth import get_user_model


class Asset(models.Model):
    STATUS_READY = 'ready'
    STATUS_MAINT = 'maint'
    STATUS_BROKEN = 'broken'

    STATUS_CHOICES = [
        (STATUS_READY, 'Sẵn sàng'),
        (STATUS_MAINT, 'Đang bảo trì'),
        (STATUS_BROKEN, 'Đã hỏng'),
    ]

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_READY)

    def __str__(self):
        return f"{self.code} - {self.name}"


class MaintenanceRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Đang chờ'),
        (STATUS_IN_PROGRESS, 'Đang xử lý'),
        (STATUS_DONE, 'Hoàn thành'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='requests')
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Yêu cầu #{self.id} - {self.asset} - {self.get_status_display()}"
