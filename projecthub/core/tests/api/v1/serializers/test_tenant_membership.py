import pytest
from rest_framework.exceptions import ValidationError

from projecthub.core.api.v1.serializers import (
    TenantMembershipUpdateSerializer,
    TenantMembershipListSerializer,
    TenantMembershipDetailSerializer,
    TenantMembershipCreateSerializer,
)
from projecthub.core.models import TenantMembership


@pytest.mark.django_db
class TestTenantMembershipListSerializer:

    def test_role_is_correct(self, tenant_membership_factory):
        membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        serializer = TenantMembershipListSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestTenantMembershipDetailSerializer:

    def test_role_is_correct(self, tenant_membership_factory):
        membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        serializer = TenantMembershipDetailSerializer(membership)
        assert serializer.data["role"] == membership.get_role_display()


@pytest.mark.django_db
class TestTenantMembershipCreateSerializer:

    def test_error_if_user_is_tenant_owner(self, tenant):
        data = {"user": tenant.owner_id, "role": TenantMembership.Role.USER}
        context = {"tenant_owner_id": tenant.owner_id}
        serializer = TenantMembershipCreateSerializer(data=data, context=context)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "Tenant owner cannot be a member." in str(exc.value)

    def test_no_error_if_user_is_not_tenant_owner(self, tenant, user):
        data = {"user": user.pk, "role": TenantMembership.Role.USER}
        context = {"tenant_owner_id": tenant.owner_id}
        serializer = TenantMembershipCreateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestTenantMembershipUpdateSerializer:

    def test_no_error_if_empty_data(self, tenant_membership):
        serializer = TenantMembershipUpdateSerializer(tenant_membership, data={})
        assert serializer.is_valid(), serializer
