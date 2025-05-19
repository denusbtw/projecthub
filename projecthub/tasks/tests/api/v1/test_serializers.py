import pytest

from projecthub.conftest import todo_board
from projecthub.tasks.api.v1.serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    BoardCreateSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)


@pytest.mark.django_db
class TestTaskListSerializer:

    def test_board_is_none(self, task_factory):
        task = task_factory(board=None)
        serializer = TaskListSerializer(task)
        assert serializer.data["board"] is None

    def test_status_is_not_none(self, task_factory, todo_board):
        task = task_factory(board=todo_board)
        serializer = TaskListSerializer(task)
        assert serializer.data["board"] == todo_board.name
        
    def test_create_by_is_nested_serializer(self, task_factory, user):
        task = task_factory(created_by=user)
        serializer = TaskListSerializer(task)
        assert serializer.data["created_by"]["id"] == str(user.id)


@pytest.mark.django_db
class TestTaskDetailSerializer:

    def test_board_is_none(self, task_factory):
        task = task_factory(board=None)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["board"] is None

    def test_board_is_not_none(self, task_factory, todo_board):
        task = task_factory(board=todo_board)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["board"] == todo_board.name

    def test_create_by_is_nested_serializer(self, task_factory, user):
        task = task_factory(created_by=user)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["created_by"]["id"] == str(user.id)

    def test_responsible_is_nested_serializer(self, task_factory, user):
        task = task_factory(responsible=user)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["responsible"]["id"] == str(user.id)


@pytest.mark.django_db
class TestTaskCreateSerializer:

    def test_to_representation_matches_list_serializer_representation(self, project):
        data = {"name": "my task"}
        serializer = TaskCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save(project=project)
        assert serializer.data == TaskListSerializer(task).data


@pytest.mark.django_db
class TestTaskUpdateSerializer:

    def test_no_error_if_empty_data(self, task):
        serializer = TaskUpdateSerializer(task, data={})
        assert serializer.is_valid(), serializer.errors


@pytest.fixture
def data():
    return {"name": "test status", "code": "test_status", "order": 10}


@pytest.mark.django_db
class TestBoardCreateSerializer:

    def test_to_representation_matches_list_serializer_matches(self, tenant, data):
        serializer = BoardCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        board = serializer.save(tenant=tenant)
        assert serializer.data == BoardListSerializer(board).data


@pytest.mark.django_db
class TestBoardUpdateSerializer:

    def test_no_error_if_empty_data(self, todo_board, data):
        serializer = BoardUpdateSerializer(todo_board, data={})
        assert serializer.is_valid(), serializer.errors
