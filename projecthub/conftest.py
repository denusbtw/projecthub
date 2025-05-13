import pytest

from projecthub.core.tests.factories import TenantFactory, TenantMembershipFactory
from projecthub.projects.tests.factories import ProjectFactory, ProjectMembershipFactory
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
def project_factory():
    return ProjectFactory


@pytest.fixture
def project(db, tenant):
    return ProjectFactory(tenant=tenant)


@pytest.fixture
def project_membership_factory():
    return ProjectMembershipFactory
