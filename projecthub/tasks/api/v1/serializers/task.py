from datetime import datetime, time

from django.utils import timezone
from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.tasks.models import Task


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

    def validate(self, attrs):
        if self.instance is None:
            project = self.context["project"]
        else:
            project = self.instance.project

        if project.is_archived:
            raise serializers.ValidationError(
                "Cannot modify tasks in an archived project."
            )
        return super().validate(attrs)

    def validate_responsible(self, responsible):
        if self.instance is None:
            project = self.context["project"]
        else:
            project = self.instance.project

        project_membership = project.members.filter(user=responsible)

        if not (
            responsible.id in {project.owner_id, project.supervisor_id}
            or project_membership.exists()
        ):
            raise serializers.ValidationError("Responsible must be member of project.")
        return responsible

    def validate_board(self, board):
        if self.instance is None:
            project = self.context["project"]
        else:
            project = self.instance.project

        if board.project_id != project.pk:
            raise serializers.ValidationError(
                "This board doesn't belong to current project."
            )
        return board

    def validate_start_date(self, start_date: datetime):
        if self.instance is None:
            project = self.context["project"]
        else:
            project = self.instance.project

        project_start = timezone.make_aware(
            datetime.combine(project.start_date, time.min)
        )

        if start_date < project_start:
            raise serializers.ValidationError("Task can't start before project start.")
        return start_date

    def validate_end_date(self, end_date):
        if self.instance is None:
            project = self.context["project"]
        else:
            project = self.instance.project
        project_end = timezone.make_aware(datetime.combine(project.end_date, time.min))

        if end_date > project_end:
            raise serializers.ValidationError("Task can't end after project end.")
        return end_date

    def validate_close_date(self, close_date):
        if self.instance is None:
            project = self.context["project"]
        else:
            project = self.instance.project

        project_start = timezone.make_aware(
            datetime.combine(project.start_date, time.min)
        )

        if close_date < project_start:
            raise serializers.ValidationError("Task can't close before project start.")

        return close_date


class TaskCreateSerializer(BaseTaskWriteSerializer):
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

    def create(self, validated_data):
        responsible = validated_data.pop("responsible", None)
        instance = super().create(validated_data)
        instance.assign_responsible(responsible)
        return instance


class TaskUpdateSerializer(BaseTaskWriteSerializer):
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

    def validate_close_date(self, close_date):
        task = self.instance
        if task.start_date and close_date < task.start_date:
            raise serializers.ValidationError("Task can't close before task start.")
        return super().validate_close_date(close_date)

    def update(self, instance, validated_data):
        responsible = validated_data.pop("responsible", None)
        super().update(instance, validated_data)
        instance.assign_responsible(responsible)
        return instance


class TaskUpdateSerializerForResponsible(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("board",)

    def validate_board(self, board):
        task = self.instance
        if board.project_id != task.project_id:
            raise serializers.ValidationError(
                "This board doesn't belong to current project."
            )
        return board

    def update(self, instance, validated_data):
        user = self.context["request_user"]

        new_board = validated_data.get("board", None)
        if new_board == instance.board:
            return instance

        if new_board is None:
            instance.revoke(user)
            return instance

        instance.set_board(new_board, user)
        return instance
