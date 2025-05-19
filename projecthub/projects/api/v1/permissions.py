from rest_framework.permissions import BasePermission

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