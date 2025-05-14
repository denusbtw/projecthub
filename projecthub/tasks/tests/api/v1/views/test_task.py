import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.tasks.models import Task


@pytest.fixture
def list_url(project):
    return reverse("api:v1:task_list", kwargs={"project_id": project.pk})


@pytest.fixture
def detail_url(task):
    return reverse(
        "api:v1:task_detail",
        kwargs={"project_id": task.project_id, "pk": task.pk}
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
        def test_project_reader(
                self,
                api_client,
                list_url,
                http_host,
                project_reader,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_reader.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
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
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_guest.user)
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
                project_user,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_user.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
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
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_responsible.user)
            data = {"name": "test task"}
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
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_supervisor.user)

            data = {"name": "test task"}
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
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=project_owner.user)
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
                tenant_owner,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_owner.user)
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
        def tasks(self, project, task_factory):
            return task_factory.create_batch(2, project=project)

        def test_staff_sees_all_tasks(
                self, admin_client, list_url, project, tasks, http_host
        ):
            response = admin_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_tenant_owner_sees_all_tasks(
                self, api_client, list_url, project, tasks, tenant_owner, http_host
        ):
            api_client.force_authenticate(tenant_owner.user)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_owner_sees_all_tasks(
                self, api_client, list_url, project, tasks, project_owner, http_host
        ):
            api_client.force_authenticate(project_owner.user)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_supervisor_sees_all_tasks(
                self, api_client, list_url, project, tasks, project_supervisor, http_host
        ):
            api_client.force_authenticate(project_supervisor.user)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_responsible_sees_all_tasks(
                self, api_client, list_url, project, tasks, project_responsible, http_host
        ):
            api_client.force_authenticate(project_responsible.user)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_project_user_sees_only_tasks_he_is_responsible_for(
                self, api_client, list_url, project, task_factory, project_user, http_host
        ):
            api_client.force_authenticate(project_user.user)

            t1 = task_factory(project=project, responsible=project_user.user)
            t2 = task_factory(project=project)

            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1
            assert {x["id"] for x in response.data["results"]} == {str(t1.pk)}

        def test_project_guest_sees_none_tasks(
                self, api_client, list_url, project, task_factory, project_guest, http_host
        ):
            api_client.force_authenticate(project_guest.user)
            task_factory.create_batch(2, project=project)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 0

        def test_project_reader_sees_none_tasks(
                self, api_client, list_url, project, task_factory, project_reader, http_host
        ):
            api_client.force_authenticate(project_reader.user)
            task_factory.create_batch(2, project=project)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 0

    def test_pagination_works(
            self, admin_client, list_url, project, task_factory, http_host
    ):
        task_factory.create_batch(5, project=project)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(
            self, admin_client, list_url, admin_user, project, http_host
    ):
        data = {"name": "my task"}
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)

        assert response.status_code == status.HTTP_201_CREATED
        task = Task.objects.get(id=response.data["id"])
        assert task.project == project
        assert task.created_by == admin_user
        assert task.updated_by == admin_user


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
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_task_responsible(
                self, api_client, detail_url, http_host, task, method, expected_status_code
        ):
            api_client.force_authenticate(user=task.responsible)
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