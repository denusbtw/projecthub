from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, filters, permissions

from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.core.api.v1.views.pagination import TenantMembershipPagination
from projecthub.core.models import TenantMembership
from projecthub.permissions import (
    ReadOnlyPermission,
    IsTenantOwnerPermission,
    IsSelfDeletePermission,
)
from projecthub.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantMemberPolicy,
)
from ..filters import TenantMembershipFilterSet
from ..serializers import (
    TenantMembershipCreateSerializer,
    TenantMembershipListSerializer,
    TenantMembershipUpdateSerializer,
    TenantMembershipDetailSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="role",
            description="Filter by role",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="creator",
            description="Filter by creator username",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    methods=["GET"],
)
class TenantMembershipListCreateAPIView(
    SecureGenericAPIView, generics.ListCreateAPIView
):
    policy_classes = [
        IsAuthenticatedPolicy & (IsAdminUserPolicy | IsTenantMemberPolicy)
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (permissions.IsAdminUser | IsTenantOwnerPermission | ReadOnlyPermission)
    ]
    pagination_class = TenantMembershipPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = TenantMembershipFilterSet
    search_fields = ("user__username",)
    ordering_fields = ("created_at",)

    def get_queryset(self):
        qs = TenantMembership.objects.for_tenant(self.request.tenant)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenantMembershipCreateSerializer
        return TenantMembershipListSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)


class TenantMembershipRetrieveUpdateDestroyAPIView(
    SecureGenericAPIView, generics.RetrieveUpdateDestroyAPIView
):
    policy_classes = [
        IsAuthenticatedPolicy & (IsAdminUserPolicy | IsTenantMemberPolicy)
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (
            permissions.IsAdminUser
            | IsTenantOwnerPermission
            | IsSelfDeletePermission
            | ReadOnlyPermission
        )
    ]

    def get_queryset(self):
        qs = TenantMembership.objects.for_tenant(self.request.tenant)
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TenantMembershipUpdateSerializer
        return TenantMembershipDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
