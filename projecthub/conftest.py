import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from projecthub.attachments.tests.factories import CommentAttachmentFactory, \
    TaskAttachmentFactory
from projecthub.comments.tests.factories import CommentFactory
from projecthub.core.models import TenantMembership
from projecthub.core.tests.factories import TenantFactory, TenantMembershipFactory
from projecthub.projects.models import ProjectMembership
from projecthub.projects.tests.factories import ProjectFactory, ProjectMembershipFactory
from projecthub.tasks.models import Board
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
def tenant_owner(db, tenant, tenant_membership_factory):
    return tenant_membership_factory(tenant=tenant, role=TenantMembership.Role.OWNER)


@pytest.fixture
def project_factory():
    return ProjectFactory


@pytest.fixture
def project(db, tenant):
    return ProjectFactory(tenant=tenant)


@pytest.fixture
def project_membership_factory():
    return ProjectMembershipFactory


@pytest.fixture
def project_membership(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.USER)


@pytest.fixture
def project_owner(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.OWNER)


@pytest.fixture
def project_supervisor(db, project):
    return ProjectMembershipFactory(
        project=project, role=ProjectMembership.Role.SUPERVISOR
    )


@pytest.fixture
def project_responsible(db, project):
    return ProjectMembershipFactory(
        project=project, role=ProjectMembership.Role.RESPONSIBLE
    )


@pytest.fixture
def project_user(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.USER)


@pytest.fixture
def project_guest(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.GUEST)


@pytest.fixture
def project_reader(db, project):
    return ProjectMembershipFactory(project=project, role=ProjectMembership.Role.READER)


@pytest.fixture
def task_factory():
    return TaskFactory


@pytest.fixture
def task(db, project):
    return TaskFactory(project=project)


@pytest.fixture
def board_factory():
    return BoardFactory


@pytest.fixture
def todo_board(db, tenant):
    return BoardFactory(tenant=tenant, name="To Do", code=Board.TODO)


@pytest.fixture
def in_progress_board(db, tenant):
    return BoardFactory(tenant=tenant, name="In progress", code=Board.IN_PROGRESS)


@pytest.fixture
def in_review_board(db, tenant):
    return BoardFactory(tenant=tenant, name="In review", code=Board.IN_REVIEW)


@pytest.fixture
def done_board(db, tenant):
    return BoardFactory(tenant=tenant, name="Done", code=Board.DONE)


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
def comment_attachment_factory():
    return CommentAttachmentFactory


@pytest.fixture
def comment_attachment(comment):
    return CommentAttachmentFactory(comment=comment)


@pytest.fixture
def task_attachment_factory():
    return TaskAttachmentFactory


@pytest.fixture
def task_attachment(task):
    return TaskAttachmentFactory(task=task)


@pytest.fixture
def file():
    return SimpleUploadedFile(
        name="test.txt",
        content=b"file content here",
        content_type="text/plain"
    )


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath