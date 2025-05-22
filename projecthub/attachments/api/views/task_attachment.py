from rest_framework.generics import get_object_or_404

from projecthub.attachments.models import TaskAttachment
from projecthub.tasks.models import Task
from .base import AttachmentListCreateAPIView, AttachmentRetrieveDestroyAPIView, \
    BaseAttachmentAPIView
from ..serializers import TaskAttachmentWriteSerializer, TaskAttachmentReadSerializer


class BaseTaskAttachmentAPIView(BaseAttachmentAPIView):

    def get_queryset(self):
        qs = TaskAttachment.objects.for_tenant(self.request.tenant)
        qs = qs.for_task(self.kwargs["task_id"])
        return qs

    def get_project_id(self):
        task = get_object_or_404(
            Task,
            project__tenant=self.request.tenant,
            pk=self.kwargs["task_id"]
        )
        return task.project_id


class TaskAttachmentListCreateAPIView(BaseTaskAttachmentAPIView,
                                      AttachmentListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskAttachmentWriteSerializer
        return TaskAttachmentReadSerializer

    def perform_create(self, serializer):
        serializer.save(
            task_id=self.kwargs["task_id"],
            uploaded_by=self.request.user
        )


class TaskAttachmentRetrieveDestroyAPIView(BaseTaskAttachmentAPIView,
                                           AttachmentRetrieveDestroyAPIView):
    serializer_class = TaskAttachmentWriteSerializer
