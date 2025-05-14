from rest_framework import generics, exceptions, permissions

from projecthub.core.models import TenantMembership
from projecthub.tasks.models import TaskStatus
from .pagination import TaskStatusPagination
from ..serializers import (
    TaskStatusCreateSerializer,
    TaskStatusListSerializer,
    TaskStatusUpdateSerializer,
    TaskStatusDetailSerializer,
)


class TaskStatusListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = TaskStatusPagination

    def initial(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        if not (request.user.is_staff or self._tenant_membership):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return

        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
        ):
            return

        raise exceptions.PermissionDenied()

    def get_queryset(self):
        return TaskStatus.objects.filter(tenant=self.request.tenant)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskStatusCreateSerializer
        return TaskStatusListSerializer

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class TaskStatusRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        if self.request.user.is_staff or self._tenant_membership:
            return TaskStatus.objects.filter(tenant=self.request.tenant)
        return TaskStatus.objects.none()

    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
        ):
            return

        raise exceptions.PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TaskStatusUpdateSerializer
        return TaskStatusDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
