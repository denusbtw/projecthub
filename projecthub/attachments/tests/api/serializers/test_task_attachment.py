import pytest

from projecthub.attachments.api.serializers import (
    TaskAttachmentWriteSerializer,
    TaskAttachmentReadSerializer
)


@pytest.mark.django_db
class TestTaskAttachmentWriteSerializer:

    def test_to_representation_matches_list_serializer_representation(self, task,
                                                                      admin_user, file):
        serializer = TaskAttachmentWriteSerializer(data={"file": file})
        assert serializer.is_valid(), serializer.errors
        attachment = serializer.save(uploaded_by=admin_user, task=task)
        assert serializer.data == TaskAttachmentReadSerializer(attachment).data