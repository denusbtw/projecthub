import pytest
from rest_framework.exceptions import ValidationError

from projecthub.tasks.api.v1.serializers import (
    BoardUpdateSerializer,
    BoardCreateSerializer,
)


@pytest.fixture
def data():
    return {"name": "test status", "order": 10}


@pytest.mark.django_db
class TestBoardCreateSerializer:

    @pytest.mark.parametrize(
        "project_fixture_name",
        [
            "active_project",
            "pending_project",
            "archived_project",
        ],
    )
    def test_error_if_project_is_archived(self, data, project_fixture_name, request):
        project = request.getfixturevalue(project_fixture_name)
        context = {"project": project}

        serializer = BoardCreateSerializer(data=data, context=context)
        if project.is_archived:
            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "for archived project" in str(exc.value)
        else:
            assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestBoardUpdateSerializer:

    def test_no_error_if_empty_data(self, todo_board, data):
        serializer = BoardUpdateSerializer(todo_board, data={})
        assert serializer.is_valid(), serializer.errors
