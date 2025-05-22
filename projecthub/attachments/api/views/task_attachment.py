from rest_framework.generics import get_object_or_404

from projecthub.attachments.models import TaskAttachment
from projecthub.tasks.models import Task
from .base import AttachmentListCreateAPIView, AttachmentRetrieveDestroyAPIView, \
    BaseAttachmentAPIView
from ..serializers import TaskAttachmentWriteSerializer, TaskAttachmentReadSerializer


class BaseTaskAttachmentAPIView(BaseAttachmentAPIView):

    def get_queryset(self):
        return TaskAttachment.objects.filter(
            task__project__tenant=self.request.tenant,
            task_id=self.kwargs["task_id"]
        )

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
