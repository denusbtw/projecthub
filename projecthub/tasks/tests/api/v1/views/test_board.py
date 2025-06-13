import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.projects.models import ProjectMembership
from projecthub.tasks.models import Board


@pytest.fixture
def list_url(active_project):
    return reverse("api:v1:board_list", kwargs={"project_id": active_project.pk})


@pytest.fixture
def detail_url(board_factory, active_project):
    board = board_factory(project=active_project, name="To Do", order=1)
    return reverse(
        "api:v1:board_detail",
        kwargs={"project_id": active_project.pk, "pk": board.pk},
    )


@pytest.fixture
def data():
    return {"name": "Custom board", "order": 10}


@pytest.mark.django_db
class TestBoardListCreateAPIView:

    class TestPermissions:

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_403_FORBIDDEN),
                ("post", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_anonymous_user(
            self, api_client, list_url, http_host, method, expected_status_code
        ):
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_404_NOT_FOUND),
                ("post", status.HTTP_404_NOT_FOUND),
            ],
        )
        def test_not_tenant_member(
            self,
            api_client,
            list_url,
            http_host,
            user_factory,
            method,
            expected_status_code,
        ):
            user = user_factory()
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
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
            tenant,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=tenant.owner)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_404_NOT_FOUND), ("post", status.HTTP_404_NOT_FOUND)],
        )
        def test_not_project_member(
            self,
            api_client,
            list_url,
            http_host,
            tenant,
            tenant_membership_factory,
            data,
            method,
            expected_status_code,
        ):
            tenant_membership = tenant_membership_factory(tenant=tenant)
            api_client.force_authenticate(user=tenant_membership.user)
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
            active_project,
            project_membership_factory,
            data,
            method,
            expected_status_code,
        ):
            project_membership = project_membership_factory(
                project=active_project, role=ProjectMembership.Role.USER
            )
            api_client.force_authenticate(user=project_membership.user)
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
            active_project,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.supervisor)
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
            active_project,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.owner)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_admin(
            self,
            admin_client,
            list_url,
            http_host,
            data,
            method,
            expected_status_code,
        ):
            response = getattr(admin_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

    def test_lists_only_board_of_specific_project(
        self,
        admin_client,
        list_url,
        active_project,
        project_factory,
        board_factory,
        http_host,
    ):
        board_factory.create_batch(3, project=active_project)

        another_project = project_factory(active=True)
        board_factory.create_batch(2, project=another_project)

        response = admin_client.get(list_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_pagination_works(
        self, admin_client, list_url, active_project, board_factory, http_host
    ):
        board_factory.create_batch(5, project=active_project)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(
        self, admin_client, list_url, active_project, data, http_host
    ):
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_201_CREATED

        board = Board.objects.get(id=response.data["id"])
        assert board.project == active_project

    def test_search_works(
        self, admin_client, list_url, active_project, board_factory, http_host
    ):
        abc_board = board_factory(name="abc", project=active_project, order=5)
        qwe_board = board_factory(name="qwe", project=active_project, order=6)

        response = admin_client.get(list_url, {"search": "ab"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {s["id"] for s in response.data["results"]} == {str(abc_board.pk)}

    def test_ordering_works(
        self, admin_client, list_url, active_project, board_factory, http_host
    ):
        a_board = board_factory(name="a", project=active_project, order=1)
        z_board = board_factory(name="z", project=active_project, order=5)

        response = admin_client.get(
            list_url, {"ordering": "-order"}, HTTP_HOST=http_host
        )
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(z_board.pk), str(a_board.pk)]
        assert [s["id"] for s in response.data["results"]] == expected_ids


@pytest.mark.django_db
class TestBoardRetrieveUpdateDestroyAPIView:

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
        def test_tenant_user(
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
            tenant,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=tenant.owner)
            response = getattr(api_client, method)(
                detail_url, data=data, HTTP_HOST=http_host
            )
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
        def test_not_project_member(
            self,
            api_client,
            detail_url,
            http_host,
            user,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(
                detail_url, data=data, HTTP_HOST=http_host
            )
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
            active_project,
            project_membership_factory,
            data,
            method,
            expected_status_code,
        ):
            project_membership = project_membership_factory(
                project=active_project, role=ProjectMembership.Role.USER
            )
            api_client.force_authenticate(user=project_membership.user)
            response = getattr(api_client, method)(
                detail_url, data=data, HTTP_HOST=http_host
            )
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
            active_project,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.supervisor)
            response = getattr(api_client, method)(
                detail_url, data=data, HTTP_HOST=http_host
            )
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
            active_project,
            data,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.owner)
            response = getattr(api_client, method)(
                detail_url, data=data, HTTP_HOST=http_host
            )
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
        def test_admin(
            self,
            admin_client,
            detail_url,
            http_host,
            data,
            method,
            expected_status_code,
        ):
            response = getattr(admin_client, method)(
                detail_url,
                data=data,
                HTTP_HOST=http_host,
                content_type="application/json",
            )
            assert response.status_code == expected_status_code
