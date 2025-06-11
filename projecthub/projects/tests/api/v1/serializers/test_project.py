from datetime import timedelta

import pytest
from django.utils import timezone
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
    return {"name": "my project"}


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
        data["owner"] = tenant.owner_id
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
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

    def test_status_is_set_based_on_start_date(self, tenant, data):
        data["owner"] = tenant.owner_id
        start_date = timezone.now().date() + timedelta(days=3)
        data["start_date"] = start_date.isoformat()

        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors
        project = serializer.save(tenant=tenant)
        assert project.is_pending

    def test_request_user_is_owner_if_not_provided(self, tenant, data):
        context = {"request_user": tenant.owner}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors
        project = serializer.save(tenant=tenant)
        assert project.owner == tenant.owner

    def test_supervisor_is_none_if_not_provided(self, tenant, data):
        data["owner"] = tenant.owner.pk
        context = {"tenant": tenant}
        serializer = ProjectCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors
        project = serializer.save(tenant=tenant)
        assert project.supervisor is None


@pytest.mark.django_db
class TestProjectUpdateSerializer:

    def test_no_error_if_empty_data(self, active_project):
        serializer = ProjectUpdateSerializer(active_project, data={})
        assert serializer.is_valid(), serializer.errors

    def test_error_if_owner_is_not_tenant_owner_or_member(
        self, active_project, user, tenant
    ):
        data = {"owner": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Must be owner or member of tenant" in str(exc.value)

    def test_error_if_supervisor_is_not_tenant_owner_or_member(
        self, active_project, user, tenant
    ):
        data = {"supervisor": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Must be owner or member of tenant" in str(exc.value)

    def test_no_error_if_owner_is_tenant_owner(self, tenant, active_project):
        data = {"owner": tenant.owner_id}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_supervisor_is_tenant_owner(self, tenant, active_project):
        data = {"supervisor": tenant.owner_id}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_owner_is_tenant_member(
        self, user, tenant, tenant_membership_factory, active_project
    ):
        tenant_membership_factory(tenant=tenant, user=user)
        data = {"owner": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_no_error_if_supervisor_is_tenant_member(
        self, user, tenant, tenant_membership_factory, active_project
    ):
        tenant_membership_factory(tenant=tenant, user=user)
        data = {"supervisor": user.pk}
        context = {"tenant": tenant}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors

    def test_error_if_update_archived_project(self, archived_project):
        serializer = ProjectUpdateSerializer(archived_project, data={})
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "You cannot modify archived project" in str(exc.value)

    @pytest.mark.parametrize(
        "status",
        [
            Project.Status.ACTIVE,
            Project.Status.PENDING,
            Project.Status.ARCHIVED,
        ],
    )
    def test_error_if_status_is_not_archived(self, active_project, status):
        serializer = ProjectUpdateSerializer(active_project, data={"status": status})

        if status == Project.Status.ARCHIVED:
            assert serializer.is_valid(), serializer.errors
        else:
            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "You may only archive project" in str(exc.value)

    def test_error_if_update_status_of_pending_project(self, pending_project):
        data = {"status": Project.Status.ARCHIVED}
        serializer = ProjectUpdateSerializer(pending_project, data=data)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "You may only archive active projects" in str(exc.value)

    @pytest.mark.parametrize("project", ["active_project", "pending_project"])
    def test_error_if_update_start_date_of_active_project(self, project, request):
        project = request.getfixturevalue(project)

        data = {"start_date": timezone.now().date()}
        serializer = ProjectUpdateSerializer(project, data=data)

        if project.is_active:
            with pytest.raises(ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert "Cannot change start_date when project is active" in str(exc.value)
        else:
            assert serializer.is_valid(), serializer.errors

    def test_archive_is_called_if_update_status(self, active_project, user, mocker):
        mock_archive = mocker.patch("projecthub.projects.models.Project.archive")

        data = {"status": Project.Status.ARCHIVED}
        context = {"request_user": user}
        serializer = ProjectUpdateSerializer(active_project, data=data, context=context)
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        mock_archive.assert_called_once_with(user)

    def test_set_start_date_is_called_if_update_start_date(
        self, pending_project, user, mocker
    ):
        mock_set_start_date = mocker.patch(
            "projecthub.projects.models.Project.set_start_date"
        )

        start_date = timezone.now().date()
        data = {"start_date": start_date.isoformat()}
        context = {"request_user": user}
        serializer = ProjectUpdateSerializer(
            pending_project, data=data, context=context
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()

        mock_set_start_date.assert_called_once_with(start_date)
