import pytest

from projecthub.projects.api.v1.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectMembershipListSerializer,
    ProjectMembershipDetailSerializer,
    ProjectMembershipUpdateSerializer,
)
from projecthub.projects.models import Project, ProjectMembership


@pytest.fixture
def data():
    return {"name": "my project", "status": Project.Status.ACTIVE}


@pytest.mark.django_db
class TestProjectListSerializer:

    def test_status_is_correct(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        project.role = ""
        serializer = ProjectListSerializer(project)
        assert serializer.data["status"] == project.get_status_display()


@pytest.mark.django_db
class TestProjectDetailSerializer:

    def test_status_is_correct(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["status"] == project.get_status_display()

    def test_owner_is_nested_serializer(self, project, project_membership_factory):
        owner_membership = project_membership_factory(
            project=project, role=ProjectMembership.Role.OWNER
        )
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["owner"]["id"] == str(owner_membership.id)


@pytest.mark.django_db
class TestProjectCreateSerializer:

    def test_to_representation_matches_list_serializer_representation(
        self, tenant, data
    ):
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        project = serializer.save(tenant=tenant)
        assert serializer.data == ProjectListSerializer(project).data

    def test_to_representation_sets_owner_role(self, tenant, data):
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        serializer.save(tenant=tenant)
        assert serializer.data["role"] == ProjectMembership.Role.OWNER


@pytest.mark.django_db
class TestProjectUpdateSerializer:

    def test_no_error_if_empty_data(self, project):
        serializer = ProjectUpdateSerializer(project, data={})
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestProjectMembershipListSerializer:

    def test_role_is_correct(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.OWNER)
        serializer = ProjectMembershipListSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestProjectMembershipDetailSerializer:

    def test_role_is_correct(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.OWNER)
        serializer = ProjectMembershipDetailSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestProjectMembershipUpdateSerializer:

    def test_no_error_if_empty_data(self, project_membership_factory):
        membership = project_membership_factory()
        serializer = ProjectMembershipUpdateSerializer(membership, data={})
        assert serializer.is_valid(), serializer.errors
