import pytest
from rest_framework.exceptions import ValidationError

from projecthub.projects.api.v1.serializers import (
    ProjectMembershipListSerializer,
    ProjectMembershipDetailSerializer,
    ProjectMembershipCreateSerializer,
    ProjectMembershipUpdateSerializer,
)
from projecthub.projects.models import ProjectMembership


@pytest.mark.django_db
class TestProjectMembershipListSerializer:

    def test_role_is_correct(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.USER)
        serializer = ProjectMembershipListSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestProjectMembershipDetailSerializer:

    def test_role_is_correct(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.USER)
        serializer = ProjectMembershipDetailSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestProjectMembershipCreateSerializer:

    def test_error_if_empty_data(self):
        serializer = ProjectMembershipCreateSerializer(data={})
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
class TestProjectMembershipUpdateSerializer:

    def test_no_error_if_empty_data(self, project_membership_factory):
        membership = project_membership_factory()
        serializer = ProjectMembershipUpdateSerializer(membership, data={})
        assert serializer.is_valid(), serializer.errors
