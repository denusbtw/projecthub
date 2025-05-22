from projecthub.attachments.models import CommentAttachment, TaskAttachment
from projecthub.comments.models import Comment
from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership, Project
from projecthub.tasks.models import Task


def get_tenant_membership(tenant, user):
    return TenantMembership.objects.filter(tenant=tenant, user=user).first()


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
    elif isinstance(obj, CommentAttachment):
        project_id = obj.comment.task.project_id
    elif isinstance(obj, TaskAttachment):
        project_id = obj.task.project_id

    return project_id


def resolve_project_id_from_view(view):
    if hasattr(view, "get_project_id"):
        return view.get_project_id()
    else:
        return view.kwargs.get("project_id")


def resolve_task_id_from_view(view):
    if hasattr(view, "get_task_id"):
        return view.get_task_id()
    else:
        return view.kwargs.get("task_id")
