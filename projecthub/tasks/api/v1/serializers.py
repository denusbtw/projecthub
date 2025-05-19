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

#TODO
# create serializer for task responsible (he can update only status)


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
        extra_kwargs = {
            "name": {"required": False},
            "order": {"required": False}
        }