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

    def test_error_if_project_is_archived(self, tenant, user, archived_project):
        data = {"user": user.pk, "role": ProjectMembership.Role.USER}
        context = {"project": archived_project}
        serializer = ProjectMembershipCreateSerializer(data=data, context=context)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "archived" in str(exc.value)

    def test_error_if_user_is_tenant_owner(self, tenant, active_project):
        data = {"user": tenant.owner_id, "role": ProjectMembership.Role.USER}
        context = {"project": active_project}
        serializer = ProjectMembershipCreateSerializer(data=data, context=context)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Owner of tenant" in str(exc.value)

    def test_error_if_user_is_project_owner(self, active_project):
        data = {"user": active_project.owner_id, "role": ProjectMembership.Role.USER}
        context = {"project": active_project}
        serializer = ProjectMembershipCreateSerializer(data=data, context=context)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Owner of tenant" in str(exc.value)

    def test_error_if_user_is_project_supervisor(self, active_project):
        data = {
            "user": active_project.supervisor_id,
            "role": ProjectMembership.Role.USER,
        }
        context = {"project": active_project}
        serializer = ProjectMembershipCreateSerializer(data=data, context=context)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Owner of tenant" in str(exc.value)

    def test_error_if_user_is_not_member_of_tenant(self, tenant, user, active_project):
        data = {"user": user.pk, "role": ProjectMembership.Role.USER}
        context = {"project": active_project}
        serializer = ProjectMembershipCreateSerializer(data=data, context=context)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "User must be member of tenant." in str(exc.value)


@pytest.mark.django_db
class TestProjectMembershipUpdateSerializer:

    def test_no_error_if_empty_data(self, project_membership_factory):
        membership = project_membership_factory()
        serializer = ProjectMembershipUpdateSerializer(membership, data={})
        assert serializer.is_valid(), serializer.errors
