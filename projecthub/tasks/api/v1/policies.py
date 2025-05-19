from rest_framework.generics import get_object_or_404

from projecthub.core.api.policies import BasePolicy
from projecthub.tasks.models import Task


def resolve_task_id_from_view(view):
    if hasattr(view, "get_task_id"):
        return view.get_task_id()
    else:
        return view.kwargs.get("task_id")


class IsTaskResponsiblePolicy(BasePolicy):
    def has_access(self, request, view):
        task_id = resolve_task_id_from_view(view)
        task = get_object_or_404(Task, project__tenant=request.tenant, pk=task_id)
        return task.responsible == request.user