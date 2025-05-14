from rest_framework import permissions

from projecthub.core.models import TenantMembership


class IsTenantOwnerOrReadOnlyForCore(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return TenantMembership.objects.filter(
            tenant=obj, user=request.user, role=TenantMembership.Role.OWNER
        ).exists()