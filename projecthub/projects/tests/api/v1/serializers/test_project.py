import pytest
from rest_framework.exceptions import ValidationError

from projecthub.projects.api.v1.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
)
from projecthub.projects.models import Project
from projecthub.tasks.models import Board


@pytest.fixture
def data():
    return {"name": "my project", "status": Project.Status.ACTIVE}


@pytest.mark.django_db
class TestProjectListSerializer:

    def test_status_is_correct(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        serializer = ProjectListSerializer(project)
        assert serializer.data["status"] == project.get_status_display()


@pytest.mark.django_db
class TestProjectDetailSerializer:

    def test_status_is_correct(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["status"] == project.get_status_display()

    def test_owner_is_nested_serializer(self, project):
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["owner"]["id"] == str(project.owner_id)

    def test_supervisor_is_nested_serializer(self, project):
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["supervisor"]["id"] == str(project.supervisor_id)

    def test_responsible_is_nested_serializer(self, project):
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["responsible"]["id"] == str(project.responsible_id)


@pytest.mark.django_db
class TestProjectCreateSerializer:

    def test_error_if_empty_data(self):
        serializer = ProjectCreateSerializer(data={})
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_default_boards_are_created(self, tenant, data):
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        project = serializer.save(tenant=tenant)
        boards = Board.objects.filter(project=project)
        assert len(boards) == 4
        assert {
            Board.Type.TODO,
            Board.Type.IN_PROGRESS,
            Board.Type.IN_REVIEW,
            Board.Type.DONE,
        } == set(boards.values_list("type", flat=True))

    def test_error_if_owner_is_not_tenant_owner_or_member(self, user, tenant, data):
        data["owner"] = user.pk
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Must be owner or member of tenant" in str(exc.value)

    def test_error_if_supervisor_is_not_tenant_owner_or_member(
        self, user, tenant, data
    ):
        data["supervisor"] = user.pk
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Must be owner or member of tenant" in str(exc.value)

    def test_no_error_if_owner_is_tenant_owner(self, tenant, data):
        data["owner"] = tenant.owner_id
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_supervisor_is_tenant_owner(self, tenant, data):
        data["supervisor"] = tenant.owner_id
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_owner_is_tenant_member(
        self, user, tenant, tenant_membership_factory, data
    ):
        tenant_membership_factory(tenant=tenant, user=user)
        data["owner"] = user.pk
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_supervisor_is_tenant_member(
        self, user, tenant, tenant_membership_factory, data
    ):
        tenant_membership_factory(tenant=tenant, user=user)
        data["supervisor"] = user.pk
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestProjectUpdateSerializer:

    def test_no_error_if_empty_data(self, project):
        serializer = ProjectUpdateSerializer(project, data={})
        assert serializer.is_valid(), serializer.errors

    def test_error_if_owner_is_not_tenant_owner_or_member(self, project, user, tenant):
        data = {"owner": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(project, data=data, context=context)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Must be owner or member of tenant" in str(exc.value)

    def test_error_if_supervisor_is_not_tenant_owner_or_member(
        self, project, user, tenant
    ):
        data = {"supervisor": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(project, data=data, context=context)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Must be owner or member of tenant" in str(exc.value)

    def test_no_error_if_owner_is_tenant_owner(self, tenant, project):
        data = {"owner": tenant.owner_id}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_supervisor_is_tenant_owner(self, tenant, project):
        data = {"supervisor": tenant.owner_id}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_owner_is_tenant_member(
        self, user, tenant, tenant_membership_factory, project
    ):
        tenant_membership_factory(tenant=tenant, user=user)
        data = {"owner": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_supervisor_is_tenant_member(
        self, user, tenant, tenant_membership_factory, project
    ):
        tenant_membership_factory(tenant=tenant, user=user)
        data = {"supervisor": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors
