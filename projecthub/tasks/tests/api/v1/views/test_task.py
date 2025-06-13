import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.tasks.models import Task


@pytest.fixture
def list_url(active_project):
    return reverse("api:v1:task_list", kwargs={"project_id": active_project.pk})


@pytest.fixture
def detail_url(task):
    return reverse(
        "api:v1:task_detail", kwargs={"project_id": task.project_id, "pk": task.pk}
    )


@pytest.mark.django_db
class TestTaskListCreateAPIView:

    class TestPermissions:

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_403_FORBIDDEN), ("post", status.HTTP_403_FORBIDDEN)],
        )
        def test_anonymous(
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
        def test_project_user(
            self,
            api_client,
            list_url,
            http_host,
            active_project_user,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project_user.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("post", status.HTTP_201_CREATED),
            ],
        )
        def test_project_supervisor(
            self,
            api_client,
            list_url,
            http_host,
            active_project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.supervisor)

            data = {"name": "test task"}
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_200_OK),
                ("post", status.HTTP_201_CREATED),
            ],
        )
        def test_project_owner(
            self,
            api_client,
            list_url,
            http_host,
            active_project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.owner)
            data = {"name": "test task"}
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
            tenant,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=tenant.owner)
            data = {"name": "test task"}
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [("get", status.HTTP_200_OK), ("post", status.HTTP_201_CREATED)],
        )
        def test_admin(
            self, admin_client, list_url, http_host, method, expected_status_code
        ):
            data = {"name": "test task"}
            response = getattr(admin_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

    class TestQueryset:

        @pytest.fixture
        def tasks(self, active_project, task_factory):
            return task_factory.create_batch(2, project=active_project)

        def test_staff_sees_all_tasks(self, admin_client, list_url, tasks, http_host):
            response = admin_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_tenant_owner_sees_all_tasks(
            self, api_client, list_url, tasks, tenant, http_host
        ):
            api_client.force_authenticate(tenant.owner)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_owner_sees_all_tasks(
            self, api_client, list_url, active_project, tasks, http_host
        ):
            api_client.force_authenticate(active_project.owner)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_supervisor_sees_all_tasks(
            self, api_client, list_url, active_project, tasks, http_host
        ):
            api_client.force_authenticate(active_project.supervisor)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_user_sees_only_tasks_he_is_responsible_for(
            self,
            api_client,
            list_url,
            active_project,
            task_factory,
            active_project_user,
            http_host,
        ):
            api_client.force_authenticate(active_project_user.user)

            t1 = task_factory(
                project=active_project, responsible=active_project_user.user
            )
            t2 = task_factory(project=active_project)

            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1
            assert {x["id"] for x in response.data["results"]} == {str(t1.pk)}

    def test_pagination_works(
        self, admin_client, list_url, active_project, task_factory, http_host
    ):
        task_factory.create_batch(5, project=active_project)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(
        self, admin_client, list_url, admin_user, active_project, http_host
    ):
        data = {"name": "my task"}
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)

        assert response.status_code == status.HTTP_201_CREATED
        task = Task.objects.get(id=response.data["id"])
        assert task.project == active_project
        assert task.created_by == admin_user
        assert task.updated_by == admin_user

    def test_filtering_works(
        self,
        admin_client,
        list_url,
        active_project,
        task_factory,
        john,
        alice,
        http_host,
    ):
        john_task = task_factory(project=active_project, created_by=john)
        alice_task = task_factory(project=active_project, created_by=alice)
        response = admin_client.get(list_url, {"creator": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {t["id"] for t in response.data["results"]} == {str(john_task.pk)}

    def test_search_works(
        self, admin_client, list_url, active_project, task_factory, http_host
    ):
        abc_task = task_factory(name="abc", project=active_project)
        qwe_task = task_factory(name="qwe", project=active_project)

        response = admin_client.get(list_url, {"search": "ab"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {t["id"] for t in response.data["results"]} == {str(abc_task.pk)}

    def test_ordering_works(
        self, admin_client, list_url, active_project, task_factory, http_host
    ):
        a_task = task_factory(name="a", project=active_project)
        z_task = task_factory(name="z", project=active_project)

        response = admin_client.get(list_url, {"ordering": "name"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(a_task.pk), str(z_task.pk)]
        assert [t["id"] for t in response.data["results"]] == expected_ids


@pytest.mark.django_db
class TestTaskRetrieveUpdateDestroyAPIView:

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
        def test_anonymous(
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
            self, api_client, detail_url, http_host, user, method, expected_status_code
        ):
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
                ("get", status.HTTP_404_NOT_FOUND),
                ("put", status.HTTP_404_NOT_FOUND),
                ("patch", status.HTTP_404_NOT_FOUND),
                ("delete", status.HTTP_404_NOT_FOUND),
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
                ("get", status.HTTP_404_NOT_FOUND),
                ("put", status.HTTP_404_NOT_FOUND),
                ("patch", status.HTTP_404_NOT_FOUND),
                ("delete", status.HTTP_404_NOT_FOUND),
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
                ("get", status.HTTP_404_NOT_FOUND),
                ("put", status.HTTP_404_NOT_FOUND),
                ("patch", status.HTTP_404_NOT_FOUND),
                ("delete", status.HTTP_404_NOT_FOUND),
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
        def test_project_supervisor(
            self,
            api_client,
            detail_url,
            http_host,
            active_project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.supervisor)
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
            active_project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=active_project.owner)
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
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=tenant.owner)
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
        def test_admin(
            self,
            admin_client,
            detail_url,
            http_host,
            method,
            expected_status_code,
        ):
            response = getattr(admin_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

    def test_perform_update(
        self, admin_client, detail_url, task, admin_user, http_host
    ):
        response = admin_client.patch(detail_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.updated_by == admin_user

    def test_uses_task_responsible_update_serializer_if_user_is_task_responsible(
        self, api_client, detail_url, board_factory, task, user, http_host
    ):
        api_client.force_authenticate(user=task.responsible)

        board = board_factory(project=task.project)
        data = {"board": board.pk}
        response = api_client.put(detail_url, data=data, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK

        # expected serializer has only one attribute 'board'
        assert set(response.data.keys()) == {"board"}
