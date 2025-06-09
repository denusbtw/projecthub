from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    IsTenantOwnerPermission,
    IsProjectStaffPermission,
    IsTaskResponsiblePermission,
    ReadOnlyPermission,
    IsProjectOwnerPermission,
)
from projecthub.policies import (
    IsAuthenticatedPolicy,
    IsAdminUserPolicy,
    IsTenantOwnerPolicy,
    IsProjectStaffPolicy,
    IsTaskResponsiblePolicy,
)


# TODO::
class AttachmentPagination(PageNumberPagination):
    page_size = 30
    max_page_size = 200
    page_size_query_param = "page_size"


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


class AttachmentRetrieveDestroyAPIView(
    BaseAttachmentAPIView, generics.RetrieveDestroyAPIView
):
    serializer_class = None
    permission_classes = [
        permissions.IsAdminUser
        | IsTenantOwnerPermission
        | IsProjectOwnerPermission
        | ReadOnlyPermission
    ]
