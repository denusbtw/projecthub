from datetime import timedelta

import pytest
from django.utils import timezone

from projecthub.projects.models import Project
from projecthub.projects.tasks import archive_ended_projects


@pytest.mark.django_db
class TestArchiveEndedProjects:

    def test_archives_ended_projects_with_zero_open_tasks(
        self, project_factory, task_factory
    ):
        project = project_factory(status=Project.Status.ACTIVE, end_date=timezone.now())
        task_factory(project=project, close_date=timezone.now())

        archive_ended_projects()
        project.refresh_from_db()

        assert project.is_archived

    def test_does_not_archive_project_if_it_has_at_least_one_open_task(
        self, project_factory, task_factory
    ):
        project = project_factory(status=Project.Status.ACTIVE, end_date=timezone.now())
        task_factory(project=project, close_date=None)

        archive_ended_projects()
        project.refresh_from_db()

        assert not project.is_archived

    def test_not_ended_project_is_not_archived(self, project_factory):
        project = project_factory(
            status=Project.Status.ACTIVE, end_date=timezone.now() + timedelta(days=3)
        )
        archive_ended_projects()
        project.refresh_from_db()
        assert not project.is_archived
