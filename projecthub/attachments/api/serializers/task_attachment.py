from rest_framework import serializers

from projecthub.attachments.models import TaskAttachment
from .base import AttachmentReadSerializer, AttachmentWriteSerializer


class TaskAttachmentReadSerializer(AttachmentReadSerializer):
    task = serializers.UUIDField()


class TaskAttachmentWriteSerializer(AttachmentWriteSerializer):
    class Meta(AttachmentWriteSerializer.Meta):
        model = TaskAttachment

    def to_representation(self, instance):
        return TaskAttachmentReadSerializer(instance, context=self.context).data
