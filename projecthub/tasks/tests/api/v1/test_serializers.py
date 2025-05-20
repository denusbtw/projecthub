import pytest
from django.core import exceptions as django_exceptions
from rest_framework import exceptions as drf_exceptions

from projecthub.conftest import todo_board
from projecthub.tasks.api.v1.serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    BoardCreateSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    TaskUpdateSerializerForResponsible,
)
from projecthub.tasks.models import Board


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


@pytest.mark.django_db
class TestTaskUpdateSerializerForTaskResponsible:

    @pytest.mark.parametrize("from_code, to_code, should_succeed", [
        (Board.TODO, None, True),
        (Board.TODO, Board.TODO, True),
        (Board.TODO, Board.IN_PROGRESS, True),
        (Board.TODO, Board.IN_REVIEW, False),
        (Board.TODO, Board.DONE, False),
        (Board.IN_PROGRESS, None, True),
        (Board.IN_PROGRESS, Board.TODO, True),
        (Board.IN_PROGRESS, Board.IN_PROGRESS, True),
        (Board.IN_PROGRESS, Board.IN_REVIEW, True),
        (Board.IN_PROGRESS, Board.DONE, False),
        (Board.IN_REVIEW, None, False),
        (Board.IN_REVIEW, Board.TODO, True),
        (Board.IN_REVIEW, Board.IN_PROGRESS, True),
        (Board.IN_REVIEW, Board.IN_REVIEW, True),
        (Board.IN_REVIEW, Board.DONE, False),
        (Board.DONE, None, False),
        (Board.DONE, Board.TODO, False),
        (Board.DONE, Board.IN_PROGRESS, False),
        (Board.DONE, Board.IN_REVIEW, False),
        (Board.DONE, Board.DONE, True),
    ])
    def test_validate_board(
            self, tenant, board_factory, task_factory,
            from_code, to_code, should_succeed
    ):
        from_board = board_factory(code=from_code, tenant=tenant)
        task = task_factory(board=from_board)

        if to_code:
            if from_code == to_code:
                data = {"board": from_board.pk}
            else:
                new_board = board_factory(code=to_code, tenant=tenant)
                data = {"board": new_board.pk}
        else:
            data = {"board": None}

        serializer = TaskUpdateSerializerForResponsible(task, data=data)

        if should_succeed:
            assert serializer.is_valid(), serializer.errors
        else:
            with pytest.raises(drf_exceptions.ValidationError, match="You can't move task from"):
                serializer.is_valid(raise_exception=True)

    def test_update_same_board(self, project, task_factory, todo_board, mocker):
        task = task_factory(board=todo_board, project=project)

        data = {"board": todo_board.pk}
        serializer = TaskUpdateSerializerForResponsible(task, data=data)
        assert serializer.is_valid(), serializer.errors

        mock_set_board = mocker.patch.object(task, "set_board")
        mock_revoke = mocker.patch.object(task, "revoke")

        serializer.save()
        mock_set_board.assert_not_called()
        mock_revoke.assert_not_called()

    def test_update_new_board(
            self, project, task_factory, todo_board, in_progress_board, mocker, rf, user
    ):
        request = rf.get("/")
        request.user = user

        task = task_factory(board=todo_board, project=project)

        data = {"board": in_progress_board.pk}
        context = {"request": request}
        serializer = TaskUpdateSerializerForResponsible(task, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

        mock_set_board = mocker.patch.object(task, "set_board")

        serializer.save()
        mock_set_board.assert_called_once_with(in_progress_board.code, user)

    def test_update_board_none(self, project, todo_board, task_factory, mocker, rf, user):
        request = rf.get("/")
        request.user = user

        task = task_factory(board=todo_board, project=project)

        data = {"board": None}
        context = {"request": request}
        serializer = TaskUpdateSerializerForResponsible(task, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

        mock_revoke = mocker.patch.object(task, "revoke")

        serializer.save()
        mock_revoke.assert_called_once_with(user)

    def test_error_if_no_request_in_context(
            self, project, todo_board, task_factory, mocker
    ):
        task = task_factory(board=todo_board, project=project)
        data = {"board": None}

        serializer = TaskUpdateSerializerForResponsible(task, data=data, context={})
        assert serializer.is_valid(), serializer.errors

        with pytest.raises(django_exceptions.ValidationError):
            serializer.save()


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
