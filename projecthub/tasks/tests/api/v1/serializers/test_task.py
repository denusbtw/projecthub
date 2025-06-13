from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from projecthub.projects.models import ProjectMembership
from projecthub.tasks.api.v1.serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskUpdateSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializerForResponsible,
)


@pytest.fixture
def data():
    return {"name": "test name"}


@pytest.fixture
def context(active_project):
    return {"project": active_project}


@pytest.fixture
def valid_start_date(active_project):
    return datetime.combine(active_project.start_date + timedelta(days=30), time.min)


@pytest.fixture
def invalid_start_date(active_project):
    return datetime.combine(active_project.start_date - timedelta(days=30), time.min)


@pytest.fixture
def valid_end_date(active_project):
    return datetime.combine(active_project.end_date - timedelta(days=1), time.min)


@pytest.fixture
def invalid_end_date(active_project):
    return datetime.combine(active_project.end_date + timedelta(days=30), time.min)


@pytest.fixture
def invalid_close_date(active_project):
    return active_project.start_date - timedelta(days=30)


@pytest.fixture
def valid_close_date(active_project):
    return active_project.start_date + timedelta(days=1)


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

    class TestValidateResponsible:

        def test_error_if_responsible_is_not_project_member(self, user, data, context):
            data["responsible"] = user.pk
            serializer = TaskCreateSerializer(data=data, context=context)
            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Responsible must be member of project" in str(exc.value)

        def test_no_error_if_responsible_is_project_user(
            self, data, active_project, project_membership_factory, context
        ):
            membership = project_membership_factory(
                project=active_project, role=ProjectMembership.Role.USER
            )
            data["responsible"] = membership.user_id
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_responsible_is_project_supervisor(
            self, data, active_project, context
        ):
            data["responsible"] = active_project.supervisor_id
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_responsible_is_project_owner(
            self, data, active_project, context
        ):
            data["responsible"] = active_project.owner_id
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

    class TestValidateBoard:

        def test_error_if_board_does_not_belong_to_project(
            self, board_factory, data, context
        ):
            board = board_factory()
            data["board"] = board.pk
            serializer = TaskCreateSerializer(data=data, context=context)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "This board doesn't belong to current project." in str(exc.value)

        def test_no_error_if_board_belong_to_project(
            self, active_project, board_factory, data, context
        ):
            board = board_factory(project=active_project)
            data["board"] = board.pk
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

    class TestValidateStartDate:

        def test_error_if_start_date_before_project_start_date(
            self, invalid_start_date, data, context
        ):
            data["start_date"] = invalid_start_date.isoformat()
            serializer = TaskCreateSerializer(data=data, context=context)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't start before project start." in str(exc.value)

        def test_no_error_if_start_date_after_project_start_date(
            self, valid_start_date, data, context
        ):
            data["start_date"] = valid_start_date.isoformat()
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

    class TestValidateEndDate:

        def test_error_if_end_date_after_project_end_date(
            self, invalid_end_date, data, context
        ):
            data["end_date"] = invalid_end_date.isoformat()
            serializer = TaskCreateSerializer(data=data, context=context)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't end after project end." in str(exc.value)

        def test_no_error_if_end_date_before_project_end_date(
            self, valid_end_date, data, context
        ):
            data["end_date"] = valid_end_date.isoformat()
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

    class TestValidateCloseDate:

        def test_error_if_close_date_before_project_start_date(
            self, invalid_close_date, data, context
        ):
            data["close_date"] = invalid_close_date.isoformat()
            serializer = TaskCreateSerializer(data=data, context=context)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't close before project start." in str(exc.value)

        def test_error_if_close_date_after_project_start_date(
            self, valid_close_date, data, context
        ):
            data["close_date"] = valid_close_date.isoformat()
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

    class TestValidate:

        def test_error_if_project_is_archived(self, archived_project, data):
            context = {"project": archived_project}
            serializer = TaskCreateSerializer(data=data, context=context)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Cannot modify tasks in an archived project." in str(exc.value)

        def test_no_error_if_project_is_pending(self, pending_project, data):
            context = {"project": pending_project}
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_project_is_active(self, active_project, data):
            context = {"project": active_project}
            serializer = TaskCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

    def test_responsible_is_set(self, active_project, data, context):
        responsible = active_project.supervisor
        data["responsible"] = responsible.pk
        serializer = TaskCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save(project=active_project)
        assert task.responsible == responsible


@pytest.mark.django_db
class TestTaskUpdateSerializer:

    class TestValidateResponsible:

        def test_error_if_responsible_is_not_project_member(self, task, user):
            data = {"responsible": user.pk}
            serializer = TaskUpdateSerializer(task, data=data)
            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Responsible must be member of project" in str(exc.value)

        def test_no_error_if_responsible_is_project_user(
            self, task, project_membership_factory
        ):
            membership = project_membership_factory(
                project=task.project, role=ProjectMembership.Role.USER
            )
            data = {"responsible": membership.user_id}
            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_responsible_is_project_supervisor(self, task):
            data = {"responsible": task.project.supervisor_id}
            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_responsible_is_project_owner(self, task):
            data = {"responsible": task.project.owner_id}
            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

    class TestValidateBoard:

        def test_error_if_board_does_not_belong_to_project(self, task, board_factory):
            board = board_factory()
            data = {"board": board.pk}
            serializer = TaskUpdateSerializer(task, data=data)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "This board doesn't belong to current project." in str(exc.value)

        def test_no_error_if_board_belong_to_project(self, task, board_factory):
            board = board_factory(project=task.project)
            data = {"board": board.pk}
            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

    class TestValidateStartDate:

        def test_error_if_start_date_before_project_start_date(
            self, invalid_start_date, task
        ):
            data = {"start_date": invalid_start_date.isoformat()}
            serializer = TaskUpdateSerializer(task, data=data)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't start before project start." in str(exc.value)

        def test_no_error_if_start_date_after_project_start_date(
            self, valid_start_date, task
        ):
            data = {"start_date": valid_start_date.isoformat()}
            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

    class TestValidateEndDate:

        def test_error_if_end_date_after_project_end_date(self, invalid_end_date, task):
            data = {"end_date": invalid_end_date.isoformat()}
            serializer = TaskUpdateSerializer(task, data=data)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't end after project end." in str(exc.value)

        def test_no_error_if_end_date_before_project_end_date(
            self, valid_end_date, task
        ):
            data = {"end_date": valid_end_date.isoformat()}
            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

    class TestValidateCloseDate:

        def test_error_if_close_date_before_task_start_date(
            self, active_project, task_factory
        ):
            task = task_factory(
                project=active_project,
                start_date=timezone.make_aware(
                    datetime.combine(active_project.start_date, time.min)
                    + timedelta(days=10)
                ),
            )
            close_date = task.start_date - timedelta(days=5)
            data = {"close_date": close_date.isoformat()}

            serializer = TaskUpdateSerializer(task, data=data)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't close before task start." in str(exc.value)

        def test_error_if_close_date_before_project_start_date(
            self, active_project, task_factory
        ):
            task = task_factory(project=active_project)
            close_date = active_project.start_date - timedelta(days=30)
            data = {"close_date": close_date.isoformat()}

            serializer = TaskUpdateSerializer(task, data=data)

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Task can't close before project start." in str(exc.value)

        def test_no_error_if_close_date_after_project_start_date(
            self, active_project, task_factory
        ):
            task = task_factory(project=active_project)
            close_date = active_project.start_date + timedelta(days=1)
            data = {"close_date": close_date.isoformat()}

            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_close_date_after_task_start_date(
            self, active_project, task_factory
        ):
            task = task_factory(
                project=active_project,
                start_date=timezone.make_aware(
                    datetime.combine(active_project.start_date, time.min)
                    + timedelta(days=10)
                ),
            )
            close_date = task.start_date + timedelta(days=5)
            data = {"close_date": close_date.isoformat()}

            serializer = TaskUpdateSerializer(task, data=data)
            assert serializer.is_valid(), serializer.errors

    class TestValidate:

        def test_error_if_archived_project(self, task_factory, archived_project):
            task = task_factory(project=archived_project)
            serializer = TaskUpdateSerializer(task, data={})

            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Cannot modify tasks in an archived project." in str(exc.value)

        def test_no_error_if_pending_project(self, task_factory, pending_project):
            task = task_factory(project=pending_project)
            serializer = TaskUpdateSerializer(task, data={})
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_active_project(self, task_factory, active_project):
            task = task_factory(project=active_project)
            serializer = TaskUpdateSerializer(task, data={})
            assert serializer.is_valid(), serializer.errors

    def test_responsible_is_set(self, task):
        responsible = task.project.supervisor
        data = {"responsible": responsible.pk}
        serializer = TaskUpdateSerializer(task, data=data)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save()
        assert task.responsible == responsible


@pytest.mark.django_db
class TestTaskUpdateSerializerForTaskResponsible:

    def test_error_if_board_does_not_belong_to_project(self, task, board_factory):
        board = board_factory()
        data = {"board": board.pk}
        serializer = TaskUpdateSerializerForResponsible(task, data=data)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)
        assert "This board doesn't belong to current project." in str(exc.value)

    def test_no_error_if_board_belongs_to_project(self, task, board_factory):
        board = board_factory(project=task.project)
        data = {"board": board.pk}
        serializer = TaskUpdateSerializerForResponsible(task, data=data)
        assert serializer.is_valid(), serializer.errors

    def test_revoke_is_called_if_board_is_none(self, task, user, mocker):
        mock_revoke = mocker.patch("projecthub.tasks.models.Task.revoke")

        context = {"request_user": user}
        serializer = TaskUpdateSerializerForResponsible(task, data={}, context=context)
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        mock_revoke.assert_called_once_with(user)

    def test_set_board_is_called_if_board(self, task, board_factory, user, mocker):
        mock_set_board = mocker.patch("projecthub.tasks.models.Task.set_board")
        board = board_factory(project=task.project)

        data = {"board": board.pk}
        context = {"request_user": user}
        serializer = TaskUpdateSerializerForResponsible(
            task, data=data, context=context
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        mock_set_board.assert_called_once_with(board, user)
