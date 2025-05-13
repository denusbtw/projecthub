from datetime import datetime

import pytest
from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError

from projecthub.projects.models import Project, ProjectMembership


@pytest.mark.django_db
class TestProject:

    def test_error_if_start_date_after_end_date(self, tenant):
        start_date = timezone.make_aware(datetime(2001, 1, 1))
        end_date = timezone.make_aware(datetime(2000, 1, 1))

        with pytest.raises(IntegrityError):
            Project.objects.create(
                tenant=tenant,
                name="my project",
                start_date=start_date,
                end_date=end_date,
            )

    def test_activate_raises_error_without_updated_by(self, project):
        with pytest.raises(ValidationError, match="updated_by is required."):
            project.activate(updated_by=None)

    def test_activate_sets_active_status_and_updated_by(self, project_factory, user):
        project = project_factory(status=Project.Status.PENDING)
        project.activate(updated_by=user)
        assert project.is_active
        assert project.updated_by == user

    def test_mark_pending_raises_error_without_updated_by(self, project):
        with pytest.raises(ValidationError, match="updated_by is required."):
            project.mark_pending(updated_by=None)

    def test_mark_pending_sets_pending_status_and_updated_by(
        self, project_factory, user
    ):
        project = project_factory(status=Project.Status.ACTIVE)
        project.mark_pending(updated_by=user)
        assert project.is_pending
        assert project.updated_by == user

    def test_archive_raises_error_without_updated_by(self, project):
        with pytest.raises(ValidationError, match="updated_by is required."):
            project.archive(updated_by=None)

    def test_archive_sets_archived_status_and_updated_by(self, project_factory, user):
        project = project_factory(status=Project.Status.ACTIVE)
        project.archive(updated_by=user)
        assert project.is_archived
        assert project.updated_by == user
        assert project.close_date is not None

    def test_is_active_property(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        assert project.is_active
        assert not project.is_pending
        assert not project.is_archived

    def test_is_pending_property(self, project_factory):
        project = project_factory(status=Project.Status.PENDING)
        assert not project.is_active
        assert project.is_pending
        assert not project.is_archived

    def test_is_archived_property(self, project_factory):
        project = project_factory(status=Project.Status.ARCHIVED)
        assert not project.is_active
        assert not project.is_pending
        assert project.is_archived

    def test_duration(self, project_factory):
        start_date = timezone.make_aware(datetime(2000, 1, 1))
        end_date = timezone.make_aware(datetime(2000, 1, 5))
        project = project_factory(start_date=start_date, end_date=end_date)
        assert project.duration.days == 4


@pytest.mark.django_db
class TestProjectMembership:

    def test_error_if_user_is_already_member_of_project(
        self, user, project, project_membership_factory
    ):
        project_membership_factory(project=project, user=user)
        with pytest.raises(IntegrityError):
            project_membership_factory(project=project, user=user)

    def test_error_if_owner_already_exists(
        self, project, user, project_membership_factory
    ):
        project_membership_factory(project=project, role=ProjectMembership.Role.OWNER)

        membership = ProjectMembership(
            project=project, user=user, role=ProjectMembership.Role.OWNER
        )
        with pytest.raises(
            ValidationError, match="Project already has a user with role"
        ):
            membership.full_clean()

    def test_error_if_supervisor_already_exists(
        self, project, user, project_membership_factory
    ):
        project_membership_factory(
            project=project, role=ProjectMembership.Role.SUPERVISOR
        )

        membership = ProjectMembership(
            project=project, user=user, role=ProjectMembership.Role.SUPERVISOR
        )
        with pytest.raises(
            ValidationError, match="Project already has a user with role"
        ):
            membership.full_clean()

    def test_error_if_responsible_already_exists(
        self, project, user, project_membership_factory
    ):
        project_membership_factory(
            project=project, role=ProjectMembership.Role.RESPONSIBLE
        )

        membership = ProjectMembership(
            project=project, user=user, role=ProjectMembership.Role.RESPONSIBLE
        )
        with pytest.raises(
            ValidationError, match="Project already has a user with role"
        ):
            membership.full_clean()

    def test_no_error_if_user_already_exists(
        self, project, user, project_membership_factory
    ):
        project_membership_factory(project=project, role=ProjectMembership.Role.USER)
        membership = ProjectMembership(
            project=project, user=user, role=ProjectMembership.Role.USER
        )
        membership.full_clean()

    def test_no_error_if_guest_already_exists(
        self, project, user, project_membership_factory
    ):
        project_membership_factory(project=project, role=ProjectMembership.Role.GUEST)
        membership = ProjectMembership(
            project=project, user=user, role=ProjectMembership.Role.GUEST
        )
        membership.full_clean()

    def test_no_error_if_reader_already_exists(
        self, project, user, project_membership_factory
    ):
        project_membership_factory(project=project, role=ProjectMembership.Role.READER)
        membership = ProjectMembership(
            project=project, user=user, role=ProjectMembership.Role.READER
        )
        membership.full_clean()

    def test_is_owner_property(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.OWNER)
        assert membership.is_owner
        assert not membership.is_supervisor
        assert not membership.is_responsible
        assert not membership.is_user
        assert not membership.is_guest
        assert not membership.is_reader

    def test_is_supervisor_property(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.SUPERVISOR)
        assert not membership.is_owner
        assert membership.is_supervisor
        assert not membership.is_responsible
        assert not membership.is_user
        assert not membership.is_guest
        assert not membership.is_reader

    def test_is_responsible_property(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.RESPONSIBLE)
        assert not membership.is_owner
        assert not membership.is_supervisor
        assert membership.is_responsible
        assert not membership.is_user
        assert not membership.is_guest
        assert not membership.is_reader

    def test_is_user_property(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.USER)
        assert not membership.is_owner
        assert not membership.is_supervisor
        assert not membership.is_responsible
        assert membership.is_user
        assert not membership.is_guest
        assert not membership.is_reader

    def test_is_guest_property(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.GUEST)
        assert not membership.is_owner
        assert not membership.is_supervisor
        assert not membership.is_responsible
        assert not membership.is_user
        assert membership.is_guest
        assert not membership.is_reader

    def test_is_reader_property(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.READER)
        assert not membership.is_owner
        assert not membership.is_supervisor
        assert not membership.is_responsible
        assert not membership.is_user
        assert not membership.is_guest
        assert membership.is_reader
