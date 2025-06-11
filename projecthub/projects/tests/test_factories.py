import pytest
from django.utils import timezone

from projecthub.core.models import TenantMembership


@pytest.mark.django_db
class TestProjectMembershipFactory:

    def test_creates_tenant_membership_for_user(
        self, project, project_membership_factory
    ):
        membership = project_membership_factory(project=project)
        assert TenantMembership.objects.filter(
            tenant=project.tenant, user=membership.user
        ).exists()


@pytest.mark.django_db
class TestProjectFactory:

    def test_active_trait(self, project_factory):
        now = timezone.now()
        active_project = project_factory(active=True)
        assert active_project.start_date <= now.date()
        assert active_project.end_date >= now.date()
        assert active_project.close_date is None
        assert active_project.is_active

    def test_pending_trait(self, project_factory):
        now = timezone.now()
        pending_project = project_factory(pending=True)
        assert pending_project.start_date >= now.date()
        assert pending_project.end_date >= now.date()
        assert pending_project.close_date is None
        assert pending_project.is_pending

    def test_archived_trait(self, project_factory):
        now = timezone.now()
        archived_project = project_factory(archived=True)
        assert archived_project.start_date <= now.date()
        assert archived_project.end_date <= now.date()
        assert archived_project.close_date <= now
        assert archived_project.is_archived

    def test_owner_is_tenant_member(self, project_factory):
        project = project_factory()
        tenant = project.tenant
        assert project.owner_id in tenant.members.values_list("user_id", flat=True)

    def test_supervisor_is_tenant_member(self, project_factory):
        project = project_factory()
        tenant = project.tenant
        assert project.supervisor_id in tenant.members.values_list("user_id", flat=True)
