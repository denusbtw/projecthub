from projecthub.tasks.models.board import Board


def create_default_boards(project):
    default_boards = [
        {"name": "To Do", "type": Board.Type.TODO, "order": 1},
        {"name": "In Progress", "type": Board.Type.IN_PROGRESS, "order": 2},
        {"name": "In Review", "type": Board.Type.IN_REVIEW, "order": 3},
        {"name": "Done", "type": Board.Type.DONE, "order": 4},
    ]
    boards = [Board(project=project, **board_data) for board_data in default_boards]
    Board.objects.bulk_create(boards)
