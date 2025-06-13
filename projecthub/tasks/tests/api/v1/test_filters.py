import pytest

from projecthub.tasks.api.v1.filters import TaskFilterSet
from projecthub.tasks.models import Task


@pytest.mark.django_db
class TestTaskFilterSet:

    def test_by_responsible_username(self, task_factory, john, alice):
        john_task = task_factory(responsible=john)
        alice_task = task_factory(responsible=alice)

        queryset = Task.objects.all()
        filtered = TaskFilterSet({"responsible": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_task.pk

    def test_by_creator_username(self, task_factory, john, alice):
        john_task = task_factory(created_by=john)
        alice_task = task_factory(created_by=alice)

        queryset = Task.objects.all()
        filtered = TaskFilterSet({"creator": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_task.pk
