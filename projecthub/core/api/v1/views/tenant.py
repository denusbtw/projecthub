from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters

from projecthub.core.models import Tenant
from .pagination import TenantPagination
from ..filters import TenantFilterSet
from ..permissions import IsTenantOwnerForCore
from ..serializers import (
    TenantCreateSerializer,
    TenantListSerializer,
    TenantUpdateSerializer,
    TenantDetailSerializer,
)
from ...permissions import ReadOnlyPermission


class TenantListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = TenantPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = TenantFilterSet
    search_fields = ["name", "sub_domain"]
    ordering_fields = ["created_at", "name", "sub_domain", "is_active"]

    def get_queryset(self):
        qs = Tenant.objects.visible_to(self.request.user)
        qs = qs.annotate_role(self.request.user)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenantCreateSerializer
        return TenantListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class TenantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser | IsTenantOwnerForCore | ReadOnlyPermission
    ]

    def get_queryset(self):
        qs = Tenant.objects.visible_to(self.request.user)
        qs = qs.annotate_role(self.request.user)
        return qs

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TenantUpdateSerializer
        return TenantDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
