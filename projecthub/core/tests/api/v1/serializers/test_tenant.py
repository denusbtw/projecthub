import pytest

from projecthub.core.api.v1.serializers import (
    TenantCreateSerializer,
    TenantListSerializer,
    TenantUpdateSerializer,
    TenantDetailSerializer,
)
from projecthub.core.models import TenantMembership


@pytest.fixture
def data():
    return {"name": "my tenant", "sub_domain": "my_tenant"}


@pytest.mark.django_db
class TestTenantDetailSerializer:

    def test_owner_is_nested_serializer(self, tenant, tenant_membership_factory):
        owner_membership = tenant_membership_factory(
            tenant=tenant, role=TenantMembership.Role.OWNER
        )
        tenant.role = ""
        serializer = TenantDetailSerializer(tenant)
        assert serializer.data["owner"]["id"] == str(owner_membership.id)

    def test_owner_is_none_if_tenant_does_not_have_owner(self, tenant):
        tenant.role = ""
        serializer = TenantDetailSerializer(tenant)
        assert serializer.data["owner"] is None


@pytest.mark.django_db
class TestTenantCreateSerializer:

    def test_to_representation_matches_list_serializer_representation(self, user, data):
        serializer = TenantCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        tenant = serializer.save()
        assert serializer.data == TenantListSerializer(tenant).data

    def test_to_representation_annotates_owner_role(self, user, data, rf):
        request = rf.get("/")
        request.user = user

        context = {"request": request}
        serializer = TenantCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        assert serializer.data["role"] == TenantMembership.Role.OWNER


@pytest.mark.django_db
class TestTenantUpdateSerializer:

    def test_no_error_if_empty_data(self, tenant):
        serializer = TenantUpdateSerializer(tenant, data={})
        assert serializer.is_valid(), serializer.errors
