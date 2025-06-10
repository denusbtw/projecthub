import pytest

from projecthub.tasks.models import Board
from projecthub.tasks.services import create_default_boards


@pytest.mark.django_db
class TestCreateDefaultBoards:

    def test_success(self, project):
        create_default_boards(project)
        boards = Board.objects.filter(project=project)

        assert len(boards) == 4
        board_types = {
            Board.Type.TODO,
            Board.Type.IN_PROGRESS,
            Board.Type.IN_REVIEW,
            Board.Type.DONE,
        }
        assert board_types == set(boards.values_list("type", flat=True))
