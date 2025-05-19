from rest_framework.permissions import BasePermission, SAFE_METHODS

from projecthub.core.models import TenantMembership


def get_tenant_membership(tenant, user):
    return TenantMembership.objects.filter(tenant=tenant, user=user).first()


class ReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


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



class IsSelfDeletePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == "DELETE" and request.user == obj.user
