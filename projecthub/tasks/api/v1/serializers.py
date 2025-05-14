from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.tasks.models import Task, TaskStatus


# ==== Task serializers ==== #
class BaseTaskReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.SerializerMethodField()
    priority = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    close_date = serializers.DateTimeField()
    created_by = UserNestedSerializer()
    created_at = serializers.DateTimeField()

    def get_status(self, obj):
        return getattr(obj.status, "name", None)


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
            "status",
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

# TODO
# create serializer for task responsible (he can update only status)
# if task status is 'Todo', he can set status to None (revoke from task) or 'In Progress'
# if task status is 'In Progress', he can set status to None(revoke), 'Todo', or 'In Review'
# if task status is 'In Review', he can set status to None(revoke), 'Todo', or 'In progress'
# if task status 'Done', he can't update status


# ==== TaskStatus serializers ==== #
class BaseTaskStatusReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    order = serializers.IntegerField()
    is_default = serializers.BooleanField()


class TaskStatusListSerializer(BaseTaskStatusReadSerializer):
    pass


class TaskStatusDetailSerializer(BaseTaskStatusReadSerializer):
    pass


class BaseTaskStatusWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = ("name", "order")


class TaskStatusCreateSerializer(BaseTaskStatusWriteSerializer):
    def to_representation(self, instance):
        return TaskStatusListSerializer(instance, context=self.context).data


class TaskStatusUpdateSerializer(BaseTaskStatusWriteSerializer):
    class Meta(BaseTaskStatusWriteSerializer.Meta):
        extra_kwargs = {
            "name": {"required": False},
            "order": {"required": False}
        }