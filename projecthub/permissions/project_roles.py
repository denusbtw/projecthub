from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from projecthub.core.utils import get_project_id_from_obj, get_project_id_from_view
from projecthub.projects.models import Project


class IsProjectOwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        # TODO: if obj is Project then use it instead of getting id
        project_id = get_project_id_from_obj(obj)
        project = get_object_or_404(Project, pk=project_id)
        return request.user.id == project.owner_id


class IsProjectStaffPermission(BasePermission):

    def has_permission(self, request, view):
        project_id = get_project_id_from_view(view)
        project = get_object_or_404(Project, pk=project_id)
        return request.user.id in {project.owner_id, project.supervisor_id}

    def has_object_permission(self, request, view, obj):
        project_id = get_project_id_from_obj(obj)
        project = get_object_or_404(Project, pk=project_id)
        return request.user.id in {project.owner_id, project.supervisor_id}
