from rest_framework import generics, permissions, filters
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
from projecthub.projects.models import Project
from projecthub.tasks.models import Board
from .pagination import BoardPagination
from ..serializers import (
    BoardCreateSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    BoardDetailSerializer,
)


class BoardListCreateAPIView(SecureGenericAPIView, generics.ListCreateAPIView):
    # TODO: such docstring for each view
    """
    API view for listing and creating boards.

    Access:
        - Only staff and members of current tenant

    Permissions:
        - GET: admin, tenant owner, owner, supervisor and members of project
        - POST: admin, tenant owner, project owner, project supervisor
    """
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
    pagination_class = BoardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name",)
    ordering_fields = ("order",)

    def get_queryset(self):
        project = self.get_project()
        return Board.objects.for_project(project)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project"] = self.get_project()
        return context

    def perform_create(self, serializer):
        serializer.save(project_id=self.get_project_id())

    def get_project_id(self):
        return self.kwargs["project_id"]

    # TODO: додати кешування project в self._cached_project
    def get_project(self):
        return get_object_or_404(Project, pk=self.get_project_id())


class BoardRetrieveUpdateDestroyAPIView(
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
        project = self.get_project()
        return Board.objects.for_project(project=project)

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_project_id(self):
        return self.kwargs["project_id"]

    def get_project(self):
        return get_object_or_404(Project, pk=self.get_project_id())
