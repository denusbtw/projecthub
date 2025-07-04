from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, permissions
from rest_framework.generics import get_object_or_404

from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    ReadOnlyPermission,
    IsTenantOwnerPermission,
    IsProjectStaffPermission,
)
from projecthub.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantOwnerPolicy,
    IsProjectMemberPolicy,
)
from projecthub.projects.models import ProjectMembership, Project
from .pagination import ProjectMembershipPagination
from ..filters import ProjectMembershipFilterSet
from ..serializers import (
    ProjectMembershipCreateSerializer,
    ProjectMembershipListSerializer,
    ProjectMembershipUpdateSerializer,
    ProjectMembershipDetailSerializer,
)


class ProjectMembershipListCreateAPIView(
    SecureGenericAPIView, generics.ListCreateAPIView
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
            | ReadOnlyPermission
        )
    ]
    pagination_class = ProjectMembershipPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProjectMembershipFilterSet
    search_fields = ["user__username"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        qs = ProjectMembership.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.get_project_id())
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectMembershipCreateSerializer
        return ProjectMembershipListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project = get_object_or_404(Project, pk=self.get_project_id())
        context["project"] = project
        return context

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def get_project_id(self):
        return self.kwargs["project_id"]


class ProjectMembershipRetrieveUpdateDestroyAPIView(
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
            | ReadOnlyPermission
        )
    ]

    def get_queryset(self):
        qs = ProjectMembership.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.get_project_id())
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ProjectMembershipUpdateSerializer
        return ProjectMembershipDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project_id"] = self.get_project_id()
        return context

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_project_id(self):
        return self.kwargs["project_id"]
