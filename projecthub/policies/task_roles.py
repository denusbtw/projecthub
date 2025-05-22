from rest_framework.generics import get_object_or_404

from projecthub.core.utils import get_task_id_from_view
from projecthub.tasks.models import Task
from .base import BasePolicy


class IsTaskResponsiblePolicy(BasePolicy):
    
    def has_access(self, request, view):
        task_id = get_task_id_from_view(view)
        task = get_object_or_404(Task, project__tenant=request.tenant, pk=task_id)
        return task.responsible == request.user
