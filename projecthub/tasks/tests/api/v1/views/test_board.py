import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.tasks.models import Board


@pytest.fixture
def list_url(project):
    return reverse("api:v1:board_list", kwargs={"project_id": project.pk})


@pytest.fixture
def detail_url(done_board, project):
    return reverse(
        "api:v1:board_detail",
        kwargs={"project_id": project.pk, "pk": done_board.pk},
    )


@pytest.fixture
def data():
    return {"name": "To Do", "type": Board.Type.TODO, "order": 10}


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
        project,
        project_factory,
        board_factory,
        http_host,
    ):
        board_factory.create_batch(3, project=project, type=Board.Type.CUSTOM)

        another_project = project_factory()
        board_factory.create_batch(2, project=another_project, type=Board.Type.CUSTOM)

        response = admin_client.get(list_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_pagination_works(
        self, admin_client, list_url, project, board_factory, http_host
    ):
        board_factory.create_batch(5, project=project, type=Board.Type.CUSTOM)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(
        self, admin_client, list_url, project, data, http_host, admin_user
    ):
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_201_CREATED

        board = Board.objects.get(id=response.data["id"])
        assert board.project == project
        assert board.created_by == admin_user
        assert board.updated_by == admin_user

    def test_filtering_works(
        self, admin_client, list_url, project, john, alice, http_host, board_factory
    ):
        john_board = board_factory(
            project=project, created_by=john, type=Board.Type.CUSTOM
        )
        alice_board = board_factory(
            project=project, created_by=alice, type=Board.Type.CUSTOM
        )
        response = admin_client.get(list_url, {"creator": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {s["id"] for s in response.data["results"]} == {str(john_board.pk)}

    def test_search_works(
        self, admin_client, list_url, project, board_factory, http_host
    ):
        abc_board = board_factory(name="abc", project=project, type=Board.Type.CUSTOM)
        qwe_board = board_factory(name="qwe", project=project, type=Board.Type.CUSTOM)

        response = admin_client.get(list_url, {"search": "ab"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {s["id"] for s in response.data["results"]} == {str(abc_board.pk)}

    def test_ordering_works(
        self, admin_client, list_url, project, board_factory, http_host
    ):
        a_board = board_factory(name="a", project=project, type=Board.Type.CUSTOM)
        z_board = board_factory(name="z", project=project, type=Board.Type.CUSTOM)

        response = admin_client.get(list_url, {"ordering": "name"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(a_board.pk), str(z_board.pk)]
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

    def test_perform_update(
        self, admin_client, detail_url, done_board, http_host, admin_user
    ):
        response = admin_client.patch(detail_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        done_board.refresh_from_db()
        assert done_board.updated_by == admin_user
