from django.contrib.auth import get_user_model
from django.test import TestCase

from ..exceptions import (
    InvalidStateTransition,
    NameAlreadyExists,
    QuotaExceeded,
    VirtualMachineNotFound,
)
from ..models import VirtualMachine
from ..services import VirtualMachineService


class VirtualMachineServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user("alice", password="x")
        self.bob = User.objects.create_user("bob", password="x")
        self.service = VirtualMachineService()

    def test_create_enforces_cpu_quota(self):
        self.service.create(owner=self.alice, name="a", cpu=12, ram_mb=1024)
        with self.assertRaises(QuotaExceeded):
            self.service.create(owner=self.alice, name="b", cpu=8, ram_mb=1024)

    def test_lifecycle(self):
        vm = self.service.create(owner=self.alice, name="a", cpu=2, ram_mb=1024)
        self.assertEqual(self.service.start(owner=self.alice, vm_id=vm.id).status, "running")
        self.assertEqual(self.service.stop(owner=self.alice, vm_id=vm.id).status, "stopped")

    def test_invalid_transition(self):
        vm = self.service.create(owner=self.alice, name="a", cpu=2, ram_mb=1024)
        with self.assertRaises(InvalidStateTransition):
            self.service.stop(owner=self.alice, vm_id=vm.id)  # pending -> stopped

    def test_cannot_touch_other_users_vm(self):
        vm = self.service.create(owner=self.alice, name="a", cpu=2, ram_mb=1024)
        with self.assertRaises(VirtualMachineNotFound):
            self.service.start(owner=self.bob, vm_id=vm.id)

    def test_deleted_vm_frees_quota_and_name(self):
        vm = self.service.create(owner=self.alice, name="a", cpu=16, ram_mb=1024)
        self.service.delete(owner=self.alice, vm_id=vm.id)
        self.service.create(owner=self.alice, name="a", cpu=16, ram_mb=1024)
        self.assertEqual(VirtualMachine.objects.count(), 2)

    def test_duplicate_active_name_rejected(self):
        self.service.create(owner=self.alice, name="a", cpu=1, ram_mb=1024)
        with self.assertRaises(NameAlreadyExists):
            self.service.create(owner=self.alice, name="a", cpu=1, ram_mb=1024)
