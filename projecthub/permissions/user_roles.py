from rest_framework.permissions import BasePermission


class IsSelfDeletePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == "DELETE" and request.user == obj.user
