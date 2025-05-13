import pytest
from django.core.exceptions import ValidationError

from projecthub.core.models import TenantMembership


@pytest.mark.django_db
class TestTenant:

    def test_is_inactive_property(self, tenant_factory):
        active_tenant = tenant_factory(is_active=True)
        assert not active_tenant.is_inactive

        inactive_tenant = tenant_factory(is_active=False)
        assert inactive_tenant.is_inactive

    def test_activate_sets_active_and_updated_by(self, tenant_factory, user):
        tenant = tenant_factory(is_active=False)
        tenant.activate(updated_by=user)
        assert tenant.is_active
        assert tenant.updated_by == user

    def test_activate_raises_error_without_updated_by(self, tenant_factory):
        tenant = tenant_factory(is_active=False)
        with pytest.raises(ValueError, match="updated_by is required."):
            tenant.activate(updated_by=None)

    def test_deactivate_sets_inactivate_and_updated_by(self, tenant_factory, user):
        tenant = tenant_factory(is_active=True)
        tenant.deactivate(updated_by=user)
        assert not tenant.is_active
        assert tenant.updated_by == user

    def test_deactivate_raises_error_without_updated_by(self, tenant_factory):
        tenant = tenant_factory(is_active=True)
        with pytest.raises(ValueError, match="updated_by is required."):
            tenant.deactivate(updated_by=None)


@pytest.mark.django_db
class TestTenantMembership:

    def test_is_owner_property(self, tenant_membership_factory):
        owner_membership = tenant_membership_factory(role=TenantMembership.Role.OWNER)
        assert owner_membership.is_owner

        user_membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        assert not user_membership.is_owner

    def test_is_user_property(self, tenant_membership_factory):
        user_membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        assert user_membership.is_user

        owner_membership = tenant_membership_factory(role=TenantMembership.Role.OWNER)
        assert not owner_membership.is_user

    def test_raises_error_if_owner_exists_for_tenant(
        self, tenant, tenant_membership_factory, user_factory
    ):
        tenant_membership_factory(tenant=tenant, role=TenantMembership.Role.OWNER)

        second_user = user_factory()
        membership = TenantMembership(
            tenant=tenant, user=second_user, role=TenantMembership.Role.OWNER
        )

        with pytest.raises(
            ValidationError, match="Each tenant can have only one owner."
        ):
            membership.full_clean()

    def test_success_if_owner_does_not_exist_for_tenant(
        self, tenant_membership_factory
    ):
        membership = tenant_membership_factory(role=TenantMembership.Role.OWNER)
        membership.full_clean()
