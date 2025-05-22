from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.generics import get_object_or_404

from projecthub.core.api.policies import IsAuthenticatedPolicy, IsAdminUserPolicy, \
    IsTenantOwnerPolicy
from projecthub.core.api.v1.views.base import SecureGenericAPIView
from projecthub.permissions import (
    IsTenantOwnerPermission,
    IsProjectOwnerPermission,
    IsCommentAuthorPermission
)
from projecthub.projects.api.v1.policies import IsProjectStaffPolicy
from projecthub.tasks.api.v1.policies import IsTaskResponsiblePolicy
from projecthub.tasks.models import Task
from .filters import CommentFilterSet
from .pagination import CommentPagination
from .serializers import CommentListSerializer, CommentCreateSerializer
from ...models import Comment


class CommentListCreateAPIView(SecureGenericAPIView, generics.ListCreateAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (
            IsAdminUserPolicy
            | IsTenantOwnerPolicy
            | IsProjectStaffPolicy
            | IsTaskResponsiblePolicy
        )
    ]
    pagination_class = CommentPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = CommentFilterSet
    search_fields = ["body"]
    ordering_fields = ["parent", "created_at"]

    def get_queryset(self):
        qs = Comment.objects.for_tenant(self.request.tenant)
        qs = qs.for_task(self.kwargs["task_id"])
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentListSerializer

    def perform_create(self, serializer):
        serializer.save(task_id=self.kwargs["task_id"], created_by=self.request.user)

    def get_project_id(self):
        task = get_object_or_404(
            Task, project__tenant=self.request.tenant, pk=self.kwargs["task_id"]
        )
        return task.project_id


class CommentDestroyAPIView(SecureGenericAPIView, generics.DestroyAPIView):
    policy_classes = [
        IsAuthenticatedPolicy
        & (
            IsAdminUserPolicy
            | IsTenantOwnerPolicy
            | IsProjectStaffPolicy
            | IsTaskResponsiblePolicy
        )
    ]
    permission_classes = [
        permissions.IsAuthenticated
        & (
            permissions.IsAdminUser
            | IsTenantOwnerPermission
            | IsProjectOwnerPermission
            | IsCommentAuthorPermission
        )
    ]

    def get_queryset(self):
        qs = Comment.objects.for_tenant(self.request.tenant)
        qs = qs.for_task(self.kwargs["task_id"])
        return qs

    def get_project_id(self):
        task = get_object_or_404(
            Task, project__tenant=self.request.tenant, pk=self.kwargs["task_id"]
        )
        return task.project_id
