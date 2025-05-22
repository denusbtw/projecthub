from rest_framework.permissions import BasePermission

from projecthub.core.models import TenantMembership
from .utils import get_tenant_membership


class IsTenantOwnerForCore(BasePermission):
    def has_object_permission(self, request, view, obj):
        return TenantMembership.objects.filter(
            tenant=obj, user=request.user, role=TenantMembership.Role.OWNER
        ).exists()


class IsTenantMemberPermission(BasePermission):
    def has_permission(self, request, view):
        membership = get_tenant_membership(
            tenant=request.tenant, user=request.user
        )
        return bool(membership)

    def has_object_permission(self, request, view, obj):
        membership = get_tenant_membership(
            tenant=request.tenant, user=request.user
        )
        return bool(membership)


class IsTenantOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        membership = get_tenant_membership(
            tenant=request.tenant, user=request.user
        )
        return membership and membership.is_owner
