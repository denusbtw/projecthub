from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.projects.models import ProjectMembership


class BaseProjectMembershipReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user = UserNestedSerializer()
    role = serializers.CharField(source="get_role_display")


class ProjectMembershipListSerializer(BaseProjectMembershipReadSerializer):
    pass


class ProjectMembershipDetailSerializer(BaseProjectMembershipReadSerializer):
    pass


class ProjectMembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("id", "user", "role")

    def validate_user(self, user):
        project = self.context["project"]
        if project.is_archived:
            error_msg = "Can't create members for archived project."
            raise serializers.ValidationError(error_msg)

        tenant = project.tenant

        if user.pk in {tenant.owner_id, project.owner_id, project.supervisor_id}:
            raise serializers.ValidationError(
                "Owner of tenant or owner and supervisor of project can't be members."
            )

        if user.pk not in tenant.members.values_list("user_id", flat=True):
            raise serializers.ValidationError("User must be member of tenant.")

        return user


class ProjectMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("role",)
