from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel
from projecthub.projects.models import Project


class BoardQuerySet(models.QuerySet):

    def default_boards(self):
        return self.exclude(code=Board.Type.CUSTOM)

    def custom_boards(self):
        return self.filter(code=Board.Type.CUSTOM)

    def for_project(self, project):
        return self.filter(project=project)


BOARD_TYPE_TODO = "todo"
BOARD_TYPE_IN_PROGRESS = "in_progress"
BOARD_TYPE_IN_REVIEW = "in_review"
BOARD_TYPE_DONE = "done"
BOARD_TYPE_CUSTOM = "custom"


class Board(UUIDModel, TimestampedModel):
    class Type(models.TextChoices):
        TODO = BOARD_TYPE_TODO, _("To Do")
        IN_PROGRESS = BOARD_TYPE_IN_PROGRESS, _("In Progress")
        IN_REVIEW = BOARD_TYPE_IN_REVIEW, _("In Review")
        DONE = BOARD_TYPE_DONE, _("Done")
        CUSTOM = BOARD_TYPE_CUSTOM, _("Custom")

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="boards",
        help_text=_("Project that owns this board."),
    )
    name = models.CharField(max_length=255, help_text=_("Name of board."))
    type = models.CharField(max_length=50, choices=Type.choices, unique=False)
    order = models.PositiveIntegerField(help_text=_("Order of board."))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_boards",
        help_text=_("User who created board."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_boards",
        help_text=_("User who made the last change."),
    )

    objects = BoardQuerySet.as_manager()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "order"], name="unique_border_order_for_project"
            ),
            models.UniqueConstraint(
                fields=["project", "type"],
                name="unique_border_type_for_project",
                condition=models.Q(
                    type__in=[
                        BOARD_TYPE_TODO,
                        BOARD_TYPE_IN_PROGRESS,
                        BOARD_TYPE_IN_REVIEW,
                        BOARD_TYPE_DONE,
                    ]
                ),
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.order}) in {self.project.name}"

    def clean(self):
        if self.type != self.Type.CUSTOM:
            if (
                Board.objects.filter(project=self.project, type=self.type)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    f"Project already has a {self.get_type_display()} board."
                )

    @property
    def is_custom(self):
        return self.type == self.Type.CUSTOM

    @property
    def is_todo(self):
        return self.type == self.Type.TODO

    @property
    def is_in_progress(self):
        return self.type == self.Type.IN_PROGRESS

    @property
    def is_in_review(self):
        return self.type == self.Type.IN_REVIEW

    @property
    def is_done(self):
        return self.type == self.Type.DONE
