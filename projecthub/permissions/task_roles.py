from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from projecthub.core.utils import get_task_id_from_view
from projecthub.tasks.models import Task


class TaskResponsibleHasNoDeletePermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.responsible != request.user:
            return True

        return request.method != "DELETE"


class IsTaskResponsiblePermission(BasePermission):

    def has_permission(self, request, view):
        task_id = get_task_id_from_view(view)
        task = get_object_or_404(Task, project__tenant=request.tenant, pk=task_id)
        return task.responsible == request.user
