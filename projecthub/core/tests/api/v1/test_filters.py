import pytest

from projecthub.core.api.v1.filters import TenantFilterSet, TenantMembershipFilterSet
from projecthub.core.models import Tenant, TenantMembership


@pytest.mark.django_db
class TestTenantFilterSet:

    def test_by_creator_username(self, tenant_factory, john, alice):
        john_tenant = tenant_factory(created_by=john)
        alice_tenant = tenant_factory(created_by=alice)

        queryset = Tenant.objects.all()
        filtered = TenantFilterSet({"creator": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_tenant.pk

    def test_by_owner_username(
        self, tenant_factory, tenant_membership_factory, john, alice
    ):
        john_tenant = tenant_factory(owner=john)
        alice_tenant = tenant_factory(owner=alice)

        queryset = Tenant.objects.all()
        filtered = TenantFilterSet({"owner": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_tenant.pk

    def test_by_user_username(
        self, tenant_factory, tenant_membership_factory, john, alice
    ):
        john_tenant = tenant_factory()
        alice_tenant = tenant_factory()
        tenant_membership_factory(
            tenant=john_tenant, user=john, role=TenantMembership.Role.USER
        )

        queryset = Tenant.objects.all()
        filtered = TenantFilterSet({"user": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_tenant.pk


@pytest.mark.django_db
class TestTenantMembershipFilterSet:

    def test_filter_by_role(self, tenant_membership_factory):
        user_membership = tenant_membership_factory(role=TenantMembership.Role.USER)

        queryset = TenantMembership.objects.all()
        data = {"role": [TenantMembership.Role.USER]}
        filtered = TenantMembershipFilterSet(data, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == user_membership.pk

    def test_filter_by_creator_username(self, tenant_membership_factory, john, alice):
        john_membership = tenant_membership_factory(created_by=john)
        alice_membership = tenant_membership_factory(created_by=alice)

        queryset = TenantMembership.objects.all()
        filtered = TenantMembershipFilterSet({"creator": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_membership.pk
