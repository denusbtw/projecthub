import pytest

from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership


@pytest.mark.django_db
class TestTaskFactory:

    def test_creates_project_and_tenant_memberships_for_responsible(
            self, project, task_factory
    ):
        task = task_factory(project=project)

        assert ProjectMembership.objects.filter(
            project=project, user=task.responsible
        ).exists()

        assert TenantMembership.objects.filter(
            tenant=project.tenant, user=task.responsible
        ).exists()