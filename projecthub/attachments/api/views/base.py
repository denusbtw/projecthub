from rest_framework import permissions, generics

from projecthub.attachments.api.views.pagination import AttachmentPagination
from projecthub.core.api.permissions import IsTenantOwnerPermission, ReadOnlyPermission
from projecthub.core.api.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantOwnerPolicy
)
from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.projects.api.v1.permissions import (
    IsProjectStaffPermission,
    IsProjectOwnerPermission
)
from projecthub.projects.api.v1.policies import IsProjectStaffPolicy
from projecthub.tasks.api.v1.permission import IsTaskResponsiblePermission
from projecthub.tasks.api.v1.policies import IsTaskResponsiblePolicy


class BaseAttachmentAPIView(SecureGenericAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (
            IsAdminUserPolicy
            | IsTenantOwnerPolicy
            | IsProjectStaffPolicy
            | IsTaskResponsiblePolicy
        )
    ]

    def get_queryset(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_project_id(self):
        raise NotImplementedError("Subclasses must implement this method.")


class AttachmentListCreateAPIView(BaseAttachmentAPIView, generics.ListCreateAPIView):
    pagination_class = AttachmentPagination
    permission_classes = [
        permissions.IsAdminUser
        | IsTenantOwnerPermission
        | IsProjectStaffPermission
        | IsTaskResponsiblePermission
        | ReadOnlyPermission
    ]

    def get_serializer_class(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def perform_create(self, serializer):
        raise NotImplementedError("Subclasses must implement this method.")


class AttachmentRetrieveDestroyAPIView(BaseAttachmentAPIView,
                                       generics.RetrieveDestroyAPIView):
    serializer_class = None
    permission_classes = [
        permissions.IsAdminUser
        | IsTenantOwnerPermission
        | IsProjectOwnerPermission
        | ReadOnlyPermission
    ]
