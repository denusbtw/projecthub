import pytest
from rest_framework.exceptions import ValidationError

from projecthub.core.api.v1.serializers import (
    TenantCreateSerializer,
    TenantUpdateSerializer,
    TenantDetailSerializer,
)
from projecthub.core.models import Tenant


@pytest.fixture
def data():
    return {"name": "my tenant", "sub_domain": "my_tenant"}


@pytest.mark.django_db
class TestTenantDetailSerializer:

    def test_owner_is_nested_serializer(self, tenant):
        tenant.role = ""
        serializer = TenantDetailSerializer(tenant)
        assert serializer.data["owner"]["id"] == str(tenant.owner_id)


@pytest.mark.django_db
class TestTenantCreateSerializer:

    def test_error_if_empty_data(self):
        serializer = TenantCreateSerializer(data={})
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_creates_tenant(self, user):
        data = {"name": "test tenant", "sub_domain": "test-tenant"}
        serializer = TenantCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        serializer.save(owner=user)

        tenant_id = serializer.data["id"]
        tenant = Tenant.objects.get(pk=tenant_id)
        assert tenant.name == data["name"]
        assert tenant.sub_domain == data["sub_domain"]
        assert tenant.owner == user


@pytest.mark.django_db
class TestTenantUpdateSerializer:

    def test_no_error_if_empty_data(self, tenant):
        serializer = TenantUpdateSerializer(tenant, data={})
        assert serializer.is_valid(), serializer.errors
