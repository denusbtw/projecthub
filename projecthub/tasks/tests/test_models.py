from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
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

    def test_set_status_error_if_without_updated_by(self, task):
        with pytest.raises(ValidationError, match="updated_by is required."):
            task.set_board(code="todo", updated_by=None)

    def test_set_status_error_if_status_does_not_exist(self, task, user):
        with pytest.raises(ValidationError, match="No board with code"):
            task.set_board(code="invalid", updated_by=user)

    def test_set_status_sets_close_date_if_status_is_done(
        self, done_board, task, user
    ):
        task.set_board(code=done_board.code, updated_by=user)
        assert task.close_date is not None

    def test_set_status_sets_status_and_updated_by(self, done_board, task, user):
        task.set_board(code=done_board.code, updated_by=user)
        assert task.board == done_board
        assert task.updated_by == user

    def test_is_todo_property(self, task_factory, todo_board):
        task = task_factory(board=todo_board)
        assert task.is_todo
        assert not task.is_in_progress
        assert not task.is_in_review
        assert not task.is_done

    def test_is_in_progress_property(self, task_factory, in_progress_board):
        task = task_factory(board=in_progress_board)
        assert not task.is_todo
        assert task.is_in_progress
        assert not task.is_in_review
        assert not task.is_done

    def test_is_in_review_property(self, task_factory, in_review_board):
        task = task_factory(board=in_review_board)
        assert not task.is_todo
        assert not task.is_in_progress
        assert task.is_in_review
        assert not task.is_done

    def test_is_done_property(self, task_factory, done_board):
        task = task_factory(board=done_board)
        assert not task.is_todo
        assert not task.is_in_progress
        assert not task.is_in_review
        assert task.is_done

    def test_revoke_should_remove_responsible_and_status(
            self, todo_board, user, task_factory
    ):
        task = task_factory(board=todo_board, responsible=user)
        task.revoke(updated_by=user)
        assert task.board is None
        assert task.responsible is None
        assert task.updated_by == user

    def test_revoke_error_if_missing_updated_by(self, task):
        with pytest.raises(ValidationError, match="updated_by is required."):
            task.revoke(updated_by=None)


@pytest.mark.django_db
class TestBoard:

    def test_error_if_board_with_such_order_exists_in_tenant(
        self, tenant, board_factory
    ):
        board_factory(tenant=tenant, order=10)
        with pytest.raises(IntegrityError):
            board_factory(tenant=tenant, order=10)

    def test_error_if_board_with_such_code_exists_in_tenant(
        self, tenant, board_factory
    ):
        board_factory(tenant=tenant, code="todo")
        with pytest.raises(IntegrityError):
            board_factory(tenant=tenant, code="todo")

    def test_is_todo_property(self, todo_board):
        assert todo_board.is_todo
        assert not todo_board.is_in_progress
        assert not todo_board.is_in_review
        assert not todo_board.is_done

    def test_is_in_progress_property(self, in_progress_board):
        assert not in_progress_board.is_todo
        assert in_progress_board.is_in_progress
        assert not in_progress_board.is_in_review
        assert not in_progress_board.is_done

    def test_is_in_review_property(self, in_review_board):
        assert not in_review_board.is_todo
        assert not in_review_board.is_in_progress
        assert in_review_board.is_in_review
        assert not in_review_board.is_done

    def test_is_done_property(self, done_board):
        assert not done_board.is_todo
        assert not done_board.is_in_progress
        assert not done_board.is_in_review
        assert done_board.is_done


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

    def test_visible_to_returns_all_tasks_if_tenant_owner(
            self, tenant_owner, project, tenant, task_factory
    ):
        task_factory.create_batch(3, project=project)
        qs = Task.objects.visible_to(
            user=tenant_owner.user,
            tenant=tenant,
            project_id=project.pk
        )
        assert qs.count() == 3

    def test_visible_to_returns_all_tasks_if_project_owner(
            self, project_owner, project, tenant, task_factory
    ):
        task_factory.create_batch(3, project=project)
        qs = Task.objects.visible_to(
            user=project_owner.user,
            tenant=tenant,
            project_id=project.pk
        )
        assert qs.count() == 3

    def test_visible_to_returns_only_tasks_user_is_responsible_for_if_project_user(
            self, user, project_user, project, tenant, task_factory
    ):
        task1 = task_factory(project=project, responsible=project_user.user)
        task2 = task_factory(project=project)
        qs = Task.objects.visible_to(
            user=project_user.user,
            tenant=tenant,
            project_id=project.pk
        )
        assert set(qs.values_list("pk", flat=True)) == {task1.pk}

    def test_visible_to_returns_empty_qs(self, user, project, tenant, task_factory):
        """Returns empty queryset if user is nor admin nor tenant owner
         nor project owner nor project user"""
        task_factory(project=project)
        qs = Task.objects.visible_to(
            user=user,
            tenant=tenant,
            project_id=project.pk
        )
        assert not qs.exists()


@pytest.mark.django_db
class TestBoardQuerySet:

    def test_for_tenant(self, tenant_factory, board_factory):
        tenant1 = tenant_factory()
        tenant2 = tenant_factory()
        board_in_tenant1 = board_factory(tenant=tenant1)
        board_in_tenant2 = board_factory(tenant=tenant2)
        qs = Board.objects.for_tenant(tenant1)
        assert set(qs.values_list("pk", flat=True)) == {board_in_tenant1.pk}