import pytest

from projecthub.attachments.api.serializers import (
    CommentAttachmentWriteSerializer,
    CommentAttachmentReadSerializer
)


@pytest.mark.django_db
class TestCommentAttachmentWriteSerializer:

    def test_to_representation_matches_list_serializer_representation(self, comment,
                                                                      admin_user, file):
        serializer = CommentAttachmentWriteSerializer(data={"file": file})
        assert serializer.is_valid(), serializer.errors
        attachment = serializer.save(uploaded_by=admin_user, comment=comment)
        assert serializer.data == CommentAttachmentReadSerializer(attachment).data