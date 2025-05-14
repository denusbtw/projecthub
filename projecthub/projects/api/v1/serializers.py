from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.projects.models import ProjectMembership, Project


# ==== Project serializers ==== #
class BaseProjectReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField(source="get_status_display")
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    close_date = serializers.DateTimeField()
    role = serializers.CharField()


class ProjectListSerializer(BaseProjectReadSerializer):
    pass


class ProjectDetailSerializer(BaseProjectReadSerializer):
    description = serializers.CharField()
    owner = serializers.SerializerMethodField()

    def get_owner(self, obj):
        owner_membership = ProjectMembership.objects.filter(
            project=obj, role=ProjectMembership.Role.OWNER
        ).first()
        if owner_membership:
            return ProjectMembershipListSerializer(
                owner_membership, context=self.context
            ).data
        return None


class BaseProjectWriteSerializer(serializers.ModelSerializer):
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


class ProjectCreateSerializer(BaseProjectWriteSerializer):
    def to_representation(self, instance):
        instance.role = ProjectMembership.Role.OWNER
        return ProjectListSerializer(instance, context=self.context).data


class ProjectUpdateSerializer(BaseProjectWriteSerializer):
    class Meta(BaseProjectWriteSerializer.Meta):
        extra_kwargs = {
            "name": {"required": False},
        }


# ==== ProjectMembershipSerializers ==== #
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
        fields = ("user", "role")

    #TODO
    # if user with single role (owner, supervisor, responsible) exists
    # then he is deleted
    # admin, tenant owner and project owner can create user with any role
    # supervisor can create only responsible, user, guest, reader
    # responsible can create only user, guest, reader


class ProjectMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("role",)

    #TODO
    # if role is single (owner, supervisor, responsible) and user with such role exists
    # then he is deleted
    # admin, tenant owner and project owner can update any role
    # supervisor can update only responsible, user, guest, reader
    # responsible can update only user, guest, reader