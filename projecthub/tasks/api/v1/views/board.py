from django_filters.rest_framework import DjangoFilterBackend
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
from ..filters import BoardFilterSet
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
        - GET: admin, owner and members of tenant
        - POST: admin and tenant owner
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
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BoardFilterSet
    search_fields = ["name", "type"]
    ordering_fields = ["name", "order", "created_at"]

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.get_project_id())
        return Board.objects.for_project(project)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def get_project_id(self):
        return self.kwargs["project_id"]


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
        project = get_object_or_404(Project, pk=self.get_project_id())
        return Board.objects.for_project(project=project)

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_project_id(self):
        return self.kwargs["project_id"]
