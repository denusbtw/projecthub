from projecthub.core.utils import get_project_id_from_obj, get_project_id_from_view
from projecthub.projects.models import ProjectMembership
from .base import BasePolicy


class IsProjectMemberPolicy(BasePolicy):

    def has_access(self, request, view):
        project_id = get_project_id_from_view(view)
        return ProjectMembership.objects.filter(
            project_id=project_id, project__tenant=request.tenant, user=request.user
        ).exists()

    def has_object_access(self, request, view, obj):
        project_id = get_project_id_from_obj(obj)
        return ProjectMembership.objects.filter(
            project_id=project_id, project__tenant=request.tenant, user=request.user
        ).exists()


class IsProjectStaffPolicy(BasePolicy):

    def has_access(self, request, view):
        project_id = get_project_id_from_view(view)
        membership = ProjectMembership.objects.filter(
            project_id=project_id, project__tenant=request.tenant, user=request.user
        ).first()
        return membership and membership.is_staff
