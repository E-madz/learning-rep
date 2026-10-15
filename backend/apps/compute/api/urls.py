from django.urls import path, re_path

from .views import VirtualMachineActionView, VirtualMachineListCreateView

urlpatterns = [
    path("vms/", VirtualMachineListCreateView.as_view()),
    path("vms/<int:vm_id>/", VirtualMachineActionView.as_view()),
    re_path(r"^vms/(?P<vm_id>\d+)/(?P<action>start|stop)/$", VirtualMachineActionView.as_view()),
]
