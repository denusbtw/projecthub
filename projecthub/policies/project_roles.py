from rest_framework.generics import get_object_or_404

from projecthub.core.utils import get_project_id_from_obj, get_project_id_from_view
from projecthub.projects.models import ProjectMembership, Project
from .base import BasePolicy


class IsProjectMemberPolicy(BasePolicy):

    def has_access(self, request, view):
        project_id = get_project_id_from_view(view)
        project = get_object_or_404(Project, pk=project_id)

        project_membership = ProjectMembership.objects.filter(
            project_id=project_id, project__tenant=request.tenant, user=request.user
        )

        has_access = (
            request.user.id in {project.owner_id, project.supervisor_id}
            or project_membership.exists()
        )
        return has_access

    def has_object_access(self, request, view, obj):
        project_id = get_project_id_from_obj(obj)
        project = get_object_or_404(Project, pk=project_id)

        project_membership = ProjectMembership.objects.filter(
            project_id=project_id, project__tenant=request.tenant, user=request.user
        )

        return (
            request.user.id in {project.owner_id, project.supervisor_id}
            or project_membership.exists()
        )


class IsProjectStaffPolicy(BasePolicy):

    def has_access(self, request, view):
        project_id = get_project_id_from_view(view)
        project = get_object_or_404(Project, pk=project_id)
        return request.user.id in {project.owner_id, project.supervisor_id}
