import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from projecthub.comments.tests.factories import CommentFactory
from projecthub.core.models import TenantMembership
from projecthub.core.tests.factories import TenantFactory, TenantMembershipFactory
from projecthub.projects.models import ProjectMembership
from projecthub.projects.tests.factories import ProjectFactory, ProjectMembershipFactory
from projecthub.tasks.tests.factories import TaskFactory, BoardFactory
from projecthub.users.tests.factories import UserFactory


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def user(db, user_factory):
    return user_factory()


@pytest.fixture
def tenant_factory():
    return TenantFactory


@pytest.fixture
def tenant(db, tenant_factory):
    return tenant_factory(sub_domain="zxc")


@pytest.fixture
def http_host(tenant):
    return f"{tenant.sub_domain}.localhost"


@pytest.fixture
def tenant_membership_factory():
    return TenantMembershipFactory


@pytest.fixture
def tenant_membership(db, tenant, tenant_membership_factory):
    return tenant_membership_factory(tenant=tenant)


@pytest.fixture
def tenant_user(db, tenant, tenant_membership_factory):
    return tenant_membership_factory(tenant=tenant, role=TenantMembership.Role.USER)


@pytest.fixture
def project_factory():
    return ProjectFactory


@pytest.fixture
def project(db, tenant):
    return ProjectFactory(tenant=tenant)


@pytest.fixture
def active_project(db, tenant, project_factory):
    return project_factory(active=True, tenant=tenant)


@pytest.fixture
def pending_project(db, tenant, project_factory):
    return project_factory(pending=True, tenant=tenant)


@pytest.fixture
def archived_project(db, tenant, project_factory):
    return project_factory(archived=True, tenant=tenant)


@pytest.fixture
def project_membership_factory():
    return ProjectMembershipFactory


@pytest.fixture
def project_membership(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.USER)


@pytest.fixture
def project_user(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.USER)


@pytest.fixture
def active_project_user(db, active_project):
    return ProjectMembershipFactory(
        project=active_project, role=ProjectMembership.Role.USER
    )


@pytest.fixture
def pending_project_user(db, pending_project):
    return ProjectMembershipFactory(
        project=pending_project, role=ProjectMembership.Role.USER
    )


@pytest.fixture
def archived_project_user(db, archived_project):
    return ProjectMembershipFactory(
        project=archived_project, role=ProjectMembership.Role.USER
    )


# TODO: remove
@pytest.fixture
def project_guest(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.GUEST)


# TODO: remove
@pytest.fixture
def project_reader(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.READER)


@pytest.fixture
def task_factory():
    return TaskFactory


@pytest.fixture
def task(db, active_project):
    return TaskFactory(project=active_project)


@pytest.fixture
def board_factory():
    return BoardFactory


@pytest.fixture
def todo_board(db, project):
    return BoardFactory(project=project, name="To Do", order=1)


@pytest.fixture
def in_progress_board(db, project):
    return BoardFactory(project=project, name="In progress", order=2)


@pytest.fixture
def in_review_board(db, project):
    return BoardFactory(project=project, name="In review", order=3)


@pytest.fixture
def done_board(db, project):
    return BoardFactory(project=project, name="Done", order=4)


@pytest.fixture
def comment_factory():
    return CommentFactory


@pytest.fixture
def comment(db, task):
    return CommentFactory(task=task)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def john(db):
    return UserFactory(username="john")


@pytest.fixture
def alice(db):
    return UserFactory(username="alice")


@pytest.fixture
def file():
    return SimpleUploadedFile(
        name="test.txt", content=b"file content here", content_type="text/plain"
    )


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def superuser():
    return UserFactory(is_superuser=True)
