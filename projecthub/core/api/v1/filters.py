from django_filters import rest_framework as filters

from ...models import Tenant, TenantMembership


class TenantFilterSet(filters.FilterSet):
    creator = filters.CharFilter(
        field_name="created_by__username", lookup_expr="icontains"
    )
    owner = filters.CharFilter(field_name="owner__username", lookup_expr="icontains")
    user = filters.CharFilter(method="filter_by_user")

    class Meta:
        model = Tenant
        fields = ("is_active", "creator", "owner", "user")

    def filter_by_user(self, queryset, name, value):
        return self._filter_by_role(queryset, value, TenantMembership.Role.USER)

    def _filter_by_role(self, queryset, value, role):
        return queryset.filter(
            members__user__username__icontains=value, members__role=role
        )


class TenantMembershipFilterSet(filters.FilterSet):
    role = filters.MultipleChoiceFilter(choices=TenantMembership.Role.choices)
    creator = filters.CharFilter(
        field_name="created_by__username", lookup_expr="icontains"
    )

    class Meta:
        model = TenantMembership
        fields = ("role", "creator")
