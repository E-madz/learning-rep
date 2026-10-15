from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class VirtualMachineApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("alice", password="x")
        self.client.force_authenticate(self.user)

    def test_create_and_list(self):
        r = self.client.post("/api/vms/", {"name": "web-1", "cpu": 2, "ram_mb": 2048}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(len(self.client.get("/api/vms/").json()), 1)

    def test_validation_error(self):
        r = self.client.post("/api/vms/", {"name": "Bad Name", "cpu": 2, "ram_mb": 2048}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_quota_maps_to_403_and_bad_transition_to_409(self):
        r = self.client.post("/api/vms/", {"name": "a", "cpu": 16, "ram_mb": 1024}, format="json")
        self.assertEqual(self.client.post("/api/vms/", {"name": "b", "cpu": 1, "ram_mb": 1024}, format="json").status_code, 403)
        self.assertEqual(self.client.post(f"/api/vms/{r.json()['id']}/stop/").status_code, 409)

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/vms/").status_code, 403)
