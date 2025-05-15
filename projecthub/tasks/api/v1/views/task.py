from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, exceptions, permissions, filters

from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership
from projecthub.tasks.api.v1.filters import TaskFilterSet
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilterSet
    search_fields = ["name"]
    #TODO: add ordering by created_at, priority, start_date, end_date and close_date

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

        # only admin, tenant owner and project member have access
        if not (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
                or self._project_membership
        ):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move into permission classes
    def check_permissions(self, request):
        # only admin, tenant owner or project staff can POST, others only GET
        if (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or (self._tenant_membership and self._tenant_membership.is_owner)
            or (self._project_membership and self._project_membership.is_staff)
        ):
            return

        raise exceptions.PermissionDenied()

    def get_queryset(self):
        qs = Task.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.kwargs["project_id"])
        qs = qs.visible_to(
            user=self.request.user,
            tenant=self.request.tenant,
            project_id=self.kwargs["project_id"]
        )
        return qs

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

    def get_queryset(self):
        qs = Task.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.kwargs["project_id"])
        qs = qs.visible_to(
            user=self.request.user,
            tenant=self.request.tenant,
            project_id=self.kwargs["project_id"]
        )
        return qs

    # TODO: move into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        # task responsible can't delete task, only update
        self._is_task_responsible = (obj.responsible_id == request.user.pk)
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
