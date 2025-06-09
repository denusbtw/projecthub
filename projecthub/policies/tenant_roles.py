from projecthub.core.models import TenantMembership
from .base import BasePolicy


class IsTenantMemberPolicy(BasePolicy):

    def has_access(self, request, view):
        tenant_membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        )
        return request.tenant.owner == request.user or tenant_membership.exists()


class IsTenantOwnerPolicy(BasePolicy):

    def has_access(self, request, view):
        return request.tenant.owner == request.user
