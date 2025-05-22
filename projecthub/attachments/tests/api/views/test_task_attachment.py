import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.attachments.models import TaskAttachment
from projecthub.conftest import file


@pytest.fixture
def list_url(task):
    return reverse(
        "api:v1:task_attachment_list",
        kwargs={"task_id": task.pk}
    )


@pytest.fixture
def detail_url(task_attachment):
    return reverse(
        "api:v1:task_attachment_detail",
        kwargs={
            "task_id": task_attachment.task_id,
            "pk": task_attachment.pk
        }
    )


@pytest.fixture
def data(file):
    return {"file": file}


@pytest.mark.django_db
class TestTaskAttachmentListCreateAPIView:

    def test_pagination_works(self, admin_client, list_url, task,
                              task_attachment_factory, http_host):
        task_attachment_factory.create_batch(5, task=task)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    class TestPermissions:

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_403_FORBIDDEN),
            ("post", status.HTTP_403_FORBIDDEN)
        ])
        def test_anonymous_user(self, api_client, list_url, http_host, method,
                                expected_status_code):
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("post", status.HTTP_404_NOT_FOUND)
        ])
        def test_not_tenant_member(self, api_client, list_url, http_host, user_factory,
                                   method, expected_status_code):
            api_client.force_authenticate(user=user_factory())
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("post", status.HTTP_404_NOT_FOUND)
        ])
        def test_tenant_user_not_project_member(self, api_client, list_url,
                                                http_host, tenant_user, method,
                                                expected_status_code):
            api_client.force_authenticate(user=tenant_user.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("post", status.HTTP_404_NOT_FOUND)
        ])
        def test_project_reader(self, api_client, list_url, http_host,
                                project_reader, method, expected_status_code):
            api_client.force_authenticate(user=project_reader.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("post", status.HTTP_404_NOT_FOUND)
        ])
        def test_project_guest(self, api_client, list_url, http_host,
                               project_guest, method, expected_status_code):
            api_client.force_authenticate(user=project_guest.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("post", status.HTTP_404_NOT_FOUND)
        ])
        def test_project_user_not_task_responsible(self, api_client, list_url,
                                                   http_host, project_user,
                                                   method, expected_status_code):
            api_client.force_authenticate(user=project_user.user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_task_responsible(self, api_client, list_url, http_host, task, data,
                                  method, expected_status_code):
            api_client.force_authenticate(user=task.responsible)
            response = getattr(api_client, method)(
                list_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_project_responsible(self, api_client, list_url, http_host,
                                     project_responsible, data, method,
                                     expected_status_code):
            api_client.force_authenticate(user=project_responsible.user)
            response = getattr(api_client, method)(
                list_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_project_supervisor(self, api_client, list_url, http_host,
                                    project_supervisor, data, method,
                                    expected_status_code):
            api_client.force_authenticate(user=project_supervisor.user)
            response = getattr(api_client, method)(
                list_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_project_owner(self, api_client, list_url, http_host,
                               project_owner, data, method,
                               expected_status_code):
            api_client.force_authenticate(user=project_owner.user)
            response = getattr(api_client, method)(
                list_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_tenant_owner(self, api_client, list_url, http_host,
                              tenant_owner, data, method,
                              expected_status_code):
            api_client.force_authenticate(user=tenant_owner.user)
            response = getattr(api_client, method)(
                list_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_admin(self, admin_client, list_url, http_host, data, method,
                       expected_status_code):
            response = getattr(admin_client, method)(
                list_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

    def test_perform_create(self, admin_client, list_url, task,
                            admin_user, data, http_host):
        response = admin_client.post(
            list_url, data=data, format="multipart", HTTP_HOST=http_host
        )
        attachment_id = response.data["id"]
        attachment = TaskAttachment.objects.get(id=attachment_id)
        assert attachment.task == task
        assert attachment.uploaded_by == admin_user


@pytest.mark.django_db
class TestTaskAttachmentRetrieveDestroyAPIView:

    class TestPermissions:
        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_403_FORBIDDEN),
            ("put", status.HTTP_403_FORBIDDEN),
            ("patch", status.HTTP_403_FORBIDDEN),
            ("delete", status.HTTP_403_FORBIDDEN)
        ])
        def test_anonymous_user(self, api_client, detail_url, http_host, method,
                                expected_status_code):
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("put", status.HTTP_404_NOT_FOUND),
            ("patch", status.HTTP_404_NOT_FOUND),
            ("delete", status.HTTP_404_NOT_FOUND)
        ])
        def test_not_tenant_member(self, api_client, detail_url, http_host, user_factory,
                                   method, expected_status_code):
            api_client.force_authenticate(user=user_factory())
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("put", status.HTTP_404_NOT_FOUND),
            ("patch", status.HTTP_404_NOT_FOUND),
            ("delete", status.HTTP_404_NOT_FOUND)
        ])
        def test_tenant_user_not_project_member(self, api_client, detail_url,
                                                http_host, tenant_user, method,
                                                expected_status_code):
            api_client.force_authenticate(user=tenant_user.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("put", status.HTTP_404_NOT_FOUND),
            ("patch", status.HTTP_404_NOT_FOUND),
            ("delete", status.HTTP_404_NOT_FOUND)
        ])
        def test_project_reader(self, api_client, detail_url, http_host,
                                project_reader, method, expected_status_code):
            api_client.force_authenticate(user=project_reader.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("put", status.HTTP_404_NOT_FOUND),
            ("patch", status.HTTP_404_NOT_FOUND),
            ("delete", status.HTTP_404_NOT_FOUND)
        ])
        def test_project_guest(self, api_client, detail_url, http_host,
                               project_guest, method, expected_status_code):
            api_client.force_authenticate(user=project_guest.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_404_NOT_FOUND),
            ("put", status.HTTP_404_NOT_FOUND),
            ("patch", status.HTTP_404_NOT_FOUND),
            ("delete", status.HTTP_404_NOT_FOUND)
        ])
        def test_project_user_not_task_responsible(self, api_client, detail_url,
                                                   http_host, project_user,
                                                   method, expected_status_code):
            api_client.force_authenticate(user=project_user.user)
            response = getattr(api_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_403_FORBIDDEN)
        ])
        def test_task_responsible(self, api_client, detail_url, http_host, task, data,
                                  method, expected_status_code):
            api_client.force_authenticate(user=task.responsible)
            response = getattr(api_client, method)(
                detail_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_403_FORBIDDEN)
        ])
        def test_project_responsible(self, api_client, detail_url, http_host,
                                     project_responsible, data, method,
                                     expected_status_code):
            api_client.force_authenticate(user=project_responsible.user)
            response = getattr(api_client, method)(
                detail_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_403_FORBIDDEN)
        ])
        def test_project_supervisor(self, api_client, detail_url, http_host,
                                    project_supervisor, data, method,
                                    expected_status_code):
            api_client.force_authenticate(user=project_supervisor.user)
            response = getattr(api_client, method)(
                detail_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_204_NO_CONTENT)
        ])
        def test_project_owner(self, api_client, detail_url, http_host,
                               project_owner, data, method,
                               expected_status_code):
            api_client.force_authenticate(user=project_owner.user)
            response = getattr(api_client, method)(
                detail_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_204_NO_CONTENT)
        ])
        def test_tenant_owner(self, api_client, detail_url, http_host,
                              tenant_owner, data, method,
                              expected_status_code):
            api_client.force_authenticate(user=tenant_owner.user)
            response = getattr(api_client, method)(
                detail_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_204_NO_CONTENT)
        ])
        def test_admin(self, admin_client, detail_url, http_host, data, method,
                       expected_status_code):
            response = getattr(admin_client, method)(
                detail_url, data=data, format="multipart", HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code