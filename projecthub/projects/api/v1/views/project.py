from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, filters, permissions

from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    ReadOnlyPermission,
    IsTenantOwnerPermission,
    IsProjectOwnerPermission,
)
from projecthub.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantMemberPolicy,
    IsTenantOwnerPolicy,
    IsProjectMemberPolicy,
)
from projecthub.projects.models import Project
from .pagination import ProjectPagination
from ..filters import ProjectFilterSet
from ..serializers import (
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
    ProjectDetailSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            description="Filter by project status (multiple allowed)",
            required=False,
            many=True,
        ),
        OpenApiParameter(
            name="start_date_after",
            type=OpenApiTypes.DATE,
            description="Filter projects with start_date >= this value",
            required=False,
        ),
        OpenApiParameter(
            name="start_date_before",
            type=OpenApiTypes.DATE,
            description="Filter projects with start_date <= this value",
            required=False,
        ),
        OpenApiParameter(
            name="end_date_after",
            type=OpenApiTypes.DATE,
            description="Filter projects with end_date >= this value",
            required=False,
        ),
        OpenApiParameter(
            name="end_date_before",
            type=OpenApiTypes.DATE,
            description="Filter projects with end_date <= this value",
            required=False,
        ),
        OpenApiParameter(
            name="close_date_after",
            type=OpenApiTypes.DATE,
            description="Filter projects with close_date >= this value",
            required=False,
        ),
        OpenApiParameter(
            name="close_date_before",
            type=OpenApiTypes.DATE,
            description="Filter projects with close_date <= this value",
            required=False,
        ),
        OpenApiParameter(
            name="creator",
            type=OpenApiTypes.STR,
            description="Filter projects by creator username (partial match)",
            required=False,
        ),
        OpenApiParameter(
            name="owner",
            type=OpenApiTypes.STR,
            description="Filter projects by owner username (partial match)",
            required=False,
        ),
        OpenApiParameter(
            name="supervisor",
            type=OpenApiTypes.STR,
            description="Filter projects by supervisor username (partial match)",
            required=False,
        ),
        OpenApiParameter(
            name="responsible",
            type=OpenApiTypes.STR,
            description="Filter projects by responsible username (partial match)",
            required=False,
        ),
    ],
    methods=["GET"],
)
class ProjectListCreateAPIView(SecureGenericAPIView, generics.ListCreateAPIView):
    policy_classes = [
        IsAuthenticatedPolicy & (IsAdminUserPolicy | IsTenantMemberPolicy)
    ]
    permission_classes = [
        permissions.IsAuthenticated & (IsTenantOwnerPermission | ReadOnlyPermission)
    ]
    pagination_class = ProjectPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProjectFilterSet
    search_fields = ("name",)  # TODO: add search by description
    ordering_fields = ("name", "created_at", "start_date", "end_date", "close_date")

    def get_queryset(self):
        qs = Project.objects.for_tenant(self.request.tenant)
        qs = qs.visible_to(user=self.request.user, tenant=self.request.tenant)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["tenant"] = self.request.tenant
        context["request_user"] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant,
            responsible=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class ProjectRetrieveUpdateDestroyAPIView(
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
            | IsProjectOwnerPermission
            | ReadOnlyPermission
        )
    ]

    def get_queryset(self):
        qs = Project.objects.for_tenant(self.request.tenant)
        qs = qs.visible_to(user=self.request.user, tenant=self.request.tenant)
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["tenant"] = self.request.tenant
        return context

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_project_id(self):
        return self.kwargs["pk"]
