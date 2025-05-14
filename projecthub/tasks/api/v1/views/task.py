from rest_framework import generics, exceptions, permissions
from rest_framework.generics import get_object_or_404

from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership
from projecthub.tasks.api.v1.serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
    TaskDetailSerializer,
)
from projecthub.tasks.api.v1.views.pagination import TaskPagination
from projecthub.tasks.models import Task


class TaskListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = TaskPagination

    # TODO: move logic into mixin
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).first()
        self._project_membership = ProjectMembership.objects.filter(
            project__tenant=request.tenant,
            project_id=kwargs["project_id"],
            user=request.user,
        ).first()

        if not (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
                or self._project_membership
        ):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move into permission classes
    def check_permissions(self, request):
        if (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or (self._tenant_membership and self._tenant_membership.is_owner)
            or (self._project_membership and self._project_membership.is_staff)
        ):
            return

        raise exceptions.PermissionDenied()

    # TODO: move logic into Task manager
    def get_queryset(self):
        base_queryset = Task.objects.filter(
            project__tenant=self.request.tenant, project_id=self.kwargs["project_id"]
        )

        # admin, tenant owner and project staff see all tasks
        if (
            self.request.user.is_staff
            or (self._tenant_membership and self._tenant_membership.is_owner)
            or (self._project_membership and self._project_membership.is_staff)
        ):
            return base_queryset

        # project user see only tasks he is responsible of
        if self._project_membership and self._project_membership.is_user:
            return base_queryset.filter(responsible=self.request.user)
        return Task.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateSerializer
        return TaskListSerializer

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_id"],
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    # TODO: move into Task manager
    def get_queryset(self):
        return Task.objects.filter(
            project__tenant=self.request.tenant,
            project_id=self.kwargs["project_id"],
        )

    # TODO: move into mixin?
    def get_object(self):
        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()
        self._project_membership = ProjectMembership.objects.filter(
            project_id=self.kwargs["project_id"], user=self.request.user
        ).first()

        task = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self._is_task_responsible = (self.request.user.pk == task.responsible_id)

        if not (
                self.request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
                or (self._project_membership and self._project_membership.is_staff)
                or self._is_task_responsible
        ):
            raise exceptions.NotFound()

        self.check_object_permissions(self.request, task)
        return task

    # TODO: move into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        if request.method == "DELETE" and self._is_task_responsible:
            raise exceptions.PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            # TODO
            # if self._is_task_responsible:
            #     return TaskUpdateSerializerForResponsible
            return TaskUpdateSerializer
        return TaskDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
