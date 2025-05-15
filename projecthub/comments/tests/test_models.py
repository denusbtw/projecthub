import pytest
from django.db import IntegrityError

from projecthub.comments.models import Comment


@pytest.mark.django_db
class TestComment:

    def test_error_if_comment_parent_is_self(self, comment):
        comment.parent = comment
        with pytest.raises(IntegrityError):
            comment.save()

    def test_is_reply(self, comment_factory, task):
        parent = comment_factory(task=task)
        reply = comment_factory(task=task, parent=parent)

        assert not parent.is_reply
        assert reply.is_reply


@pytest.mark.django_db
class TestCommentQuerySet:

    def test_for_tenant(
            self, tenant_factory, project_factory, task_factory, comment_factory
    ):
        tenant1 = tenant_factory()
        tenant2 = tenant_factory()
        project_in_tenant1 = project_factory(tenant=tenant1)
        project_in_tenant2 = project_factory(tenant=tenant2)
        task_in_tenant1 = task_factory(project=project_in_tenant1)
        task_in_tenant2 = task_factory(project=project_in_tenant2)
        comment_in_tenant1 = comment_factory(task=task_in_tenant1)
        comment_in_tenant2 = comment_factory(task=task_in_tenant2)
        qs = Comment.objects.for_tenant(tenant1)
        assert set(qs.values_list("pk", flat=True)) == {comment_in_tenant1.pk}

    def test_for_task(self, tenant, project, task_factory, comment_factory):
        task1 = task_factory(project=project)
        task2 = task_factory(project=project)
        comment_in_task1 = comment_factory(task=task1)
        comment_in_task2 = comment_factory(task=task2)
        qs = Comment.objects.for_task(task1.pk)
        assert set(qs.values_list("pk", flat=True)) == {comment_in_task1.pk}