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


@pytest.mark.django_db
class TestProjectUpdateSerializer:

    def test_no_error_if_empty_data(self, project):
        serializer = ProjectUpdateSerializer(project, data={})
        assert serializer.is_valid(), serializer.errors
