from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer


class AttachmentReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    file = serializers.FileField()
    uploaded_by = UserNestedSerializer()
    uploaded_at = serializers.DateTimeField()


class AttachmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ("file",)

    # TODO
    def validate_file(self, file):
        pass

    def to_representation(self, instance):
        raise NotImplementedError("Subclasses must implement this method.")