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
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "owner",
            "supervisor",
            "description",
            "start_date",
            "end_date",
        )

    def create(self, validated_data):
        owner = validated_data.get("owner")
        if owner is None:
            validated_data["owner"] = self.context["request_user"]

        start_date = validated_data.pop("start_date", None)

        instance = super().create(validated_data)

        if start_date:
            instance.set_start_date(start_date)

        create_default_boards(instance)
        return instance


class ProjectUpdateSerializer(BaseProjectWriteSerializer):
    class Meta:
        model = Project
        fields = (
            "name",
            "owner",
            "supervisor",
            "description",
            "status",
            "start_date",
            "end_date",
        )
        extra_kwargs = {
            "name": {"required": False},
        }

    def validate(self, attrs):
        # забороняє редагування якщо проєкт заархівований
        if self.instance.is_archived:
            raise serializers.ValidationError("You cannot modify archived project.")
        return attrs

    def validate_status(self, status):
        # дозволено тільки архівувати проєкт
        if status != Project.Status.ARCHIVED:
            raise serializers.ValidationError("You may only archive project.")

        # архівувати можна лише активні проєкти
        if not self.instance.is_active:
            raise serializers.ValidationError("You may only archive active projects.")

        return status

    def validate_start_date(self, start_date):
        # не можна змінити дату старту активного проєкту
        if self.instance.is_active and start_date != self.instance.start_date:
            raise serializers.ValidationError(
                "Cannot change start_date when project is active."
            )
        return start_date

    def update(self, instance, validated_data):
        status = validated_data.pop("status", None)
        if status:
            instance.archive(self.context["request_user"])

        start_date = validated_data.pop("start_date", None)
        if start_date:
            instance.updated_by = self.context["request_user"]
            instance.set_start_date(start_date)

        instance = super().update(instance, validated_data)
        return instance
