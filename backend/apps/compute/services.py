"""Service layer: business rules live here, not in views or serializers."""
from django.db import transaction

from .exceptions import (
    InvalidStateTransition,
    NameAlreadyExists,
    QuotaExceeded,
    VirtualMachineNotFound,
)
from .models import VirtualMachine
from .repositories import VirtualMachineRepository

Status = VirtualMachine.Status

CPU_QUOTA_PER_USER = 16

ALLOWED_TRANSITIONS = {
    Status.PENDING: {Status.RUNNING, Status.DELETED},
    Status.RUNNING: {Status.STOPPED, Status.DELETED},
    Status.STOPPED: {Status.RUNNING, Status.DELETED},
}


class VirtualMachineService:
    def __init__(self, repo: VirtualMachineRepository | None = None):
        self.repo = repo or VirtualMachineRepository()

    @transaction.atomic
    def create(self, *, owner, name, cpu, ram_mb) -> VirtualMachine:
        # NOTE: MySQL has no partial unique index, so this check is not race-free.
        # Hardening it is part of the database lesson.
        if self.repo.name_exists(owner, name):
            raise NameAlreadyExists(name)
        if self.repo.used_cpu(owner) + cpu > CPU_QUOTA_PER_USER:
            raise QuotaExceeded(f"CPU quota of {CPU_QUOTA_PER_USER} exceeded")
        return self.repo.add(owner=owner, name=name, cpu=cpu, ram_mb=ram_mb)

    def start(self, *, owner, vm_id):
        return self._transition(owner, vm_id, Status.RUNNING)

    def stop(self, *, owner, vm_id):
        return self._transition(owner, vm_id, Status.STOPPED)

    def delete(self, *, owner, vm_id):
        return self._transition(owner, vm_id, Status.DELETED)

    @transaction.atomic
    def _transition(self, owner, vm_id, target):
        vm = self.repo.get_for_update(owner=owner, vm_id=vm_id)
        if vm is None:
            raise VirtualMachineNotFound(vm_id)
        if target not in ALLOWED_TRANSITIONS.get(vm.status, set()):
            raise InvalidStateTransition(f"{vm.status} -> {target}")
        vm.status = target
        self.repo.save(vm)
        return vm
