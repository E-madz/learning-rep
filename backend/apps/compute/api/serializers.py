from rest_framework import serializers

from ..models import VirtualMachine


class VirtualMachineCreateSerializer(serializers.Serializer):
    name = serializers.RegexField(r"^[a-z0-9-]{1,64}$")
    cpu = serializers.IntegerField(min_value=1, max_value=16)
    ram_mb = serializers.IntegerField(min_value=512, max_value=65536)


class VirtualMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMachine
        fields = ["id", "name", "cpu", "ram_mb", "status", "created_at"]
