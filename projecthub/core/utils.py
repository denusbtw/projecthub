from rest_framework.views import exception_handler

from projecthub.comments.models import Comment
from projecthub.projects.models import Project, ProjectMembership
from projecthub.tasks.models import Task


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response["status_code"] = response.status_code

    return response


def get_project_id_from_obj(obj):
    match obj:
        case Project():
            return obj.pk
        case ProjectMembership():
            return obj.project_id
        case Task():
            return obj.project_id
        case Comment():
            return obj.task.project_id
        case _:
            return None


def get_project_id_from_view(view):
    if hasattr(view, "get_project_id"):
        return view.get_project_id()
    else:
        return view.kwargs.get("project_id")


def get_task_id_from_view(view):
    if hasattr(view, "get_task_id"):
        return view.get_task_id()
    else:
        return view.kwargs.get("task_id")
