import textwrap

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models.base import UUIDModel, TimestampedModel
from projecthub.tasks.models import Task


class CommentQuerySet(models.QuerySet):

    def for_tenant(self, tenant):
        return self.filter(task__project__tenant=tenant)

    def for_task(self, task_id):
        return self.filter(task_id=task_id)


class Comment(UUIDModel, TimestampedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text=_("Task that owns this comment."),
    )
    parent = models.ForeignKey(
        "Comment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        help_text=_("Parent comment."),
    )
    body = models.CharField(max_length=2000, help_text=_("Body of comment."))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        related_name="created_comments",
        help_text=_("Author of comment"),
    )

    #TODO:
    # add search vector: `search_vector = SearchVectorField(null=True)`
    # create index for it `GinIndex(fields=["search_vector"]`
    # override save method: `self.search_vector = SearchVector("body")
    # in views:
    # def get_queryset(self):
    #   queryset = super().get_queryset()
    #   query = self.request.query_params.get('search')
    #   if query:
    #       search_query = SearchQuery(query)
    #       queryset = queryset.annotate(
    #           rank=SearchRank(F('search_vector'), search_query)
    #       ).filter(search_vector=search_query).order_by('-rank')
    #   return queryset

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(parent_id=models.F("id")),
                name="prevent_self_parent",
            )
        ]

    def __str__(self):
        body = textwrap.shorten(self.body, 20)
        return f"{self.created_by.username}: {body} in {self.task.name}"

    @property
    def is_reply(self):
        return self.parent is not None
