from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, filters, permissions
from rest_framework.generics import get_object_or_404

from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    ReadOnlyPermission,
    IsTenantOwnerPermission,
    IsProjectStaffPermission,
    TaskResponsibleHasNoDeletePermission,
)
from projecthub.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantOwnerPolicy,
    IsProjectMemberPolicy,
)
from projecthub.projects.models import Project
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


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            description="Фільтр за статусом задачі (можна передати кілька через кому)",
            required=False,
            many=True,
        ),
        OpenApiParameter(
            name="priority",
            type=OpenApiTypes.INT,
            description="Фільтр за точним пріоритетом",
            required=False,
        ),
        OpenApiParameter(
            name="priority_min",
            type=OpenApiTypes.INT,
            description="Фільтр за мінімальним пріоритетом (gte)",
            required=False,
        ),
        OpenApiParameter(
            name="priority_max",
            type=OpenApiTypes.INT,
            description="Фільтр за максимальним пріоритетом (lte)",
            required=False,
        ),
        OpenApiParameter(
            name="responsible",
            type=OpenApiTypes.STR,
            description="Фільтр за username відповідального",
            required=False,
        ),
        OpenApiParameter(
            name="creator",
            type=OpenApiTypes.STR,
            description="Фільтр за username того, хто створив задачу",
            required=False,
        ),
        OpenApiParameter(
            name="start_date_after",
            type=OpenApiTypes.DATE,
            description="Фільтр за початковою датою задачі, починаючи з цієї дати (gte)",
            required=False,
        ),
        OpenApiParameter(
            name="start_date_before",
            type=OpenApiTypes.DATE,
            description="Фільтр за початковою датою задачі до цієї дати (lte)",
            required=False,
        ),
        OpenApiParameter(
            name="end_date_after",
            type=OpenApiTypes.DATE,
            description="Фільтр за кінцевою датою задачі, починаючи з цієї дати (gte)",
            required=False,
        ),
        OpenApiParameter(
            name="end_date_before",
            type=OpenApiTypes.DATE,
            description="Фільтр за кінцевою датою задачі до цієї дати (lte)",
            required=False,
        ),
        OpenApiParameter(
            name="close_date_after",
            type=OpenApiTypes.DATE,
            description="Фільтр за датою закриття задачі, починаючи з цієї дати (gte)",
            required=False,
        ),
        OpenApiParameter(
            name="close_date_before",
            type=OpenApiTypes.DATE,
            description="Фільтр за датою закриття задачі до цієї дати (lte)",
            required=False,
        ),
    ],
    methods=["GET"],
)
class TaskListCreateAPIView(SecureGenericAPIView, generics.ListCreateAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (IsAdminUserPolicy | IsTenantOwnerPolicy | IsProjectMemberPolicy)
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
        filters.OrderingFilter,
    ]
    filterset_class = TaskFilterSet
    search_fields = ["name"]  # TODO: add search by description
    ordering_fields = [
        "name",
        "priority",
        "created_at",
        "start_date",
        "end_date",
        "close_date",
    ]

    def get_queryset(self):
        qs = Task.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.kwargs["project_id"])
        qs = qs.visible_to(
            user=self.request.user,
            tenant=self.request.tenant,
            project_id=self.kwargs["project_id"],
        )
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateSerializer
        return TaskListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_id"])
        return context

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_id"],
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class TaskRetrieveUpdateDestroyAPIView(
    SecureGenericAPIView, generics.RetrieveUpdateDestroyAPIView
):
    policy_classes = [
        IsAuthenticatedPolicy
        & (IsAdminUserPolicy | IsTenantOwnerPolicy | IsProjectMemberPolicy)
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
            project_id=self.kwargs["project_id"],
        )
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            task = self.get_object()
            if task.responsible == self.request.user:
                return TaskUpdateSerializerForResponsible
            return TaskUpdateSerializer
        return TaskDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request_user"] = self.request.user
        return context

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
