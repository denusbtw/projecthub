from rest_framework import serializers

from projecthub.comments.models import Comment
from projecthub.core.api.v1.serializers.base import UserNestedSerializer


class CommentListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    body = serializers.CharField()
    created_by = UserNestedSerializer()
    parent = serializers.PrimaryKeyRelatedField(read_only=True)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body", "parent")

    def to_representation(self, instance):
        return CommentListSerializer(instance, context=self.context).data