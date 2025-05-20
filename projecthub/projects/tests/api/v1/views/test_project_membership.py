from datetime import datetime

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.projects.models import ProjectMembership


@pytest.fixture
def list_url(project):
    return reverse(
        "api:v1:project_membership_list",
        kwargs={"project_id": project.pk}
    )


@pytest.fixture
def detail_url(project_membership):
    return reverse(
        "api:v1:project_membership_detail",
        kwargs={
            "project_id": project_membership.project_id,
            "pk": project_membership.pk,
        },
    )


@pytest.fixture
def data(user_factory):
    return {"user": user_factory().pk, "role": ProjectMembership.Role.READER}


@pytest.mark.django_db
class TestProjectMembershipListCreateAPIView:

    class TestPermissions:

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_403_FORBIDDEN), ("post", status.HTTP_403_FORBIDDEN)],
        )
        def test_anonymous_user(
                self, api_client, list_url, http_host, method, expected_status_code
        ):
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_404_NOT_FOUND), ("post", status.HTTP_404_NOT_FOUND)],
        )
        def test_not_tenant_member(
                self, api_client, list_url, http_host, user, method, expected_status_code
        ):
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_404_NOT_FOUND), ("post", status.HTTP_404_NOT_FOUND)],
        )
        def test_tenant_user_not_project_member(
                self,
                api_client,
                list_url,
                http_host,
                tenant_user,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_user.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_403_FORBIDDEN)],
        )
        def test_project_reader(
                self,
                api_client,
                list_url,
                http_host,
                project_reader,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_reader.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_403_FORBIDDEN)],
        )
        def test_project_guest(
                self,
                api_client,
                list_url,
                http_host,
                project_guest,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_guest.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_403_FORBIDDEN)],
        )
        def test_project_user(
                self,
                api_client,
                list_url,
                http_host,
                project_user,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_user.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_project_responsible(
                self,
                api_client,
                list_url,
                http_host,
                project_responsible,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_responsible.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_project_supervisor(
                self,
                api_client,
                list_url,
                http_host,
                project_supervisor,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_supervisor.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_project_owner(
                self,
                api_client,
                list_url,
                http_host,
                project_owner,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_owner.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_tenant_owner(
                self,
                api_client,
                list_url,
                http_host,
                tenant_owner,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_owner.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_admin(
                self, admin_client, list_url, http_host, data, method, expected_status_code
        ):
            response = getattr(admin_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

    def test_pagination_works(
            self, admin_client, list_url, project, project_membership_factory, http_host
    ):
        project_membership_factory.create_batch(
            5, project=project, role=ProjectMembership.Role.USER
        )
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filtering_works(
            self,
            admin_client,
            list_url,
            project,
            project_membership_factory,
            john,
            alice,
            http_host
    ):
        john_membership = project_membership_factory(project=project, created_by=john)
        alice_membership = project_membership_factory(project=project, created_by=alice)
        response = admin_client.get(list_url, {"creator": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {m["id"] for m in response.data["results"]} == {str(john_membership.pk)}

    def test_search_works(
            self,
            admin_client,
            list_url,
            project,
            project_membership_factory,
            john,
            alice,
            http_host
    ):
        john_membership = project_membership_factory(project=project, user=john)
        alice_membership = project_membership_factory(project=project, user=alice)

        response = admin_client.get(list_url, {"search": "jo"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {m["id"] for m in response.data["results"]} == {str(john_membership.pk)}

    def test_ordering_works(
            self, admin_client, list_url, project, project_membership_factory, http_host
    ):
        old_membership = project_membership_factory(
            created_at=timezone.make_aware(datetime(2000, 1, 1)),
            project=project
        )
        new_membership = project_membership_factory(
            created_at=timezone.make_aware(datetime(2000, 2, 2)),
            project=project
        )

        query_params = {"ordering": {"created_at"}}
        response = admin_client.get(list_url, query_params, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(old_membership.pk), str(new_membership.pk)]
        assert [m["id"] for m in response.data["results"]] == expected_ids


@pytest.mark.django_db
class TestProjectMembershipRetrieveUpdateDestroyAPIView:

    class TestPermissions:

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_403_FORBIDDEN),
                ("put", status.HTTP_403_FORBIDDEN),
                ("patch", status.HTTP_403_FORBIDDEN),
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_anonymous_user(
                self, api_client, detail_url, http_host, method, expected_status_code
        ):
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_404_NOT_FOUND),
                ("put", status.HTTP_404_NOT_FOUND),
                ("patch", status.HTTP_404_NOT_FOUND),
                ("delete", status.HTTP_404_NOT_FOUND),
            ],
        )
        def test_not_tenant_member(
                self,
                api_client,
                detail_url,
                http_host,
                user_factory,
                method,
                expected_status_code,
        ):
            user = user_factory()
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_404_NOT_FOUND),
                ("put", status.HTTP_404_NOT_FOUND),
                ("patch", status.HTTP_404_NOT_FOUND),
                ("delete", status.HTTP_404_NOT_FOUND),
            ],
        )
        def test_tenant_user_not_project_member(
                self,
                api_client,
                detail_url,
                http_host,
                tenant_user,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_user.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_403_FORBIDDEN),
                ("patch", status.HTTP_403_FORBIDDEN),
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_project_reader(
                self,
                api_client,
                detail_url,
                http_host,
                project_reader,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_reader.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_403_FORBIDDEN),
                ("patch", status.HTTP_403_FORBIDDEN),
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_project_guest(
                self,
                api_client,
                detail_url,
                http_host,
                project_guest,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_guest.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_403_FORBIDDEN),
                ("patch", status.HTTP_403_FORBIDDEN),
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_project_user(
                self,
                api_client,
                detail_url,
                http_host,
                project_user,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_user.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_200_OK),
                ("patch", status.HTTP_200_OK),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_project_responsible(
                self,
                api_client,
                detail_url,
                http_host,
                project_responsible,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_responsible.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_200_OK),
                ("patch", status.HTTP_200_OK),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_project_supervisor(
                self,
                api_client,
                detail_url,
                http_host,
                project_supervisor,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_supervisor.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_200_OK),
                ("patch", status.HTTP_200_OK),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_project_owner(
                self,
                api_client,
                detail_url,
                http_host,
                project_owner,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_owner.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_200_OK),
                ("patch", status.HTTP_200_OK),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_tenant_owner(
                self,
                api_client,
                detail_url,
                http_host,
                tenant_owner,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_owner.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_200_OK),
                ("patch", status.HTTP_200_OK),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_admin_user(
                self, admin_client, detail_url, http_host, method, expected_status_code
        ):
            response = getattr(admin_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        class TestDelete:

            @pytest.mark.parametrize("role", [
                ProjectMembership.Role.OWNER,
                ProjectMembership.Role.SUPERVISOR,
                ProjectMembership.Role.RESPONSIBLE,
                ProjectMembership.Role.USER,
                ProjectMembership.Role.GUEST,
                ProjectMembership.Role.READER
            ])
            def test_admin_can_delete_any_member(
                    self, admin_client, detail_url, project_membership, http_host, role
            ):
                project_membership.role = role
                project_membership.save()

                response = admin_client.delete(detail_url, HTTP_HOST=http_host)
                assert response.status_code == status.HTTP_204_NO_CONTENT

            @pytest.mark.parametrize("method, role, expected_status_code", [
                ("put", ProjectMembership.Role.OWNER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.OWNER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.OWNER, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.SUPERVISOR, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.SUPERVISOR, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.SUPERVISOR, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.RESPONSIBLE, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.RESPONSIBLE, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.RESPONSIBLE, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.USER, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.GUEST, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.READER, status.HTTP_204_NO_CONTENT)
            ])
            def test_tenant_owner_can_manage_any_member(
                    self,
                    api_client,
                    detail_url,
                    tenant_owner,
                    project_membership,
                    http_host,
                    method,
                    role,
                    expected_status_code
            ):
                api_client.force_authenticate(user=tenant_owner.user)

                project_membership.role = role
                project_membership.save()

                response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
                assert response.status_code == expected_status_code

            @pytest.mark.parametrize("method, role, expected_status_code", [
                ("put", ProjectMembership.Role.OWNER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.OWNER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.OWNER, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.SUPERVISOR, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.SUPERVISOR, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.SUPERVISOR, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.RESPONSIBLE, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.RESPONSIBLE, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.RESPONSIBLE, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.USER, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.GUEST, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.READER, status.HTTP_204_NO_CONTENT)
            ])
            def test_project_owner_can_manage_any_member(
                    self,
                    api_client,
                    detail_url,
                    project_owner,
                    project_membership,
                    http_host,
                    method,
                    role,
                    expected_status_code
            ):
                api_client.force_authenticate(user=project_owner.user)

                project_membership.role = role
                project_membership.save()

                response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
                assert response.status_code == expected_status_code

            @pytest.mark.parametrize("method, role, expected_status_code", [
                ("put", ProjectMembership.Role.OWNER, status.HTTP_403_FORBIDDEN),
                ("patch", ProjectMembership.Role.OWNER, status.HTTP_403_FORBIDDEN),
                ("delete", ProjectMembership.Role.OWNER, status.HTTP_403_FORBIDDEN),
                ("put", ProjectMembership.Role.RESPONSIBLE, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.RESPONSIBLE, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.RESPONSIBLE, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.USER, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.GUEST, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.READER, status.HTTP_204_NO_CONTENT)
            ])
            def test_project_supervisor_can_manage_responsible_and_below(
                    self,
                    api_client,
                    detail_url,
                    project_supervisor,
                    project_membership,
                    http_host,
                    method,
                    role,
                    expected_status_code
            ):
                api_client.force_authenticate(user=project_supervisor.user)

                project_membership.role = role
                project_membership.save()

                response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
                assert response.status_code == expected_status_code

            @pytest.mark.parametrize("method, role, expected_status_code", [
                ("put", ProjectMembership.Role.OWNER, status.HTTP_403_FORBIDDEN),
                ("patch", ProjectMembership.Role.OWNER, status.HTTP_403_FORBIDDEN),
                ("delete", ProjectMembership.Role.OWNER, status.HTTP_403_FORBIDDEN),
                ("put", ProjectMembership.Role.SUPERVISOR, status.HTTP_403_FORBIDDEN),
                ("patch", ProjectMembership.Role.SUPERVISOR, status.HTTP_403_FORBIDDEN),
                ("delete", ProjectMembership.Role.SUPERVISOR, status.HTTP_403_FORBIDDEN),
                ("put", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.USER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.USER, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.GUEST, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.GUEST, status.HTTP_204_NO_CONTENT),
                ("put", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("patch", ProjectMembership.Role.READER, status.HTTP_200_OK),
                ("delete", ProjectMembership.Role.READER, status.HTTP_204_NO_CONTENT)
            ])
            def test_project_responsible_can_delete_user_and_below(
                    self,
                    api_client,
                    detail_url,
                    project_responsible,
                    project_membership,
                    http_host,
                    method,
                    role,
                    expected_status_code
            ):
                api_client.force_authenticate(user=project_responsible.user)

                project_membership.role = role
                project_membership.save()

                response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
                assert response.status_code == expected_status_code

            @pytest.mark.parametrize("role", [
                ProjectMembership.Role.OWNER,
                ProjectMembership.Role.SUPERVISOR,
                ProjectMembership.Role.RESPONSIBLE,
                ProjectMembership.Role.USER,
                ProjectMembership.Role.GUEST,
                ProjectMembership.Role.READER
            ])
            def test_any_member_can_delete_self(
                    self,
                    api_client,
                    detail_url,
                    project_membership,
                    http_host,
                    role,
            ):
                api_client.force_authenticate(user=project_membership.user)
                project_membership.role = role
                project_membership.save()

                response = api_client.delete(detail_url, HTTP_HOST=http_host)
                assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_perform_update(
            self, admin_client, detail_url, admin_user, http_host, project_membership
    ):
        data = {"role": ProjectMembership.Role.READER}
        response = admin_client.patch(
            detail_url, data=data, HTTP_HOST=http_host, content_type="application/json"
        )
        assert response.status_code == status.HTTP_200_OK
        project_membership.refresh_from_db()
        assert project_membership.updated_by == admin_user