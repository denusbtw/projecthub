from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters

from projecthub.core.api.policies import IsAuthenticatedPolicy, IsAdminUserPolicy, \
    IsTenantMemberPolicy
from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import ReadOnlyPermission, IsTenantOwnerPermission
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
    #TODO: such docstring for each view
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
        & (IsAdminUserPolicy | IsTenantMemberPolicy)
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (permissions.IsAdminUser | IsTenantOwnerPermission | ReadOnlyPermission)
    ]
    pagination_class = BoardPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = BoardFilterSet
    search_fields = ["name", "code"]
    ordering_fields = ["name", "order", "created_at", "is_default"]

    def get_queryset(self):
        return Board.objects.for_tenant(self.request.tenant)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class BoardRetrieveUpdateDestroyAPIView(SecureGenericAPIView,
                                        generics.RetrieveUpdateDestroyAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (IsAdminUserPolicy | IsTenantMemberPolicy)
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (permissions.IsAdminUser | IsTenantOwnerPermission | ReadOnlyPermission)
    ]

    def get_queryset(self):
        return Board.objects.for_tenant(tenant=self.request.tenant)

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
