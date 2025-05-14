from rest_framework import generics, exceptions, permissions

from projecthub.core.api.v1.serializers import (
    TenantMembershipCreateSerializer,
    TenantMembershipListSerializer,
    TenantMembershipUpdateSerializer,
    TenantMembershipDetailSerializer,
)
from projecthub.core.api.v1.views.pagination import TenantMembershipPagination
from projecthub.core.models import TenantMembership


class TenantMembershipListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = TenantMembershipPagination

    # TODO: move into mixin
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).first()

        self._is_staff = request.user.is_staff
        self._tenant_role = getattr(membership, "role", None)
        self._is_tenant_member = bool(membership)
        self._is_tenant_owner = (self._tenant_role == TenantMembership.Role.OWNER)
        self._is_tenant_user = (self._tenant_role == TenantMembership.Role.USER)
        if not (request.user.is_staff or self._is_tenant_member):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move logic into permission classes
    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return

        if self._is_staff or self._is_tenant_owner:
            return

        raise exceptions.PermissionDenied()

    # TODO: move logic into TenantMembership manager
    def get_queryset(self):
        return TenantMembership.objects.filter(tenant=self.request.tenant)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TenantMembershipCreateSerializer
        return TenantMembershipListSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)


class TenantMembershipRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [permissions.IsAuthenticated]

    # TODO: move logic in permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        if request.user.is_staff or self._membership.is_owner:
            return

        is_self_user = request.user == obj.user
        if request.method == "DELETE" and is_self_user:
            return

        raise exceptions.PermissionDenied()

    # TODO: move logic into TenantMembership manager
    def get_queryset(self):
        self._membership = TenantMembership.objects.filter(
            tenant=self.request.tenant,
            user=self.request.user,
        ).first()

        if self.request.user.is_staff or self._membership:
            return TenantMembership.objects.filter(
                tenant=self.request.tenant
            )
        return TenantMembership.objects.none()

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TenantMembershipUpdateSerializer
        return TenantMembershipDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
