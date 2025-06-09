import pytest

from projecthub.core.models import TenantMembership, Tenant


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

    def test_is_user_property(self, tenant_membership_factory):
        user_membership = tenant_membership_factory(role=TenantMembership.Role.USER)
        assert user_membership.is_user


@pytest.mark.django_db
class TestTenantQuerySet:

    def test_annotate_role_none_if_not_member(self, user, tenant_factory):
        tenant = tenant_factory()
        qs = Tenant.objects.annotate_role(user)
        tenant = qs.get(pk=tenant.pk)
        assert tenant.role is None

    def test_annotate_role_not_none_if_member(
            self, user, tenant_factory, tenant_membership_factory
    ):
        tenant = tenant_factory()
        membership = tenant_membership_factory(tenant=tenant, user=user)
        qs = Tenant.objects.annotate_role(user)
        tenant = qs.get(pk=tenant.pk)
        assert tenant.role == membership.role

    def test_visible_to_returns_all_if_staff(self, admin_user, tenant_factory):
        tenant_factory.create_batch(3)
        qs = Tenant.objects.visible_to(admin_user)
        assert qs.count() == 3

    def test_visible_to_returns_only_tenants_user_is_member_of(
            self, user, tenant_factory, tenant_membership_factory
    ):
        tenant = tenant_factory()
        another_tenant = tenant_factory()
        tenant_membership_factory(tenant=tenant, user=user)
        qs = Tenant.objects.visible_to(user)
        assert qs.count() == 1
        assert set(qs.values_list("pk", flat=True)) == {tenant.pk}


@pytest.mark.django_db
class TestTenantMembershipQuerySet:

    def test_for_tenant(self, tenant_factory, tenant_membership_factory):
        tenant1 = tenant_factory()
        tenant2 = tenant_factory()
        tenant1_membership = tenant_membership_factory(tenant=tenant1)
        tenant2_membership = tenant_membership_factory(tenant=tenant2)
        qs = TenantMembership.objects.for_tenant(tenant1)
        assert qs.count() == 1
        assert set(qs.values_list("pk", flat=True)) == {tenant1_membership.pk}