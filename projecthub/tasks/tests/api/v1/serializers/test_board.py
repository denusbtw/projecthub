import pytest

from projecthub.tasks.api.v1.serializers import (
    BoardUpdateSerializer,
)


@pytest.fixture
def data():
    return {"name": "test status", "code": "test_status", "order": 10}


@pytest.mark.django_db
class TestBoardUpdateSerializer:

    def test_no_error_if_empty_data(self, todo_board, data):
        serializer = BoardUpdateSerializer(todo_board, data={})
        assert serializer.is_valid(), serializer.errors
