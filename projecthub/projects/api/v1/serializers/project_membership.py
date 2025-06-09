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


class BaseProjectMembershipWriteSerializer(serializers.ModelSerializer):
    pass


class ProjectMembershipCreateSerializer(BaseProjectMembershipWriteSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("user", "role")


class ProjectMembershipUpdateSerializer(BaseProjectMembershipWriteSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("role",)
