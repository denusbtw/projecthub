from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership, Project
from projecthub.projects.utils import get_role_value


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
    def create(self, validated_data):
        DEFAULT_BOARDS = {
            {"code": Type.TODO, "name": "To Do", "order": 1},
            {"code": Type.IN_PROGRESS, "name": "In Progress", "order": 2},
            {"code": Type.IN_REVIEW, "name": "In Review", "order": 3},
            {"code": Type.DONE, "name": "Done", "order": 4},
        }
        #TODO: create default boards
        pass

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


class BaseProjectMembershipWriteSerializer(serializers.ModelSerializer):

    def validate_role(self, value):
        """
        Validates whether a user can assign the specified role (`new_role`) to a project member,
        based on the current user's privileges and role constraints within the project.

        Role constraints:
        - Only one project member may hold the `owner`, `supervisor`, or `responsible` role at any time.
        - Admins and tenant owners can assign any role, but may only assign a unique role
          (`owner`, `supervisor`, `responsible`) if it is currently unoccupied.
          If the target role is already assigned to another member, a ValidationError is raised.
        - Project owners may transfer their `owner` role to another user only if the `supervisor` role is vacant.
          Otherwise, the operation is denied.
        - Project supervisors may transfer their `supervisor` role only if the `responsible` role is vacant.
        - Project responsibles cannot transfer their own role, but they may assign the roles
          `user`, `guest`, or `reader` to new or existing members.
        - All role changes must respect role uniqueness; automatic demotion of other members is not allowed.

        Raises:
            ValidationError: if the role assignment violates any of the above constraints.
        """
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Request is required.")

        project_id = self.context.get("project_id")
        if not project_id:
            raise serializers.ValidationError("project_id is required in context.")

        project = get_object_or_404(Project, tenant=request.tenant, pk=project_id)
        new_role = value
        # admin, tenant owner and project owner can create/update any role
        if not (
                request.user.is_staff
                or request.tenant.has_role(TenantMembership.Role.OWNER, request.user)
                or project.has_role(ProjectMembership.Role.OWNER, request.user)
        ):
            request_user_role = project.get_role_of(request.user)
            if get_role_value(request_user_role) < get_role_value(new_role):
                raise serializers.ValidationError(
                    f"As'{request_user_role}' you can't assign '{new_role}' role."
                )

        if new_role in ProjectMembership.SINGLE_USER_ROLES:
            downgrade_role = self.get_downgrade_role(new_role)
            if downgrade_role == ProjectMembership.Role.USER:
                return new_role

            if project.has_role(downgrade_role):
                raise serializers.ValidationError(
                    f"You can't assign '{new_role}' role to user"
                    f" unless you free '{downgrade_role}' role."
                )

        return new_role

    def get_downgrade_role(self, role):
        return {
            ProjectMembership.Role.OWNER: ProjectMembership.Role.SUPERVISOR,
            ProjectMembership.Role.SUPERVISOR: ProjectMembership.Role.RESPONSIBLE,
            ProjectMembership.Role.RESPONSIBLE: ProjectMembership.Role.USER,
        }.get(role)


class ProjectMembershipCreateSerializer(BaseProjectMembershipWriteSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("user", "role")

    def create(self, validated_data):
        request = self.context.get("request")
        project_id = self.context.get("project_id")

        project = get_object_or_404(Project, tenant=request.tenant, pk=project_id)

        new_role = validated_data["role"]
        if new_role in ProjectMembership.SINGLE_USER_ROLES:
            downgrade_role = self.get_downgrade_role(new_role)
            project_membership = ProjectMembership.objects.get(
                project=project,
                role=new_role
            )
            project_membership.set_role(downgrade_role, request.user)
            project_membership.save()

        membership = ProjectMembership(
            user=validated_data["user"],
            project=project,
            created_by=request.user
        )
        membership.set_role(new_role, request.user)
        membership.save()
        return membership


class ProjectMembershipUpdateSerializer(BaseProjectMembershipWriteSerializer):
    class Meta:
        model = ProjectMembership
        fields = ("role",)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        project_id = self.context.get("project_id")

        project = get_object_or_404(Project, tenant=request.tenant, pk=project_id)

        new_role = validated_data.get("role")
        if new_role is None:
            return instance

        if new_role in ProjectMembership.SINGLE_USER_ROLES:
            downgrade_role = self.get_downgrade_role(new_role)
            project_membership = ProjectMembership.objects.get(
                project=project,
                role=new_role
            )
            project_membership.set_role(downgrade_role, request.user)
            project_membership.save()

        instance.set_role(new_role, request.user)
        instance.save()
        return instance