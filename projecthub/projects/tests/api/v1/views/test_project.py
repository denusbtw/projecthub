import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.projects.models import Project


@pytest.fixture
def list_url():
    return reverse("api:v1:project_list")


@pytest.fixture
def detail_url(project):
    return reverse("api:v1:project_detail", kwargs={"pk": project.pk})


@pytest.fixture
def data():
    return {"name": "test project"}


@pytest.mark.django_db
class TestProjectListCreateAPIView:

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

    class TestQueryset:

        @pytest.fixture
        def projects(self, project_factory, tenant):
            return project_factory.create_batch(2, tenant=tenant)

        def test_staff_sees_all_projects(
            self, admin_client, list_url, projects, http_host
        ):
            response = admin_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_tenant_owner_sees_all_projects(
            self, api_client, list_url, projects, tenant, http_host
        ):
            api_client.force_authenticate(user=tenant.owner)
            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 2

        def test_tenant_user_sees_only_projects_he_is_member_of(
            self,
            api_client,
            list_url,
            project_membership_factory,
            projects,
            tenant_user,
            http_host,
        ):
            api_client.force_authenticate(user=tenant_user.user)
            p1, p2 = projects

            project_membership_factory(project=p1, user=tenant_user.user)

            response = api_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1
            assert {x["id"] for x in response.data["results"]} == {str(p1.id)}

    def test_pagination_works(
        self, admin_client, list_url, project_factory, tenant, http_host
    ):
        project_factory.create_batch(5, tenant=tenant)
        response = admin_client.get(list_url, {"page_size": 3}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(
        self, admin_client, list_url, tenant, http_host, admin_user
    ):
        data = {"name": "todo project"}
        response = admin_client.post(list_url, data=data, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_201_CREATED
        project = Project.objects.get(id=response.data["id"])
        assert project.tenant == tenant
        assert project.created_by == admin_user
        assert project.updated_by == admin_user

    def test_filtering_works(
        self, admin_client, list_url, tenant, project_factory, john, alice, http_host
    ):
        john_project = project_factory(tenant=tenant, created_by=john)
        alice_project = project_factory(tenant=tenant, created_by=alice)
        response = admin_client.get(list_url, {"creator": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {p["id"] for p in response.data["results"]} == {str(john_project.pk)}

    def test_search_works(
        self, admin_client, list_url, tenant, project_factory, http_host
    ):
        abc_project = project_factory(tenant=tenant, name="abc")
        qwe_project = project_factory(tenant=tenant, name="qwe")
        response = admin_client.get(list_url, {"search": "ab"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {p["id"] for p in response.data["results"]} == {str(abc_project.pk)}

    def test_ordering_works(
        self, admin_client, list_url, tenant, project_factory, http_host
    ):
        a_project = project_factory(name="a", tenant=tenant)
        z_project = project_factory(name="z", tenant=tenant)

        response = admin_client.get(list_url, {"ordering": "name"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(a_project.pk), str(z_project.pk)]
        assert [p["id"] for p in response.data["results"]] == expected_ids


@pytest.mark.django_db
class TestProjectRetrieveUpdateDestroyAPIView:

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
            self, api_client, detail_url, user, http_host, method, expected_status_code
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
                ("put", status.HTTP_403_FORBIDDEN),
                ("patch", status.HTTP_403_FORBIDDEN),
                ("delete", status.HTTP_403_FORBIDDEN),
            ],
        )
        def test_project_responsible(
            self,
            api_client,
            detail_url,
            http_host,
            project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=project.responsible)
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
        def test_project_supervisor(
            self,
            api_client,
            detail_url,
            http_host,
            project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=project.supervisor)
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
            project,
            method,
            expected_status_code,
        ):
            api_client.force_authenticate(user=project.owner)
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
            self, admin_client, detail_url, http_host, method, expected_status_code
        ):
            response = getattr(admin_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

    def test_perform_update(
        self, admin_client, detail_url, http_host, admin_user, project
    ):
        response = admin_client.patch(detail_url, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.updated_by == admin_user
