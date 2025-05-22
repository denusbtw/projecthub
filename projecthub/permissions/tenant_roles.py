from rest_framework.permissions import BasePermission

from projecthub.core.models import TenantMembership


class IsTenantOwnerForCore(BasePermission):

    def has_object_permission(self, request, view, obj):
        return TenantMembership.objects.filter(
            tenant=obj, user=request.user, role=TenantMembership.Role.OWNER
        ).exists()


class IsTenantMemberPermission(BasePermission):

    def has_permission(self, request, view):
        return TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).exists()

    def has_object_permission(self, request, view, obj):
        return TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).exists()


class IsTenantOwnerPermission(BasePermission):

    def has_permission(self, request, view):
        membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).first()
        return membership and membership.is_owner
