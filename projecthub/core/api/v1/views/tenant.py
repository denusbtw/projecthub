from django.db.models import OuterRef, Subquery
from rest_framework import generics, permissions

from projecthub.core.models import TenantMembership, Tenant
from .pagination import TenantPagination
from ..permissions import IsTenantOwnerOrReadOnlyForCore
from ..serializers import (
    TenantCreateSerializer,
    TenantListSerializer,
    TenantUpdateSerializer,
    TenantDetailSerializer,
)


class TenantListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = TenantPagination
    permission_classes = [permissions.IsAuthenticated]
    #TODO: add filterset_class
    #TODO: add search by name and sub_domain
    #TODO: add ordering by created_at

    # TODO: move logic into Tenant manager
    def get_queryset(self):
        role_subquery = TenantMembership.objects.filter(
            tenant=OuterRef("pk"), user=self.request.user
        ).values("role")[:1]

        base_queryset = Tenant.objects.annotate(role=Subquery(role_subquery))

        if self.request.user.is_staff:
            return base_queryset

        return base_queryset.filter(members__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenantCreateSerializer
        return TenantListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class TenantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser | IsTenantOwnerOrReadOnlyForCore
    ]

    # TODO: move logic in Tenant manager
    def get_queryset(self):
        role_subquery = TenantMembership.objects.filter(
            tenant=OuterRef("pk"), user=self.request.user
        ).values("role")[:1]

        base_queryset = Tenant.objects.annotate(role=Subquery(role_subquery))
        if self.request.user.is_staff:
            return base_queryset

        return base_queryset.filter(members__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TenantUpdateSerializer
        return TenantDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)