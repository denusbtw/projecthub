from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.projects.models import Project
from projecthub.tasks.services import create_default_boards


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


class BaseProjectWriteSerializer(serializers.ModelSerializer):

    def _validate_user_is_tenant_owner_or_member(self, user):
        tenant = self.context["tenant"]
        tenant_members_ids = tenant.members.values_list("user_id", flat=True)

        if not (user.pk == tenant.owner_id or user.pk in tenant_members_ids):
            raise serializers.ValidationError("Must be owner or member of tenant.")
        return user

    def validate_owner(self, owner):
        return self._validate_user_is_tenant_owner_or_member(owner)

    def validate_supervisor(self, supervisor):
        return self._validate_user_is_tenant_owner_or_member(supervisor)


class ProjectCreateSerializer(BaseProjectWriteSerializer):
    def create(self, validated_data):
        instance = super().create(validated_data)
        create_default_boards(instance)
        return instance

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "owner",
            "supervisor",
            "status",
            "description",
            "start_date",
            "end_date",
            "close_date",
        )


class ProjectUpdateSerializer(BaseProjectWriteSerializer):
    class Meta:
        model = Project
        fields = (
            "name",
            "owner",
            "supervisor",
            "status",
            "description",
            "start_date",
            "end_date",
            "close_date",
        )
        extra_kwargs = {
            "name": {"required": False},
        }
