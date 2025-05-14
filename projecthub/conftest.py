import pytest
from rest_framework.test import APIClient

from projecthub.comments.tests.factories import CommentFactory
from projecthub.core.models import TenantMembership
from projecthub.core.tests.factories import TenantFactory, TenantMembershipFactory
from projecthub.projects.models import ProjectMembership
from projecthub.projects.tests.factories import ProjectFactory, ProjectMembershipFactory
from projecthub.tasks.tests.factories import TaskFactory, TaskStatusFactory
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
def task_status_factory():
    return TaskStatusFactory


@pytest.fixture
def todo_task_status(db, tenant):
    return TaskStatusFactory(tenant=tenant, name="To Do", code="todo")


@pytest.fixture
def in_progress_task_status(db, tenant):
    return TaskStatusFactory(tenant=tenant, name="In progress", code="in_progress")


@pytest.fixture
def in_review_task_status(db, tenant):
    return TaskStatusFactory(tenant=tenant, name="In review", code="in_review")


@pytest.fixture
def done_task_status(db, tenant):
    return TaskStatusFactory(tenant=tenant, name="Done", code="done")


@pytest.fixture
def comment_factory():
    return CommentFactory


@pytest.fixture
def comment(db, task):
    return CommentFactory(task=task)


@pytest.fixture
def api_client():
    return APIClient()