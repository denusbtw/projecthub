from projecthub.permissions.utils import (
    resolve_project_id_from_view,
    get_project_membership,
    resolve_project_id_from_obj
)
from .base import BasePolicy


class IsProjectMemberPolicy(BasePolicy):

    def has_access(self, request, view):
        project_id = resolve_project_id_from_view(view)
        membership = get_project_membership(
            project_id=project_id, tenant=request.tenant, user=request.user
        )
        return bool(membership)

    def has_object_access(self, request, view, obj):
        project_id = resolve_project_id_from_obj(obj)
        membership = get_project_membership(
            project_id=project_id, tenant=request.tenant, user=request.user
        )
        return bool(membership)


class IsProjectStaffPolicy(BasePolicy):

    def has_access(self, request, view):
        project_id = resolve_project_id_from_view(view)
        membership = get_project_membership(
            project_id=project_id, tenant=request.tenant, user=request.user
        )
        return membership and membership.is_staff
