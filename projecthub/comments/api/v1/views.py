from rest_framework import generics, exceptions, permissions
from rest_framework.generics import get_object_or_404

from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership
from projecthub.tasks.models import Task
from .pagination import CommentPagination
from .serializers import CommentListSerializer, CommentCreateSerializer
from ...models import Comment


class CommentListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = CommentPagination
    permission_classes = [permissions.IsAuthenticated]
    #TODO: add custom filterset_class
    #TODO: add search by body
    #TODO: add ordering by created_at and parent

    # TODO: move logic into mixin
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._task = get_object_or_404(
            Task, pk=kwargs["task_id"], project__tenant=request.tenant
        )

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=request.tenant, user=request.user
        ).first()
        self._project_membership = ProjectMembership.objects.filter(
            project_id=self._task.project_id, user=request.user
        ).first()
        self._is_task_responsible = (self._task.responsible_id == request.user.pk)

        if not (
            request.user.is_staff
            or (self._tenant_membership and self._tenant_membership.is_owner)
            or (self._project_membership and self._project_membership.is_staff)
            or self._is_task_responsible
        ):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move logic into Comment manager
    def get_queryset(self):
        return Comment.objects.filter(
            task__project__tenant=self.request.tenant, task_id=self.kwargs["task_id"]
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentListSerializer

    def perform_create(self, serializer):
        serializer.save(task_id=self.kwargs["task_id"], created_by=self.request.user)


class CommentDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    # TODO: move into mixin
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._task = get_object_or_404(
            Task, project__tenant=self.request.tenant, pk=self.kwargs["task_id"]
        )

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()
        self._project_membership = ProjectMembership.objects.filter(
            project_id=self._task.project_id, user=self.request.user
        ).first()
        self._is_task_responsible = (self._task.responsible_id == self.request.user.pk)

        # admin, tenant owner, project staff and task responsible have access
        if not (
            request.user.is_staff
            or (self._tenant_membership and self._tenant_membership.is_owner)
            or (self._project_membership and self._project_membership.is_staff)
            or self._is_task_responsible
        ):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move logic into Comment manager
    def get_queryset(self):
        return Comment.objects.filter(
            task__project__tenant=self.request.tenant,
            task_id=self.kwargs["task_id"]
        )

    # TODO: move into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        # staff, tenant owner, project owner and comment author can PUT, PATCH, DELETE
        self._is_comment_author = (obj.created_by_id == request.user.pk)
        if (
            request.user.is_staff
            or (self._tenant_membership and self._tenant_membership.is_owner)
            or (self._project_membership and self._project_membership.is_owner)
            or self._is_comment_author
        ):
            return

        raise exceptions.PermissionDenied()