from django.db import models
from django.contrib.auth import get_user_model


class Building(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('building', 'number')

    def __str__(self):
        # Return: "BLDG01 — Building Name — Floor Name"
        # If floor.name is missing, fall back to number: "BLDG01 — Building Name — Tầng {number}"
        building_part = f"{self.building.code} — {self.building.name}"
        floor_part = self.name if self.name else f"Tầng {self.number}"
        return f"{building_part} — {floor_part}"


class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('floor', 'code')

    def __str__(self):
        # Use the floor's string (which includes building code and name) then the room label
        floor_label = str(self.floor)
        room_label = f"{self.code} {self.name}".strip()
        return f"{floor_label} — {room_label}"


class Equipment(models.Model):
    STATUS_READY = 'ready'
    STATUS_MAINT = 'maint'
    STATUS_BROKEN = 'broken'

    STATUS_CHOICES = [
        (STATUS_READY, 'Sẵn sàng'),
        (STATUS_MAINT, 'Đang bảo trì'),
        (STATUS_BROKEN, 'Đã hỏng'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='equipments')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_READY)

    class Meta:
        unique_together = ('room', 'code')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.room})"


class MaintenanceRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Đang chờ'),
        (STATUS_IN_PROGRESS, 'Đang xử lý'),
        (STATUS_DONE, 'Hoàn thành'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='requests', null=True, blank=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Yêu cầu #{self.id} - {self.equipment} - {self.get_status_display()}"
