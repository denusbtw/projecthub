from rest_framework.permissions import BasePermission

from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership
from projecthub.projects.utils import get_role_value
from .utils import (
    resolve_project_id_from_obj,
    get_project_membership,
    resolve_project_id_from_view
)


class IsProjectOwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        project_id = resolve_project_id_from_obj(obj)
        membership = get_project_membership(
            project_id=project_id, tenant=request.tenant, user=request.user
        )
        return membership and membership.is_owner


class IsProjectStaffPermission(BasePermission):

    def has_permission(self, request, view):
        project_id = resolve_project_id_from_view(view)
        membership = get_project_membership(
            project_id=project_id, tenant=request.tenant, user=request.user
        )
        return membership and membership.is_staff

    def has_object_permission(self, request, view, obj):
        project_id = resolve_project_id_from_obj(obj)
        membership = get_project_membership(
            project_id=project_id, tenant=request.tenant, user=request.user
        )
        return membership and membership.is_staff


class CanManageProjectMembershipPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Determines whether the requesting user has permission to delete a specific project membership.

        Rules:
        - A user can always delete their own membership.
        - Admins, tenant owners, and project owners can delete any project member.
        - A project supervisor can delete:
            - themselves,
            - members with roles: responsible, user, guest, reader.
        - A project responsible can delete:
            - themselves,
            - members with roles: user, guest, reader.
        - Deletion is only allowed via the DELETE method. All other methods are denied by this permission.
        """
        if request.method not in {"PUT", "PATCH", "DELETE"}:
            return False

        tenant = request.tenant
        project = obj.project

        if (
                request.user == obj.user
                or request.user.is_staff
                or tenant.has_role(TenantMembership.Role.OWNER, request.user)
                or project.has_role(ProjectMembership.Role.OWNER, request.user)
        ):
            return True

        request_user_role = project.get_role_of(request.user)
        if request_user_role not in ProjectMembership.STAFF_USER_ROLES:
            return False

        return get_role_value(request_user_role) >= get_role_value(obj.role)
