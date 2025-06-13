from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from projecthub.tasks.models import Task, Board


@pytest.mark.django_db
class TestTask:

    def test_error_if_start_date_after_end_date(self, task_factory):
        start_date = timezone.make_aware(datetime(2001, 1, 1))
        end_date = timezone.make_aware(datetime(2000, 1, 1))
        with pytest.raises(IntegrityError):
            task_factory(start_date=start_date, end_date=end_date)

    def test_duration(self, task_factory):
        start_date = timezone.make_aware(datetime(2000, 1, 1))
        end_date = timezone.make_aware(datetime(2000, 1, 5))
        task = task_factory(start_date=start_date, end_date=end_date)
        assert task.duration.days == 4

    def test_set_board_error_if_without_updated_by(self, task, todo_board):
        with pytest.raises(ValidationError, match="updated_by is required."):
            task.set_board(board=todo_board, updated_by=None)

    def test_set_board_sets_board_and_updated_by(self, done_board, task, user):
        task.set_board(board=done_board, updated_by=user)
        assert task.board == done_board
        assert task.updated_by == user

    def test_revoke_should_remove_responsible_and_status(
        self, todo_board, user, task_factory
    ):
        task = task_factory(board=todo_board, responsible=user)
        task.revoke(updated_by=user)
        assert task.board is None
        assert task.responsible is None

    def test_revoke_error_if_missing_updated_by(self, task):
        with pytest.raises(ValidationError, match="updated_by is required."):
            task.revoke(updated_by=None)

    class TestAssignResponsible:

        def test_does_not_call_celery_task_when_new_responsible_is_none(
            self, task, mocker
        ):
            mock_send_task_assignment_email = mocker.patch(
                "projecthub.tasks.tasks.send_task_assignment_email"
            )
            task.assign_responsible(None)
            mock_send_task_assignment_email.delay.assert_not_called()

        def test_calls_celery_task_when_assigning_new_responsible(
            self, task_factory, user, mocker
        ):
            mock_send_task_assignment_email = mocker.patch(
                "projecthub.tasks.tasks.send_task_assignment_email"
            )
            task = task_factory(responsible=None)
            task.assign_responsible(user)
            mock_send_task_assignment_email.delay.assert_called_once_with(
                task_id=task.pk, user_id=user.pk
            )

        def test_does_not_call_celery_task_when_assigning_same_responsible(
            self, task, mocker
        ):
            mock_send_task_assignment_email = mocker.patch(
                "projecthub.tasks.tasks.send_task_assignment_email"
            )
            current_responsible = task.responsible
            task.assign_responsible(current_responsible)
            mock_send_task_assignment_email.delay.assert_not_called()

        def test_updates_responsible_field(self, task, user):
            old_responsible = task.responsible
            task.assign_responsible(user)
            task.refresh_from_db()
            assert task.responsible == user
            assert task.responsible != old_responsible

        def test_calls_celery_task_when_reassigning_responsible(
            self, task, user, mocker
        ):
            mock_send_task_assignment_email = mocker.patch(
                "projecthub.tasks.tasks.send_task_assignment_email"
            )
            task.assign_responsible(user)
            mock_send_task_assignment_email.delay.assert_called_once_with(
                task_id=task.pk, user_id=user.pk
            )

        def test_does_not_call_celery_task_when_removing_responsible(
            self, task, mocker
        ):
            mock_send_task_assignment_email = mocker.patch(
                "projecthub.tasks.tasks.send_task_assignment_email"
            )
            task.assign_responsible(None)
            mock_send_task_assignment_email.delay.assert_not_called()


@pytest.mark.django_db
class TestBoard:

    def test_str(self, project_factory, board_factory):
        project = project_factory(name="projecthub", active=True)
        board = board_factory(project=project, name="To Do", order=1)
        assert str(board) == "To Do (1) in projecthub"

    def test_unique_order_per_project(self, project_factory, board_factory):
        project1 = project_factory(active=True)
        project2 = project_factory(active=True)

        board_factory(project=project1, order=1)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                board_factory(project=project1, order=1)

        board_factory(project=project2, order=1)


@pytest.mark.django_db
class TestTaskQuerySet:

    def test_for_tenant(self, tenant_factory, project_factory, task_factory):
        tenant1 = tenant_factory()
        tenant2 = tenant_factory()
        task_in_tenant1 = task_factory(project=project_factory(tenant=tenant1))
        task_in_tenant2 = task_factory(project=project_factory(tenant=tenant2))
        qs = Task.objects.for_tenant(tenant1)
        assert qs.count() == 1
        assert set(qs.values_list("pk", flat=True)) == {task_in_tenant1.pk}

    def test_for_project(self, tenant, project_factory, task_factory):
        project1 = project_factory(tenant=tenant)
        project2 = project_factory(tenant=tenant)
        task_in_project1 = task_factory(project=project1)
        task_in_project2 = task_factory(project=project2)
        qs = Task.objects.for_project(project1.pk)
        assert qs.count() == 1
        assert set(qs.values_list("pk", flat=True)) == {task_in_project1.pk}

    def test_for_responsible(self, user, task_factory):
        task1 = task_factory(responsible=user)
        task2 = task_factory()
        qs = Task.objects.for_responsible(user)
        assert qs.count() == 1
        assert set(qs.values_list("pk", flat=True)) == {task1.pk}

    def test_visible_to_returns_all_tasks_if_admin(
        self, admin_user, project, tenant, task_factory
    ):
        task_factory.create_batch(3, project=project)
        qs = Task.objects.visible_to(admin_user, project.pk, tenant)
        assert qs.count() == 3

    def test_visible_to_returns_all_tasks_if_project_owner(self, project, task_factory):
        task_factory.create_batch(3, project=project)
        qs = Task.objects.visible_to(
            user=project.owner, tenant=project.tenant, project_id=project.pk
        )
        assert qs.count() == 3

    def test_visible_to_returns_all_tasks_if_project_supervisor(
        self, project, task_factory
    ):
        task_factory.create_batch(3, project=project)
        qs = Task.objects.visible_to(
            user=project.supervisor, tenant=project.tenant, project_id=project.pk
        )
        assert qs.count() == 3

    def test_visible_to_returns_only_tasks_user_is_responsible_for_if_project_user(
        self, user, project_user, project, task_factory
    ):
        task1 = task_factory(project=project, responsible=project_user.user)
        task2 = task_factory(project=project)
        qs = Task.objects.visible_to(
            user=project_user.user, tenant=project.tenant, project_id=project.pk
        )
        assert set(qs.values_list("pk", flat=True)) == {task1.pk}

    def test_visible_to_returns_empty_qs(self, user, project, task_factory):
        """Returns empty queryset if user is nor admin nor tenant owner
        nor project owner nor project user"""
        task_factory(project=project)
        qs = Task.objects.visible_to(
            user=user, tenant=project.tenant, project_id=project.pk
        )
        assert not qs.exists()


@pytest.mark.django_db
class TestBoardQuerySet:

    def test_for_project(self, project_factory, board_factory):
        project1 = project_factory()
        project2 = project_factory()
        board_in_project1 = board_factory(project=project1)
        board_in_project2 = board_factory(project=project2)
        qs = Board.objects.for_project(project1)
        assert set(qs.values_list("pk", flat=True)) == {board_in_project1.pk}
