from datetime import datetime

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from projecthub.core.models import TenantMembership


@pytest.fixture
def list_url():
    return reverse("api:v1:tenant_membership_list")


@pytest.fixture
def detail_url(tenant_membership):
    return reverse(
        "api:v1:tenant_membership_detail",
        kwargs={"pk": tenant_membership.pk}
    )


@pytest.fixture
def data(user_factory):
    return {"user": user_factory().pk, "role": TenantMembership.Role.USER}


@pytest.mark.django_db
class TestTenantMembershipListCreateAPIView:

    class TestPermissions:

        @pytest.mark.parametrize(
            "method, expected_status_code", [
                ("get", status.HTTP_403_FORBIDDEN),
                ("post", status.HTTP_403_FORBIDDEN)
            ],
        )
        def test_anonymous_user(
                self, api_client, list_url, http_host, method, expected_status_code
        ):
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code", [
                ("get", status.HTTP_404_NOT_FOUND),
                ("post", status.HTTP_404_NOT_FOUND)
            ],
        )
        def test_not_tenant_user(
                self, api_client, list_url, http_host, user, method, expected_status_code
        ):
            api_client.force_authenticate(user=user)
            response = getattr(api_client, method)(list_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code", [
                ("get", status.HTTP_200_OK),
                ("post", status.HTTP_403_FORBIDDEN)
            ],
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
            "method, expected_status_code", [
                ("get", status.HTTP_200_OK),
                ("post", status.HTTP_201_CREATED)
            ],
        )
        def test_tenant_owner(
                self,
                api_client,
                list_url,
                http_host,
                data,
                tenant_owner,
                method,
                expected_status_code,
        ):
            api_client.force_authenticate(user=tenant_owner.user)
            response = getattr(api_client, method)(
                list_url, data=data, HTTP_HOST=http_host
            )
            assert response.status_code == expected_status_code

        @pytest.mark.parametrize(
            "method, expected_status_code", [
                ("get", status.HTTP_200_OK),
                ("post", status.HTTP_201_CREATED)
            ],
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

        def test_returns_only_members_of_tenant_specified_in_sub_domain(
                self, admin_client, list_url, http_host, tenant, tenant_membership_factory
        ):
            tenant_membership_factory(tenant=tenant)
            tenant_membership_factory()

            response = admin_client.get(list_url, HTTP_HOST=http_host)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1

    def test_pagination_works(
            self, admin_client, list_url, http_host, tenant, tenant_membership_factory
    ):
        tenant_membership_factory.create_batch(5, tenant=tenant)
        response = admin_client.get(f"{list_url}?page_size=3", HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filtering_works(
            self,
            admin_client,
            list_url,
            tenant,
            tenant_membership_factory,
            john,
            alice,
            http_host
    ):
        john_membership = tenant_membership_factory(tenant=tenant, created_by=john)
        alice_membership = tenant_membership_factory(tenant=tenant, created_by=alice)
        response = admin_client.get(list_url, {"creator": "john"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {m["id"] for m in response.data["results"]} == {str(john_membership.pk)}

    def test_search_works(
            self,
            admin_client,
            list_url,
            tenant,
            tenant_membership_factory,
            john,
            alice,
            http_host
    ):
        john_membership = tenant_membership_factory(tenant=tenant, user=john)
        alice_membership = tenant_membership_factory(tenant=tenant, user=alice)

        response = admin_client.get(list_url, {"search": "jo"}, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        assert {m["id"] for m in response.data["results"]} == {str(john_membership.pk)}

    def test_ordering_works(
            self, admin_client, list_url, tenant, tenant_membership_factory, http_host
    ):
        old_membership = tenant_membership_factory(
            created_at=timezone.make_aware(datetime(2000, 1, 1)),
            tenant=tenant
        )
        new_membership = tenant_membership_factory(
            created_at=timezone.make_aware(datetime(2002, 1, 1)),
            tenant=tenant
        )

        query_params = {"ordering": "created_at"}
        response = admin_client.get(list_url, query_params, HTTP_HOST=http_host)
        assert response.status_code == status.HTTP_200_OK
        expected_ids = [str(old_membership.pk), str(new_membership.pk)]
        assert [m["id"] for m in response.data["results"]] == expected_ids


@pytest.mark.django_db
class TestTenantMembershipRetrieveUpdateDestroyAPIView:

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
                self, api_client, detail_url, http_host, user_factory, method, expected_status_code
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
                expected_status_code
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
                ("delete", status.HTTP_204_NO_CONTENT),
            ],
        )
        def test_self(
                self,
                api_client,
                detail_url,
                http_host,
                tenant_membership,
                method,
                expected_status_code
        ):
            tenant_membership.role = TenantMembership.Role.USER
            tenant_membership.save()
            api_client.force_authenticate(user=tenant_membership.user)
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
                expected_status_code
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
                self, admin_client, detail_url, http_host, method, expected_status_code
        ):
            response = getattr(admin_client, method)(detail_url, HTTP_HOST=http_host)
            assert response.status_code == expected_status_code

    def test_perform_update(
            self, admin_client, detail_url, admin_user, http_host, tenant_membership
    ):
        response = admin_client.patch(detail_url, HTTP_HOST=http_host)
        tenant_membership.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert tenant_membership.updated_by == admin_user