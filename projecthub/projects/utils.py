from projecthub.comments.models import Comment
from projecthub.projects.models import ProjectMembership, Project
from projecthub.tasks.models import Task


def get_project_membership(project_id, tenant, user):
    return ProjectMembership.objects.filter(
        user=user,
        project__tenant=tenant,
        project_id=project_id,
    ).first()


def resolve_project_id_from_obj(obj):
    project_id = None

    if isinstance(obj, Project):
        project_id = obj.pk
    elif isinstance(obj, ProjectMembership):
        project_id = obj.project_id
    elif isinstance(obj, Task):
        project_id = obj.project_id
    elif isinstance(obj, Comment):
        project_id = obj.task.project_id

    return project_id


def resolve_project_id_from_view(view):
    if hasattr(view, "get_project_id"):
        return view.get_project_id()
    else:
        return view.kwargs.get("project_id")
