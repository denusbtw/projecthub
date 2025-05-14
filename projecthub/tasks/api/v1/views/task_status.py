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
    #TODO: add filterset_class
    #TODO: add search by name and code
    #TODO: add ordering by created_at, order, name

    #TODO: move into mixin
    def initial(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        # only staff and tenant member have access
        if not (request.user.is_staff or self._tenant_membership):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move into permission classes
    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return

        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
        ):
            return

        raise exceptions.PermissionDenied()

    # TODO: move into TaskStatus manager
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

    # TODO: move into Task Status manager
    def get_queryset(self):
        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        # admin and tenant member see all task statuses
        if self.request.user.is_staff or self._tenant_membership:
            return TaskStatus.objects.filter(tenant=self.request.tenant)
        return TaskStatus.objects.none()

    # TODO: move into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        # only admin and tenant owner can PUT, PATCH and DELETE
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
