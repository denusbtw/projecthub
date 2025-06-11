from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.tasks.models import Task, Board


class BaseTaskReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    board = serializers.SerializerMethodField()
    priority = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    close_date = serializers.DateTimeField()
    created_by = UserNestedSerializer()
    created_at = serializers.DateTimeField()

    def get_board(self, obj):
        return getattr(obj.board, "name", None)


class TaskListSerializer(BaseTaskReadSerializer):
    pass


class TaskDetailSerializer(BaseTaskReadSerializer):
    responsible = UserNestedSerializer()
    description = serializers.CharField()


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "board",
            "priority",
            "description",
            "responsible",
            "start_date",
            "end_date",
            "close_date",
        )

    # TODO: responsible should be member of project and tenant
    # def validate_responsible(self, responsible):
    #     pass

    def create(self, validated_data):
        responsible = validated_data.pop("responsible")
        instance = super().create(validated_data)
        instance.assign_responsible(responsible)
        return instance


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "name",
            "board",
            "priority",
            "description",
            "responsible",
            "start_date",
            "end_date",
            "close_date",
        )
        extra_kwargs = {"name": {"required": False}}

    # TODO: responsible should be member of project and tenant
    # def validate_responsible(self, responsible):
    #     pass

    def update(self, instance, validated_data):
        responsible = validated_data.pop("responsible")
        super().update(instance, validated_data)
        instance.assign_responsible(responsible)
        return instance


class TaskUpdateSerializerForResponsible(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("board",)

    def validate_board(self, new_board):
        allowed_transitions = {
            Board.Type.TODO: [None, Board.Type.IN_PROGRESS],
            Board.Type.IN_PROGRESS: [None, Board.Type.TODO, Board.Type.IN_REVIEW],
            Board.Type.IN_REVIEW: [Board.Type.TODO, Board.Type.IN_PROGRESS],
            Board.Type.DONE: [],
        }

        task = self.instance
        current_board = task.board

        if new_board == current_board:
            return new_board

        new_board_type = new_board.type if new_board else None
        new_board_name = new_board.name if new_board else None
        if new_board_type not in allowed_transitions.get(current_board.type):
            raise serializers.ValidationError(
                f"You can't move task from {current_board.name} to {new_board_name}"
            )

        return new_board

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        new_board = validated_data.get("board")
        if new_board == instance.board:
            return instance

        if new_board is None:
            instance.revoke(user)
            return instance

        instance.set_board(new_board, user)
        return instance
