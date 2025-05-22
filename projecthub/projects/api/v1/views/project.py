from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, permissions

from projecthub.core.api.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantMemberPolicy,
    IsTenantOwnerPolicy,
)
from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    ReadOnlyPermission,
    IsTenantOwnerPermission,
    IsProjectOwnerPermission
)
from projecthub.projects.api.v1.filters import ProjectFilterSet
from projecthub.projects.api.v1.policies import IsProjectMemberPolicy
from projecthub.projects.api.v1.serializers import (
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
    ProjectDetailSerializer,
)
from projecthub.projects.api.v1.views.pagination import ProjectPagination
from projecthub.projects.models import Project


class ProjectListCreateAPIView(SecureGenericAPIView, generics.ListCreateAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (IsAdminUserPolicy | IsTenantMemberPolicy)
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (permissions.IsAdminUser | IsTenantOwnerPermission | ReadOnlyPermission)
    ]
    pagination_class = ProjectPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProjectFilterSet
    search_fields = ["name"] #TODO: add search by description
    ordering_fields = ["name", "created_at", "start_date", "end_date", "close_date"]

    def get_queryset(self):
        qs = Project.objects.for_tenant(self.request.tenant)
        qs = qs.visible_to(user=self.request.user, tenant=self.request.tenant)
        qs = qs.annotate_role(self.request.user)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectListSerializer

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class ProjectRetrieveUpdateDestroyAPIView(SecureGenericAPIView,
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
            | IsProjectOwnerPermission
            | ReadOnlyPermission
        )
    ]

    def get_queryset(self):
        qs = Project.objects.for_tenant(self.request.tenant)
        qs = qs.visible_to(user=self.request.user, tenant=self.request.tenant)
        qs = qs.annotate_role(self.request.user)
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_project_id(self):
        return self.kwargs["pk"]
