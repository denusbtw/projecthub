import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.tasks.models import TaskStatus


@pytest.fixture
def list_url():
    return reverse("api:v1:task_status_list")


@pytest.fixture
def detail_url(done_task_status):
    return reverse(
        "api:v1:task_status_detail",
        kwargs={"pk": done_task_status.pk}
    )


@pytest.fixture
def data():
    return {"name": "To Do", "code": "todo", "order": 10}


@pytest.mark.django_db
class TestTaskStatusListCreateAPIView:

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
            [("get", status.HTTP_200_OK), ("post", status.HTTP_403_FORBIDDEN)],
        )
        def test_tenant_user(
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

    def test_lists_only_task_statuses_of_request_tenant(
            self,
            admin_client,
            list_url,
            tenant,
            tenant_factory,
            task_status_factory,
            http_host,
    ):
        task_status_factory.create_batch(3, tenant=tenant)

        another_tenant = tenant_factory()
        task_status_factory.create_batch(1, tenant=another_tenant)

        response = admin_client.get(list_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_pagination_works(
            self, admin_client, list_url, tenant, task_status_factory, http_host
    ):
        task_status_factory.create_batch(5, tenant=tenant)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(
            self, admin_client, list_url, tenant, data, http_host, admin_user
    ):
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_201_CREATED
        task_status = TaskStatus.objects.get(id=response.data["id"])
        assert task_status.tenant == tenant
        assert task_status.created_by == admin_user
        assert task_status.updated_by == admin_user

    def test_filtering_works(
            self,
            admin_client,
            list_url,
            tenant,
            john,
            alice,
            http_host,
            task_status_factory
    ):
        john_status = task_status_factory(tenant=tenant, created_by=john)
        alice_status = task_status_factory(tenant=tenant, created_by=alice)
        response = admin_client.get(list_url, {"creator": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {s["id"] for s in response.data["results"]} == {str(john_status.pk)}

    def test_search_works(
            self, admin_client, list_url, tenant, task_status_factory, http_host
    ):
        abc_status = task_status_factory(name="abc", tenant=tenant)
        qwe_status = task_status_factory(name="qwe", tenant=tenant)

        response = admin_client.get(list_url, {"search": "ab"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {s["id"] for s in response.data["results"]} == {str(abc_status.pk)}

    def test_ordering_works(
            self, admin_client, list_url, tenant, task_status_factory, http_host
    ):
        a_status = task_status_factory(name="a", tenant=tenant)
        z_status = task_status_factory(name="z", tenant=tenant)

        response = admin_client.get(list_url, {"ordering": "name"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(a_status.pk), str(z_status.pk)]
        assert [s["id"] for s in response.data["results"]] == expected_ids


@pytest.mark.django_db
class TestTaskStatusRetrieveUpdateDestroyAPIView:

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
                ("get", status.HTTP_200_OK),
                ("put", status.HTTP_403_FORBIDDEN),
                ("patch", status.HTTP_403_FORBIDDEN),
                ("delete", status.HTTP_403_FORBIDDEN),
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
                tenant_owner,
                data,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_owner.user)
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
                content_type="application/json"
            )
            assert response.status_code == expected_status_code


    def test_get_404_if_task_status_does_not_belong_tenant(
            self, admin_client, detail_url, tenant_factory, done_task_status, http_host
    ):
        another_tenant = tenant_factory(sub_domain="lol")
        done_task_status.tenant = another_tenant
        done_task_status.save()

        response = admin_client.get(detail_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_perform_update(
            self, admin_client, detail_url, done_task_status, http_host, admin_user
    ):
        response = admin_client.patch(detail_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        done_task_status.refresh_from_db()
        assert done_task_status.updated_by == admin_user

