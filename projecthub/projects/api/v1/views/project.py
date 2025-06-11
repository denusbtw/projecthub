from django_filters.rest_framework import DjangoFilterBackend
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
