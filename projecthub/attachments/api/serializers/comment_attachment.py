from rest_framework import serializers

from projecthub.attachments.models import CommentAttachment
from .base import AttachmentReadSerializer, AttachmentWriteSerializer


class CommentAttachmentReadSerializer(AttachmentReadSerializer):
    comment = serializers.UUIDField()


class CommentAttachmentWriteSerializer(AttachmentWriteSerializer):
    class Meta(AttachmentWriteSerializer.Meta):
        model = CommentAttachment

    def to_representation(self, instance):
        return CommentAttachmentReadSerializer(instance, context=self.context).data
