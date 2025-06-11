import pytest
from django.core import exceptions as django_exceptions
from rest_framework import exceptions as drf_exceptions

from projecthub.tasks.api.v1.serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskUpdateSerializer,
    TaskCreateSerializer,
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

    def test_responsible_is_set(self, project, user):
        data = {"name": "test task", "responsible": user.pk}
        serializer = TaskCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        task = serializer.save(project=project)
        assert task.responsible == user


@pytest.mark.django_db
class TestTaskUpdateSerializer:

    def test_no_error_if_empty_data(self, task):
        serializer = TaskUpdateSerializer(task, data={})
        assert serializer.is_valid(), serializer.errors

    def test_responsible_is_set(self, task, user):
        data = {"responsible": user.pk}
        serializer = TaskUpdateSerializer(task, data=data)
        assert serializer.is_valid(), serializer.errors

        task = serializer.save()
        assert task.responsible == user


@pytest.mark.django_db
class TestTaskUpdateSerializerForTaskResponsible:

    @pytest.mark.parametrize(
        "from_type, to_type, should_succeed",
        [
            (Board.Type.TODO, None, True),
            (Board.Type.TODO, Board.Type.TODO, True),
            (Board.Type.TODO, Board.Type.IN_PROGRESS, True),
            (Board.Type.TODO, Board.Type.IN_REVIEW, False),
            (Board.Type.TODO, Board.Type.DONE, False),
            (Board.Type.IN_PROGRESS, None, True),
            (Board.Type.IN_PROGRESS, Board.Type.TODO, True),
            (Board.Type.IN_PROGRESS, Board.Type.IN_PROGRESS, True),
            (Board.Type.IN_PROGRESS, Board.Type.IN_REVIEW, True),
            (Board.Type.IN_PROGRESS, Board.Type.DONE, False),
            (Board.Type.IN_REVIEW, None, False),
            (Board.Type.IN_REVIEW, Board.Type.TODO, True),
            (Board.Type.IN_REVIEW, Board.Type.IN_PROGRESS, True),
            (Board.Type.IN_REVIEW, Board.Type.IN_REVIEW, True),
            (Board.Type.IN_REVIEW, Board.Type.DONE, False),
            (Board.Type.DONE, None, False),
            (Board.Type.DONE, Board.Type.TODO, False),
            (Board.Type.DONE, Board.Type.IN_PROGRESS, False),
            (Board.Type.DONE, Board.Type.IN_REVIEW, False),
            (Board.Type.DONE, Board.Type.DONE, True),
        ],
    )
    def test_validate_board(
        self, project, board_factory, task_factory, from_type, to_type, should_succeed
    ):
        from_board = board_factory(type=from_type, project=project)
        task = task_factory(board=from_board)

        if to_type:
            if from_type == to_type:
                data = {"board": from_board.pk}
            else:
                new_board = board_factory(type=to_type, project=project)
                data = {"board": new_board.pk}
        else:
            data = {"board": None}

        serializer = TaskUpdateSerializerForResponsible(task, data=data)

        if should_succeed:
            assert serializer.is_valid(), serializer.errors
        else:
            with pytest.raises(
                drf_exceptions.ValidationError, match="You can't move task from"
            ):
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
        serializer = TaskUpdateSerializerForResponsible(
            task, data=data, context=context
        )
        assert serializer.is_valid(), serializer.errors

        mock_set_board = mocker.patch.object(task, "set_board")

        serializer.save()
        mock_set_board.assert_called_once_with(in_progress_board, user)

    def test_update_board_none(
        self, project, todo_board, task_factory, mocker, rf, user
    ):
        request = rf.get("/")
        request.user = user

        task = task_factory(board=todo_board, project=project)

        data = {"board": None}
        context = {"request": request}
        serializer = TaskUpdateSerializerForResponsible(
            task, data=data, context=context
        )
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
