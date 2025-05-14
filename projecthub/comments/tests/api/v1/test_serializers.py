import pytest

from projecthub.comments.api.v1.serializers import (
    CommentCreateSerializer, CommentListSerializer
)


@pytest.mark.django_db
class TestCommentCreateSerializer:

    def test_representation_matches_list_serializer_representation(self, task, user):
        data = {"body": "test comment"}
        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        comment = serializer.save(task=task, created_by=user)
        assert serializer.data == CommentListSerializer(comment).data