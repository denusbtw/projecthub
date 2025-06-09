from django_filters import rest_framework as filters

from ...models import Project, ProjectMembership


class ProjectFilterSet(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=Project.Status.choices)
    start_date_after = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_before = filters.DateFilter(field_name="start_date", lookup_expr="lte")
    end_date_after = filters.DateFilter(field_name="end_date", lookup_expr="gte")
    end_date_before = filters.DateFilter(field_name="end_date", lookup_expr="lte")
    close_date_after = filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="gte"
    )
    close_date_before = filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="lte"
    )
    creator = filters.CharFilter(
        field_name="created_by__username", lookup_expr="icontains"
    )
    owner = filters.CharFilter(field_name="owner__username", lookup_expr="icontains")
    supervisor = filters.CharFilter(
        field_name="supervisor__username", lookup_expr="icontains"
    )
    responsible = filters.CharFilter(
        field_name="responsible__username", lookup_expr="icontains"
    )

    class Meta:
        model = Project
        fields = (
            "status",
            "start_date_after",
            "start_date_before",
            "end_date_after",
            "end_date_before",
            "close_date_after",
            "close_date_before",
            "creator",
            "owner",
            "supervisor",
            "responsible",
        )


class ProjectMembershipFilterSet(filters.FilterSet):
    role = filters.MultipleChoiceFilter(choices=ProjectMembership.Role.choices)
    creator = filters.CharFilter(
        field_name="created_by__username", lookup_expr="icontains"
    )

    class Meta:
        model = ProjectMembership
        fields = ("role", "creator")
