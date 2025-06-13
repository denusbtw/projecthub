from projecthub.tasks.models.board import Board


def create_default_boards(project):
    default_boards = [
        {"name": "To Do", "order": 1},
        {"name": "In Progress", "order": 2},
        {"name": "In Review", "order": 3},
        {"name": "Done", "order": 4},
    ]
    boards = [Board(project=project, **board_data) for board_data in default_boards]
    Board.objects.bulk_create(boards)
