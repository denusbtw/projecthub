import pytest

from projecthub.core.api.v1.serializers import (
    TenantMembershipUpdateSerializer,
    TenantMembershipListSerializer,
    TenantMembershipDetailSerializer,
)
from projecthub.core.models import TenantMembership


@pytest.mark.django_db
class TestTenantListSerializer:

    def test_role_is_correct(self, tenant_membership_factory):
        membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        serializer = TenantMembershipListSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestTenantDetailSerializer:

    def test_role_is_correct(self, tenant_membership_factory):
        membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        serializer = TenantMembershipDetailSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestTenantUpdateSerializer:

    def test_no_error_if_empty_data(self, tenant_membership):
        serializer = TenantMembershipUpdateSerializer(tenant_membership, data={})
        assert serializer.is_valid(), serializer.errors
