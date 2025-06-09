import pytest

from projecthub.projects.api.v1.filters import (
    ProjectFilterSet,
    ProjectMembershipFilterSet,
)
from projecthub.projects.models import Project, ProjectMembership


@pytest.mark.django_db
class TestProjectFilterSet:

    def test_by_creator_username(self, project_factory, john, alice):
        john_project = project_factory(created_by=john)
        alice_project = project_factory(created_by=alice)

        queryset = Project.objects.all()
        filtered = ProjectFilterSet({"creator": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_project.pk

    def test_by_owner_username(self, project_factory, john, alice):
        john_project = project_factory(owner=john)
        alice_project = project_factory(owner=alice)

        queryset = Project.objects.all()
        filtered = ProjectFilterSet({"owner": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_project.pk

    def test_by_supervisor_username(self, project_factory, john, alice):
        john_project = project_factory(supervisor=john)
        alice_project = project_factory(supervisor=alice)

        queryset = Project.objects.all()
        filtered = ProjectFilterSet({"supervisor": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_project.pk

    def test_by_responsible_username(self, project_factory, john, alice):
        john_project = project_factory(responsible=john)
        alice_project = project_factory(responsible=alice)

        queryset = Project.objects.all()
        filtered = ProjectFilterSet({"responsible": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_project.pk


@pytest.mark.django_db
class TestProjectMembershipFilterSet:

    def test_by_creator_username(
        self, project, project_membership_factory, john, alice
    ):
        john_membership = project_membership_factory(created_by=john)
        alice_membership = project_membership_factory(created_by=alice)

        queryset = ProjectMembership.objects.all()
        filtered = ProjectMembershipFilterSet({"creator": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_membership.pk
