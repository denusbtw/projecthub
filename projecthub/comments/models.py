import textwrap

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models.base import UUIDModel, TimestampedModel
from projecthub.tasks.models import Task


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
