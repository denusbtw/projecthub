from projecthub.core.utils import get_tenant_membership
from .base import BasePolicy


class IsTenantMemberPolicy(BasePolicy):

    def has_access(self, request, view):
        membership = get_tenant_membership(
            tenant=request.tenant, user=request.user
        )
        return bool(membership)


class IsTenantOwnerPolicy(BasePolicy):

    def has_access(self, request, view):
        membership = get_tenant_membership(
            tenant=request.tenant, user=request.user
        )
        return membership and membership.is_owner
