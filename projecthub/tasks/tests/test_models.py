from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone


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
            task.set_status(code="todo", updated_by=None)

    def test_set_status_error_if_status_does_not_exist(self, task, user):
        with pytest.raises(ValidationError, match="No status with code"):
            task.set_status(code="invalid", updated_by=user)

    def test_set_status_sets_close_date_if_status_is_done(
        self, done_task_status, task, user
    ):
        task.set_status(code=done_task_status.code, updated_by=user)
        assert task.close_date is not None

    def test_set_status_sets_status_and_updated_by(self, done_task_status, task, user):
        task.set_status(code=done_task_status.code, updated_by=user)
        assert task.status == done_task_status
        assert task.updated_by == user

    def test_is_todo_property(self, task_factory, todo_task_status):
        task = task_factory(status=todo_task_status)
        assert task.is_todo
        assert not task.is_in_progress
        assert not task.is_in_review
        assert not task.is_done

    def test_is_in_progress_property(self, task_factory, in_progress_task_status):
        task = task_factory(status=in_progress_task_status)
        assert not task.is_todo
        assert task.is_in_progress
        assert not task.is_in_review
        assert not task.is_done

    def test_is_in_review_property(self, task_factory, in_review_task_status):
        task = task_factory(status=in_review_task_status)
        assert not task.is_todo
        assert not task.is_in_progress
        assert task.is_in_review
        assert not task.is_done

    def test_is_done_property(self, task_factory, done_task_status):
        task = task_factory(status=done_task_status)
        assert not task.is_todo
        assert not task.is_in_progress
        assert not task.is_in_review
        assert task.is_done

    def test_revoke_should_remove_responsible_and_status(
            self, todo_task_status, user, task_factory
    ):
        task = task_factory(status=todo_task_status, responsible=user)
        task.revoke(updated_by=user)
        assert task.status is None
        assert task.responsible is None
        assert task.updated_by == user

    def test_revoke_error_if_missing_updated_by(self, task):
        with pytest.raises(ValidationError, match="updated_by is required."):
            task.revoke(updated_by=None)


@pytest.mark.django_db
class TestTaskStatus:

    def test_error_if_task_status_with_such_order_exists_in_tenant(
        self, tenant, task_status_factory
    ):
        task_status_factory(tenant=tenant, order=10)
        with pytest.raises(IntegrityError):
            task_status_factory(tenant=tenant, order=10)

    def test_error_if_task_status_with_such_code_exists_in_tenant(
        self, tenant, task_status_factory
    ):
        task_status_factory(tenant=tenant, code="todo")
        with pytest.raises(IntegrityError):
            task_status_factory(tenant=tenant, code="todo")

    def test_is_todo_property(self, todo_task_status):
        assert todo_task_status.is_todo
        assert not todo_task_status.is_in_progress
        assert not todo_task_status.is_in_review
        assert not todo_task_status.is_done

    def test_is_in_progress_property(self, in_progress_task_status):
        assert not in_progress_task_status.is_todo
        assert in_progress_task_status.is_in_progress
        assert not in_progress_task_status.is_in_review
        assert not in_progress_task_status.is_done

    def test_is_in_review_property(self, in_review_task_status):
        assert not in_review_task_status.is_todo
        assert not in_review_task_status.is_in_progress
        assert in_review_task_status.is_in_review
        assert not in_review_task_status.is_done

    def test_is_done_property(self, done_task_status):
        assert not done_task_status.is_todo
        assert not done_task_status.is_in_progress
        assert not done_task_status.is_in_review
        assert done_task_status.is_done
