import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.core.models import Tenant


@pytest.fixture
def list_url():
    return reverse("api:v1:tenant_list")


@pytest.fixture
def detail_url(tenant):
    return reverse("api:v1:tenant_detail", kwargs={"pk": tenant.pk})


@pytest.fixture
def data():
    return {"name": "my tenant", "sub_domain": "my_tenant"}


@pytest.mark.django_db
class TestTenantListCreateAPIView:

    class TestPermissions:

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_403_FORBIDDEN),
            ("post", status.HTTP_403_FORBIDDEN)
        ])
        def test_anonymous_user(self, api_client, list_url, method, expected_status_code):
            response = getattr(api_client, method)(list_url)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize("method, expected_status_code", [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED)
        ])
        def test_authenticated_user(
                self, api_client, list_url, user, data, method, expected_status_code
        ):
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(list_url, data=data)
            assert response.status_code == expected_status_code

    class TestQueryset:

        def test_staff_sees_all_tenants(self, admin_client, list_url, tenant_factory):
            tenant_factory.create_batch(3)
            response = admin_client.get(list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 3

        def test_non_staff_sees_only_tenants_he_is_member_of(
                self, api_client, list_url, tenant_factory, tenant_membership_factory, user
        ):
            api_client.force_authenticate(user=user)
            t1 = tenant_factory()
            _ = tenant_factory()
            tenant_membership_factory(tenant=t1, user=user)

            response = api_client.get(list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1
            assert {t["id"] for t in response.data["results"]} == {str(t1.id)}

        def test_role_is_annotated_correctly(
                self, api_client, list_url, tenant_membership_factory
        ):
            membership = tenant_membership_factory()
            api_client.force_authenticate(user=membership.user)

            response = api_client.get(list_url)

            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1
            assert response.data["results"][0]["role"] == membership.role

    def test_pagination_works(self, admin_client, list_url, tenant_membership_factory):
        tenant_membership_factory.create_batch(5)
        response = admin_client.get(f"{list_url}?page_size=3")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_perform_create(self, admin_client, list_url, admin_user, data):
        response = admin_client.post(list_url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        tenant = Tenant.objects.get(id=response.data["id"])
        assert tenant.created_by == admin_user
        assert tenant.updated_by == admin_user

    def test_filtering_works(
            self, admin_client, list_url, tenant_factory, john, alice
    ):
        john_tenant = tenant_factory(created_by=john)
        alice_tenant = tenant_factory(created_by=alice)
        response = admin_client.get(list_url, {"creator": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert {t["id"] for t in response.data["results"]} == {str(john_tenant.pk)}

    def test_search_works(self, admin_client, list_url, tenant_factory):
        abc_tenant = tenant_factory(name="abc")
        qwe_tenant = tenant_factory(name="qwe")

        response = admin_client.get(list_url, {"search": "abc"})
        assert response.status_code == status.HTTP_200_OK
        assert {t["id"] for t in response.data["results"]} == {str(abc_tenant.pk)}

@pytest.mark.django_db
class TestTenantRetrieveUpdateDestroyAPIView:

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
                self, api_client, detail_url, method, expected_status_code
        ):
            response = getattr(api_client, method)(detail_url)
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
                self, api_client, detail_url, user, method, expected_status_code
        ):
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(detail_url)
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
                tenant_user,
                tenant,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_user.user)
            response = getattr(api_client, method)(detail_url)
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
                tenant_owner,
                tenant,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_owner.user)
            response = getattr(api_client, method)(detail_url)
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
                tenant,
                method,
                expected_status_code,
        ):
            response = getattr(admin_client, method)(detail_url)
            assert response.status_code == expected_status_code

    class TestQueryset:

        def test_role_is_annotated_correctly(
                self, api_client, tenant, detail_url, tenant_membership_factory
        ):
            membership = tenant_membership_factory(tenant=tenant)
            api_client.force_authenticate(user=membership.user)
            response = api_client.get(detail_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["role"] == membership.role

        def test_owner_field_serialized_correctly(
                self, admin_client, detail_url, tenant, tenant_owner
        ):
            response = admin_client.get(detail_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["owner"]["user"]["id"] == str(tenant_owner.user_id)

    def test_perform_update(self, admin_client, detail_url, tenant, admin_user):
        response = admin_client.patch(detail_url)
        assert response.status_code == status.HTTP_200_OK
        tenant.refresh_from_db()
        assert tenant.updated_by == admin_user