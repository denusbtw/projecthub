import pytest

from projecthub.core.models import TenantMembership


@pytest.mark.django_db
class TestProjectMembershipFactory:

    def test_creates_tenant_membership_for_user(
            self, project, project_membership_factory
    ):
        membership = project_membership_factory(project=project)
        assert TenantMembership.objects.filter(
            tenant=project.tenant,
            user=membership.user
        ).exists()
