from django.forms import CharField
from django_filters import rest_framework as filters

from projecthub.core.filters import MultipleValueFilter
from ...models import Task


class TaskFilterSet(filters.FilterSet):
    status = MultipleValueFilter(field_name="status__name", field_class=CharField)
    priority = filters.NumberFilter()
    priority_min = filters.NumberFilter(field_name="priority", lookup_expr="gte")
    priority_max = filters.NumberFilter(field_name="priority", lookup_expr="lte")
    responsible = filters.CharFilter(
        field_name="responsible__username", lookup_expr="icontains"
    )
    creator = filters.CharFilter(
        field_name="created_by__username", lookup_expr="icontains"
    )
    start_date_after = filters.IsoDateTimeFilter(
        field_name="start_date", lookup_expr="gte"
    )
    start_date_before = filters.IsoDateTimeFilter(
        field_name="start_date", lookup_expr="lte"
    )
    end_date_after = filters.IsoDateTimeFilter(field_name="end_date", lookup_expr="gte")
    end_date_before = filters.IsoDateTimeFilter(
        field_name="end_date", lookup_expr="lte"
    )
    close_date_after = filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="gte"
    )
    close_date_before = filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="lte"
    )

    class Meta:
        model = Task
        fields = (
            "status",
            "priority",
            "responsible",
            "creator",
            "start_date_after",
            "start_date_before",
            "end_date_after",
            "end_date_before",
            "close_date_after",
            "close_date_before",
        )
