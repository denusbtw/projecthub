from rest_framework.permissions import BasePermission

from projecthub.core.utils import get_tenant_membership
from projecthub.projects.models import ProjectMembership
from projecthub.projects.utils import (
    get_project_membership, resolve_project_id_from_obj,
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


class CanDeleteProjectMembershipPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method != "DELETE":
            return False

        # user can delete self
        if request.user == obj.user:
            return True

        tenant_membership = get_tenant_membership(
            tenant=request.tenant, user=request.user
        )
        project_membership = get_project_membership(
            project_id=obj.project_id, tenant=request.tenant, user=request.user
        )

        # admin, tenant owner and project owner can delete any project member
        if (
                request.user.is_staff
                or (tenant_membership and tenant_membership.is_owner)
                or (project_membership and project_membership.is_owner)
        ):
            return True

        request_user_role_value = self.get_role_value(project_membership.role)
        member_role_value = self.get_role_value(obj.role)
        return request_user_role_value > member_role_value

    def get_role_value(self, role):
        role_values = {
            ProjectMembership.Role.OWNER: 5,
            ProjectMembership.Role.SUPERVISOR: 4,
            ProjectMembership.Role.RESPONSIBLE: 3,
            ProjectMembership.Role.USER: 2,
            ProjectMembership.Role.GUEST: 1,
            ProjectMembership.Role.READER: 0,
        }
        return role_values.get(role)
