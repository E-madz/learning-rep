"""Thin views: parse input -> call service -> map domain errors to HTTP."""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..exceptions import (
    InvalidStateTransition,
    NameAlreadyExists,
    QuotaExceeded,
    VirtualMachineNotFound,
)
from ..repositories import VirtualMachineRepository
from ..services import VirtualMachineService
from .serializers import VirtualMachineCreateSerializer, VirtualMachineSerializer

ERROR_STATUS = {
    QuotaExceeded: status.HTTP_403_FORBIDDEN,
    InvalidStateTransition: status.HTTP_409_CONFLICT,
    NameAlreadyExists: status.HTTP_409_CONFLICT,
    VirtualMachineNotFound: status.HTTP_404_NOT_FOUND,
}


class DomainErrorMixin:
    def handle_exception(self, exc):
        code = ERROR_STATUS.get(type(exc))
        if code:
            return Response({"detail": str(exc)}, status=code)
        return super().handle_exception(exc)


class VirtualMachineListCreateView(DomainErrorMixin, APIView):
    permission_classes = [IsAuthenticated]
    service = VirtualMachineService()

    def get(self, request):
        vms = VirtualMachineRepository().list_for_owner(request.user)
        return Response(VirtualMachineSerializer(vms, many=True).data)

    def post(self, request):
        data = VirtualMachineCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        vm = self.service.create(owner=request.user, **data.validated_data)
        return Response(VirtualMachineSerializer(vm).data, status=status.HTTP_201_CREATED)


class VirtualMachineActionView(DomainErrorMixin, APIView):
    """POST /vms/<id>/<action>/  where action in start|stop ; DELETE /vms/<id>/"""

    permission_classes = [IsAuthenticated]
    service = VirtualMachineService()

    def post(self, request, vm_id, action):
        handler = {"start": self.service.start, "stop": self.service.stop}[action]
        vm = handler(owner=request.user, vm_id=vm_id)
        return Response(VirtualMachineSerializer(vm).data)

    def delete(self, request, vm_id, action=None):
        self.service.delete(owner=request.user, vm_id=vm_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
