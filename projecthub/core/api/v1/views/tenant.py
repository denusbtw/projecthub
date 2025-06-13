from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, permissions, filters

from projecthub.core.models import Tenant
from projecthub.permissions import ReadOnlyPermission, IsTenantOwnerForCore
from .pagination import TenantPagination
from ..filters import TenantFilterSet
from ..serializers import (
    TenantCreateSerializer,
    TenantListSerializer,
    TenantUpdateSerializer,
    TenantDetailSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter tenants by active status.",
        ),
        OpenApiParameter(
            name="creator",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Case-insensitive partial match on the creator's username.",
        ),
        OpenApiParameter(
            name="owner",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Case-insensitive partial match on the owner's username.",
        ),
        OpenApiParameter(
            name="user",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Case-insensitive partial match on usernames of users with 'user' role in tenant memberships.",
        ),
    ],
    methods=["GET"],
)
class TenantListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = TenantPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = TenantFilterSet
    search_fields = ("name", "sub_domain")
    ordering_fields = ("created_at", "name", "sub_domain", "is_active")

    def get_queryset(self):
        qs = Tenant.objects.visible_to(self.request.user)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenantCreateSerializer
        return TenantListSerializer

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class TenantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser | IsTenantOwnerForCore | ReadOnlyPermission,
    ]

    def get_queryset(self):
        qs = Tenant.objects.visible_to(self.request.user)
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TenantUpdateSerializer
        return TenantDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
