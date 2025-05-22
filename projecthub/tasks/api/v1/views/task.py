from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, permissions

from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    ReadOnlyPermission,
    IsTenantOwnerPermission,
    IsProjectStaffPermission,
    TaskResponsibleHasNoDeletePermission
)
from projecthub.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantOwnerPolicy,
    IsProjectMemberPolicy,
)
from projecthub.tasks.models import Task
from .pagination import TaskPagination
from ..filters import TaskFilterSet
from ..serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
    TaskDetailSerializer,
    TaskUpdateSerializerForResponsible,
)


class TaskListCreateAPIView(SecureGenericAPIView, generics.ListCreateAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (
            IsAdminUserPolicy
            | IsTenantOwnerPolicy
            | IsProjectMemberPolicy
        )
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (
            permissions.IsAdminUser
            | IsTenantOwnerPermission
            | IsProjectStaffPermission
            | ReadOnlyPermission
        )
    ]
    pagination_class = TaskPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = TaskFilterSet
    search_fields = ["name"] #TODO: add search by description
    ordering_fields = [
        "name",
        "priority",
        "created_at",
        "start_date",
        "end_date",
        "close_date"
    ]

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


class TaskRetrieveUpdateDestroyAPIView(SecureGenericAPIView,
                                       generics.RetrieveUpdateDestroyAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (
            IsAdminUserPolicy
            | IsTenantOwnerPolicy
            | IsProjectMemberPolicy
        )
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (
            permissions.IsAdminUser
            | IsTenantOwnerPermission
            | IsProjectStaffPermission
            | TaskResponsibleHasNoDeletePermission
            | ReadOnlyPermission
        )
    ]

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
        if self.request.method in {"PUT", "PATCH"}:
            task = self.get_object()
            if task.responsible == self.request.user:
                return TaskUpdateSerializerForResponsible
            return TaskUpdateSerializer
        return TaskDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
