from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.tasks.models import Task, Board


# ==== Task serializers ==== #
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


class BaseTaskWriteSerializer(serializers.ModelSerializer):
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


class TaskCreateSerializer(BaseTaskWriteSerializer):
    def to_representation(self, instance):
        return TaskListSerializer(instance, context=self.context).data


class TaskUpdateSerializer(BaseTaskWriteSerializer):
    class Meta(BaseTaskWriteSerializer.Meta):
        extra_kwargs = {"name": {"required": False}}


class TaskUpdateSerializerForResponsible(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("board",)

    def validate_board(self, new_board):
        allowed_transitions = {
            Board.TODO: [None, Board.IN_PROGRESS],
            Board.IN_PROGRESS: [None, Board.TODO, Board.IN_REVIEW],
            Board.IN_REVIEW: [Board.TODO, Board.IN_PROGRESS],
            Board.DONE: [],
        }
        
        task = self.instance
        current_board = task.board

        if new_board == current_board:
            return new_board

        new_board_code = new_board.code if new_board else None
        new_board_name = new_board.name if new_board else None
        if new_board_code not in allowed_transitions.get(current_board.code):
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

        instance.set_board(new_board.code, user)
        return instance


# ==== Board serializers ==== #
class BaseBoardReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    order = serializers.IntegerField()
    is_default = serializers.BooleanField()


class BoardListSerializer(BaseBoardReadSerializer):
    pass


class BoardDetailSerializer(BaseBoardReadSerializer):
    pass


class BaseBoardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("name", "order")


class BoardCreateSerializer(BaseBoardWriteSerializer):
    def to_representation(self, instance):
        return BoardListSerializer(instance, context=self.context).data


class BoardUpdateSerializer(BaseBoardWriteSerializer):
    class Meta(BaseBoardWriteSerializer.Meta):
        extra_kwargs = {"name": {"required": False}, "order": {"required": False}}
