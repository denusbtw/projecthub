from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel, Tenant


class BoardQuerySet(models.QuerySet):

    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)


class Board(UUIDModel, TimestampedModel):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="boards",
        help_text=_("Tenant that owns this board."),
    )
    name = models.CharField(max_length=255, help_text=_("Name of board."))
    code = models.CharField(max_length=50, unique=False, blank=True, default="")
    order = models.PositiveIntegerField(help_text=_("Order of board."))
    is_default = models.BooleanField(
        default=False,
        help_text=_(
            "Determines whether board is default (todo, done, in review, etc)."
        ),
    )
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
                fields=["tenant", "order"], name="unique_border_order_for_tenant"
            ),
            models.UniqueConstraint(
                fields=["tenant", "code"], name="unique_border_code_code_for_tenant"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.order}) in {self.tenant.name}"

    @property
    def is_todo(self):
        return self.code == "todo"

    @property
    def is_in_progress(self):
        return self.code == "in_progress"

    @property
    def is_in_review(self):
        return self.code == "in_review"

    @property
    def is_done(self):
        return self.code == "done"
