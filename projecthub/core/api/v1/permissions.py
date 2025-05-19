from rest_framework.permissions import BasePermission

from projecthub.core.models import TenantMembership


class IsTenantOwnerForCore(BasePermission):
    def has_object_permission(self, request, view, obj):
        return TenantMembership.objects.filter(
            tenant=obj, user=request.user, role=TenantMembership.Role.OWNER
        ).exists()