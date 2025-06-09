from rest_framework.permissions import BasePermission

from projecthub.core.models import TenantMembership


class IsTenantOwnerForCore(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsTenantMemberPermission(BasePermission):

    def has_permission(self, request, view):
        tenant_membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        )
        return request.tenant.owner == request.user or tenant_membership.exists()

    def has_object_permission(self, request, view, obj):
        tenant_membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        )
        return request.tenant.owner == request.user or tenant_membership.exists()


class IsTenantOwnerPermission(BasePermission):

    def has_permission(self, request, view):
        return request.tenant.owner == request.user
