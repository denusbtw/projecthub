from projecthub.core.models import TenantMembership
from .base import BasePolicy


class IsTenantMemberPolicy(BasePolicy):

    def has_access(self, request, view):
        return TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).exists()


class IsTenantOwnerPolicy(BasePolicy):

    def has_access(self, request, view):
        membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).first()
        return membership and membership.is_owner
