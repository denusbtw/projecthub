import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.comments.models import Comment
from projecthub.projects.models import ProjectMembership


@pytest.fixture
def list_url(task):
    return reverse("api:v1:comment_list", kwargs={"task_id": task.pk})


@pytest.fixture
def detail_url(comment):
    return reverse(
        "api:v1:comment_detail",
        kwargs={"task_id": comment.task_id, "pk": comment.pk}
    )


@pytest.fixture
def data():
    return {"body": "this is comment"}


@pytest.mark.django_db
class TestCommentListCreateAPIView:

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
            [("get", status.HTTP_404_NOT_FOUND), ("post", status.HTTP_404_NOT_FOUND)],
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
            [("get", status.HTTP_404_NOT_FOUND), ("post", status.HTTP_404_NOT_FOUND)],
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
            [("get", status.HTTP_404_NOT_FOUND), ("post", status.HTTP_404_NOT_FOUND)],
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
        def test_task_responsible(
                self,
                api_client,
                list_url,
                http_host,
                task,
                data,
                method,
                expected_status_code
        ):
            api_client.force_authenticate(user=task.responsible)
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
                self,
                admin_client,
                list_url,
                http_host,
                data,
                method,
                expected_status_code
        ):
            response = getattr(admin_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

    def test_pagination_works(
            self, admin_client, list_url, task, http_host, comment_factory
    ):
        comment_factory.create_batch(5, task=task)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_lists_comments_of_specific_task(
            self,
            admin_client,
            list_url,
            project,
            http_host,
            task,
            task_factory,
            comment_factory,
    ):
        comment_factory.create_batch(2, task=task)

        another_task = task_factory(project=project)
        comment_factory.create_batch(5, task=another_task)

        response = admin_client.get(list_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_perform_create(
            self, admin_client, list_url, task, data, http_host, admin_user
    ):
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_201_CREATED
        comment = Comment.objects.get(id=response.data["id"])
        assert comment.task == task
        assert comment.created_by == admin_user

    def test_filtering_works(
            self,
            admin_client,
            list_url,
            task,
            comment_factory,
            john,
            alice,
            http_host
    ):
        john_comment = comment_factory(task=task, created_by=john)
        alice_comment = comment_factory(task=task, created_by=alice)
        response = admin_client.get(list_url, {"author": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {c["id"] for c in response.data["results"]} == {str(john_comment.pk)}


@pytest.mark.django_db
class TestCommentDestroyAPIView:

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
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_task_responsible(
                self,
                api_client,
                detail_url,
                http_host,
                task,
                user_factory,
                method,
                expected_status_code
        ):
            task.responsible = user_factory()
            task.save()
            api_client.force_authenticate(user=task.responsible)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("delete", status.HTTP_403_FORBIDDEN),
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
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("delete", status.HTTP_403_FORBIDDEN),
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
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
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
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
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
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_admin(
                self, admin_client, detail_url, http_host, method, expected_status_code
        ):
            response = getattr(admin_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code",
            [
                ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_comment_author(
                self,
                api_client,
                detail_url,
                http_host,
                comment,
                task,
                project_membership_factory,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=comment.created_by)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code
