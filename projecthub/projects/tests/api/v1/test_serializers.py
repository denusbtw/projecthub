import pytest
from rest_framework import serializers

from projecthub.projects.api.v1.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectMembershipListSerializer,
    ProjectMembershipDetailSerializer,
    ProjectMembershipUpdateSerializer,
    ProjectMembershipCreateSerializer,
)
from projecthub.projects.models import Project, ProjectMembership


@pytest.fixture
def data():
    return {"name": "my project", "status": Project.Status.ACTIVE}


@pytest.mark.django_db
class TestProjectListSerializer:

    def test_status_is_correct(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        project.role = ""
        serializer = ProjectListSerializer(project)
        assert serializer.data["status"] == project.get_status_display()


@pytest.mark.django_db
class TestProjectDetailSerializer:

    def test_status_is_correct(self, project_factory):
        project = project_factory(status=Project.Status.ACTIVE)
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["status"] == project.get_status_display()

    def test_owner_is_nested_serializer(self, project, project_membership_factory):
        owner_membership = project_membership_factory(
            project=project, role=ProjectMembership.Role.OWNER
        )
        project.role = ""
        serializer = ProjectDetailSerializer(project)
        assert serializer.data["owner"]["id"] == str(owner_membership.id)


@pytest.mark.django_db
class TestProjectCreateSerializer:

    def test_to_representation_matches_list_serializer_representation(
        self, tenant, data
    ):
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        project = serializer.save(tenant=tenant)
        assert serializer.data == ProjectListSerializer(project).data

    def test_to_representation_sets_owner_role(self, tenant, data):
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        serializer.save(tenant=tenant)
        assert serializer.data["role"] == ProjectMembership.Role.OWNER


@pytest.mark.django_db
class TestProjectUpdateSerializer:

    def test_no_error_if_empty_data(self, project):
        serializer = ProjectUpdateSerializer(project, data={})
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestProjectMembershipListSerializer:

    def test_role_is_correct(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.OWNER)
        serializer = ProjectMembershipListSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestProjectMembershipDetailSerializer:

    def test_role_is_correct(self, project_membership_factory):
        membership = project_membership_factory(role=ProjectMembership.Role.OWNER)
        serializer = ProjectMembershipDetailSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestProjectMembershipCreateSerializer:

    class TestValidateRole:

        def test_error_if_no_request(self, user):
            data = {"user": user.pk, "role": ProjectMembership.Role.USER}
            serializer = ProjectMembershipCreateSerializer(data=data, context={})
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]) == "Request is required."

        def test_error_if_request_has_no_user(self, user, rf):
            request = rf.get("/")
            request.user = None

            data = {"user": user.pk, "role": ProjectMembership.Role.USER}
            context = {"request": request}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]) == "Request is required."

        def test_error_if_no_project_id_in_context(self, user, admin_user, rf):
            request = rf.get("/")
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.USER}
            context = {"request": request}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]) == "project_id is required in context."

        def test_error_if_role_is_owner_and_supervisor_exists(
                self, user, admin_user, tenant, project, project_membership_factory, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            project_membership_factory(project=project, role=ProjectMembership.Role.SUPERVISOR)

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]).startswith("You can't assign")

        def test_error_if_role_is_supervisor_and_responsible_exists(
                self, user, admin_user, tenant, project, project_membership_factory, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            project_membership_factory(project=project, role=ProjectMembership.Role.RESPONSIBLE)

            data = {"user": user.pk, "role": ProjectMembership.Role.SUPERVISOR}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]).startswith("You can't assign")

        def test_no_error_if_role_is_owner_and_supervisor_does_not_exist(
                self, user, admin_user, tenant, project, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_role_is_supervisor_and_responsible_does_not_exist(
                self, user, admin_user, tenant, project, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.SUPERVISOR}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_role_is_responsible(
                self, user, admin_user, tenant, project, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.RESPONSIBLE}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

        def test_error_if_supervisor_creates_owner(
                self, user, project_supervisor, tenant, project, rf
        ):
            request = rf.get("/")
            request.user = project_supervisor.user
            request.tenant = tenant

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)

        @pytest.mark.parametrize("role", [
            ProjectMembership.Role.OWNER,
            ProjectMembership.Role.SUPERVISOR
        ])
        def test_error_if_responsible_creates_owner_or_supervisor(
                self, user, project_responsible, tenant, project, rf, role
        ):
            request = rf.get("/")
            request.user = project_responsible.user
            request.tenant = tenant

            data = {"user": user.pk, "role": role}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)

    class TestCreate:

        def test_previous_owner_is_demoted_to_supervisor_if_role_is_owner(
                self, user, admin_user, tenant, project, project_membership_factory, rf
        ):
            request = rf.get("/")
            request.user = admin_user
            request.tenant = tenant

            owner_membership = project_membership_factory(
                project=project, role=ProjectMembership.Role.OWNER
            )

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

            new_membership = serializer.save()
            assert new_membership.is_owner

            owner_membership.refresh_from_db()
            assert owner_membership.is_supervisor

        def test_previous_supervisor_is_demoted_to_responsible_if_role_is_supervisor(
                self, user, admin_user, tenant, project, project_membership_factory, rf
        ):
            request = rf.get("/")
            request.user = admin_user
            request.tenant = tenant

            supervisor_membership = project_membership_factory(
                project=project, role=ProjectMembership.Role.SUPERVISOR
            )

            data = {"user": user.pk, "role": ProjectMembership.Role.SUPERVISOR}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

            new_membership = serializer.save()
            assert new_membership.is_supervisor

            supervisor_membership.refresh_from_db()
            assert supervisor_membership.is_responsible

        def test_previous_responsible_is_demoted_to_user_if_role_is_responsible(
                self, user, admin_user, tenant, project, project_membership_factory, rf
        ):
            request = rf.get("/")
            request.user = admin_user
            request.tenant = tenant

            responsible_membership = project_membership_factory(
                project=project, role=ProjectMembership.Role.RESPONSIBLE
            )

            data = {"user": user.pk, "role": ProjectMembership.Role.RESPONSIBLE}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipCreateSerializer(data=data, context=context)
            assert serializer.is_valid(), serializer.errors

            new_membership = serializer.save()
            assert new_membership.is_responsible

            responsible_membership.refresh_from_db()
            assert responsible_membership.is_user


@pytest.mark.django_db
class TestProjectMembershipUpdateSerializer:

    def test_no_error_if_empty_data(self, project_membership_factory):
        membership = project_membership_factory()
        serializer = ProjectMembershipUpdateSerializer(membership, data={})
        assert serializer.is_valid(), serializer.errors

    class TestValidateRole:

        def test_error_if_no_request(self, project_membership, user):
            data = {"user": user.pk, "role": ProjectMembership.Role.USER}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context={}
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]) == "Request is required."

        def test_error_if_request_has_no_user(self, project_membership, user, rf):
            request = rf.get("/")
            request.user = None

            data = {"user": user.pk, "role": ProjectMembership.Role.USER}
            context = {"request": request}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]) == "Request is required."

        def test_error_if_no_project_id_in_context(
                self, user, admin_user, project_membership, rf):
            request = rf.get("/")
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.USER}
            context = {"request": request}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]) == "project_id is required in context."

        def test_error_if_role_is_owner_and_supervisor_exists(
                self, user, admin_user, tenant, project, project_membership_factory,
                project_membership, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            project_membership_factory(project=project, role=ProjectMembership.Role.SUPERVISOR)

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]).startswith("You can't assign")

        def test_error_if_role_is_supervisor_and_responsible_exists(
                self, user, admin_user, tenant, project, project_membership_factory,
                project_membership, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            project_membership_factory(project=project, role=ProjectMembership.Role.RESPONSIBLE)

            data = {"user": user.pk, "role": ProjectMembership.Role.SUPERVISOR}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)
            assert str(exc.value.detail["role"][0]).startswith("You can't assign")

        def test_no_error_if_role_is_owner_and_supervisor_does_not_exist(
                self, user, admin_user, tenant, project, project_membership, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_role_is_supervisor_and_responsible_does_not_exist(
                self, user, admin_user, tenant, project, project_membership, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.SUPERVISOR}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            assert serializer.is_valid(), serializer.errors

        def test_no_error_if_role_is_responsible(
                self, user, admin_user, tenant, project, project_membership, rf
        ):
            request = rf.get("/")
            request.tenant = tenant
            request.user = admin_user

            data = {"user": user.pk, "role": ProjectMembership.Role.RESPONSIBLE}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            assert serializer.is_valid(), serializer.errors

        def test_error_if_supervisor_creates_owner(
                self, user, project_supervisor, tenant, project, project_membership, rf
        ):
            request = rf.get("/")
            request.user = project_supervisor.user
            request.tenant = tenant

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)

        @pytest.mark.parametrize("role", [
            ProjectMembership.Role.OWNER,
            ProjectMembership.Role.SUPERVISOR
        ])
        def test_error_if_responsible_creates_owner_or_supervisor(
                self, user, project_responsible, tenant, project,
                project_membership, rf, role
        ):
            request = rf.get("/")
            request.user = project_responsible.user
            request.tenant = tenant

            data = {"user": user.pk, "role": role}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            with pytest.raises(serializers.ValidationError) as exc:
                serializer.is_valid(raise_exception=True)

    class TestUpdate:

        def test_previous_owner_is_demoted_to_supervisor_if_role_is_owner(
                self, user, admin_user, tenant, project, project_membership_factory,
                project_membership, rf
        ):
            request = rf.get("/")
            request.user = admin_user
            request.tenant = tenant

            owner_membership = project_membership_factory(
                project=project, role=ProjectMembership.Role.OWNER
            )

            data = {"user": user.pk, "role": ProjectMembership.Role.OWNER}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            assert serializer.is_valid(), serializer.errors

            new_membership = serializer.save()
            assert new_membership.is_owner

            owner_membership.refresh_from_db()
            assert owner_membership.is_supervisor

        def test_previous_supervisor_is_demoted_to_responsible_if_role_is_supervisor(
                self, user, admin_user, tenant, project, project_membership_factory,
                project_membership, rf
        ):
            request = rf.get("/")
            request.user = admin_user
            request.tenant = tenant

            supervisor_membership = project_membership_factory(
                project=project, role=ProjectMembership.Role.SUPERVISOR
            )

            data = {"user": user.pk, "role": ProjectMembership.Role.SUPERVISOR}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            assert serializer.is_valid(), serializer.errors

            new_membership = serializer.save()
            assert new_membership.is_supervisor

            supervisor_membership.refresh_from_db()
            assert supervisor_membership.is_responsible

        def test_previous_responsible_is_demoted_to_user_if_role_is_responsible(
                self, user, admin_user, tenant, project, project_membership_factory,
                project_membership, rf
        ):
            request = rf.get("/")
            request.user = admin_user
            request.tenant = tenant

            responsible_membership = project_membership_factory(
                project=project, role=ProjectMembership.Role.RESPONSIBLE
            )

            data = {"user": user.pk, "role": ProjectMembership.Role.RESPONSIBLE}
            context = {"request": request, "project_id": project.pk}
            serializer = ProjectMembershipUpdateSerializer(
                project_membership, data=data, context=context
            )
            assert serializer.is_valid(), serializer.errors

            new_membership = serializer.save()
            assert new_membership.is_responsible

            responsible_membership.refresh_from_db()
            assert responsible_membership.is_user
