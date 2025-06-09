from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.projects.models import Project


class BaseProjectReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField(source="get_status_display")
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    close_date = serializers.DateTimeField()


class ProjectListSerializer(BaseProjectReadSerializer):
    pass


class ProjectDetailSerializer(BaseProjectReadSerializer):
    description = serializers.CharField()
    owner = UserNestedSerializer()
    supervisor = UserNestedSerializer()
    responsible = UserNestedSerializer()


class ProjectCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # DEFAULT_BOARDS = {
        #     {"code": Type.TODO, "name": "To Do", "order": 1},
        #     {"code": Type.IN_PROGRESS, "name": "In Progress", "order": 2},
        #     {"code": Type.IN_REVIEW, "name": "In Review", "order": 3},
        #     {"code": Type.DONE, "name": "Done", "order": 4},
        # }
        # TODO: create default boards
        return super().create(validated_data)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "status",
            "description",
            "start_date",
            "end_date",
            "close_date",
        )


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "name",
            "status",
            "description",
            "start_date",
            "end_date",
            "close_date",
        )
        extra_kwargs = {
            "name": {"required": False},
        }
