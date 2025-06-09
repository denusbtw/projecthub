from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from ..models import Attachment


class AttachmentReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    file = serializers.FileField()
    uploaded_by = UserNestedSerializer()
    uploaded_at = serializers.DateTimeField()

    # TODO: add nested serializers
    task = serializers.UUIDField()
    comment = serializers.UUIDField()


class AttachmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "file", "task", "comment")

    # TODO
    def validate_file(self, file):
        pass
