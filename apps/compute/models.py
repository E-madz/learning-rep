from django.conf import settings
from django.db import models


class VirtualMachine(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        STOPPED = "stopped"
        DELETED = "deleted"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="virtual_machines"
    )
    name = models.CharField(max_length=64)
    cpu = models.PositiveSmallIntegerField()
    ram_mb = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["owner", "status"])]

    def __str__(self):
        return f"{self.name} ({self.status})"
