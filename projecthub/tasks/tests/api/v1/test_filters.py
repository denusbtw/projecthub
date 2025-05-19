import pytest

from projecthub.tasks.api.v1.filters import TaskFilterSet, BoardFilterSet
from projecthub.tasks.models import Task, Board


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


@pytest.mark.django_db
class TestBoardFilterSet:

    def test_by_creator(self, board_factory, john, alice):
        john_board = board_factory(created_by=john)
        alice_board = board_factory(created_by=alice)

        queryset = Board.objects.all()
        filtered = BoardFilterSet({"creator": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_board.pk
