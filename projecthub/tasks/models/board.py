from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel
from projecthub.projects.models import Project


class BoardQuerySet(models.QuerySet):

    def for_project(self, project):
        return self.filter(project=project)


class Board(UUIDModel, TimestampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="boards",
        help_text=_("Project that owns this board."),
    )
    name = models.CharField(max_length=255, help_text=_("Name of board."))
    order = models.PositiveIntegerField(help_text=_("Order of board."))

    objects = BoardQuerySet.as_manager()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "order"], name="unique_border_order_for_project"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.order}) in {self.project.name}"
