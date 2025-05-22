from rest_framework.generics import get_object_or_404

from projecthub.comments.models import Comment
from .base import (
    AttachmentListCreateAPIView,
    AttachmentRetrieveDestroyAPIView,
    BaseAttachmentAPIView
)
from ..serializers import (
    CommentAttachmentWriteSerializer,
    CommentAttachmentReadSerializer
)
from ...models import CommentAttachment


class BaseCommentAttachmentAPIView(BaseAttachmentAPIView):

    def get_queryset(self):
        qs = CommentAttachment.objects.for_tenant(self.request.tenant)
        qs = qs.for_comment(self.kwargs["comment_id"])
        return qs

    # TODO: cache `comment`
    def get_project_id(self):
        comment = self.get_comment()
        return comment.task.project_id

    def get_task_id(self):
        comment = self.get_comment()
        return comment.task_id

    def get_comment(self):
        return get_object_or_404(
            Comment,
            task__project__tenant=self.request.tenant,
            pk=self.kwargs["comment_id"]
        )


class CommentAttachmentListCreateAPIView(BaseCommentAttachmentAPIView,
                                         AttachmentListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentAttachmentWriteSerializer
        return CommentAttachmentReadSerializer

    def perform_create(self, serializer):
        serializer.save(
            comment_id=self.kwargs["comment_id"],
            uploaded_by=self.request.user
        )


class CommentAttachmentRetrieveDestroyAPIView(BaseCommentAttachmentAPIView,
                                              AttachmentRetrieveDestroyAPIView):
    serializer_class = CommentAttachmentReadSerializer
