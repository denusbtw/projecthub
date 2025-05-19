from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, exceptions, permissions, filters

from projecthub.core.models import TenantMembership
from projecthub.tasks.models import Board
from .pagination import BoardPagination
from ..filters import BoardFilterSet
from ..serializers import (
    BoardCreateSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    BoardDetailSerializer,
)


class BoardListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = BoardPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = BoardFilterSet
    search_fields = ["name", "code"]
    ordering_fields = ["name", "order", "created_at", "is_default"]

    #TODO:
    def initial(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        # only staff and tenant member have access
        if not (request.user.is_staff or self._tenant_membership):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move into permission classes
    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return

        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
        ):
            return

        raise exceptions.PermissionDenied()

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


class BoardRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    # if task board is 'Todo', he can set board to None (revoke from task) or 'In Progress'
    # if task board is 'In Progress', he can set board to None(revoke), 'Todo', or 'In Review'
    # if task board 'Done' or 'In Review', he can't update board

    def check_permissions(self, request):
        super().check_permissions(request)

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        if not (self.request.user.is_staff or self._tenant_membership):
            raise exceptions.NotFound()

    def get_queryset(self):
        return Board.objects.for_tenant(tenant=self.request.tenant)

    # TODO: move into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        # only admin and tenant owner can PUT, PATCH and DELETE
        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
        ):
            return

        raise exceptions.PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
