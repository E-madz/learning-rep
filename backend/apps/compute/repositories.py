"""Repository: the only place that knows how VirtualMachine rows are queried."""
from django.db.models import Sum

from .models import VirtualMachine


class VirtualMachineRepository:
    def add(self, *, owner, name, cpu, ram_mb) -> VirtualMachine:
        return VirtualMachine.objects.create(owner=owner, name=name, cpu=cpu, ram_mb=ram_mb)

    def get_for_update(self, *, owner, vm_id) -> VirtualMachine | None:
        # select_for_update must be called inside transaction.atomic
        return (
            VirtualMachine.objects.select_for_update()
            .filter(owner=owner, pk=vm_id)
            .exclude(status=VirtualMachine.Status.DELETED)
            .first()
        )

    def list_for_owner(self, owner):
        return VirtualMachine.objects.filter(owner=owner).exclude(
            status=VirtualMachine.Status.DELETED
        )

    def used_cpu(self, owner) -> int:
        return self.list_for_owner(owner).aggregate(total=Sum("cpu"))["total"] or 0

    def name_exists(self, owner, name) -> bool:
        return self.list_for_owner(owner).filter(name=name).exists()

    def save(self, vm: VirtualMachine) -> None:
        vm.save(update_fields=["status"])
