import pytest

from projecthub.tasks.models import Board
from projecthub.tasks.services import create_default_boards


@pytest.mark.django_db
class TestCreateDefaultBoards:

    def test_create_4_boards(self, project):
        create_default_boards(project)
        boards = Board.objects.filter(project=project)
        assert len(boards) == 4

    def test_create_boards_with_correct_names(self, project):
        create_default_boards(project)
        expected_names = {"To Do", "In Progress", "In Review", "Done"}
        actual_names = set(project.boards.values_list("name", flat=True))
        assert actual_names == expected_names

    def test_create_boards_with_correct_order(self, project):
        create_default_boards(project)
        boards = project.boards.order_by("order")
        orders = list(boards.values_list("order", flat=True))
        assert orders == [1, 2, 3, 4]
