from django_filters import rest_framework as filters

from ...models import Comment


class CommentFilterSet(filters.FilterSet):
    parent = filters.NumberFilter(field_name="parent__id")
    author = filters.CharFilter(
        field_name="created_by__username", lookup_expr="icontains"
    )
    created_after = filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Comment
        fields = ("parent", "author", "created_after", "created_before")
