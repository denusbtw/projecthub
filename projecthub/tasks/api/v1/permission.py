from rest_framework.permissions import BasePermission


class TaskResponsibleHasNoDeletePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.responsible != request.user:
            return True

        return request.method != "DELETE"