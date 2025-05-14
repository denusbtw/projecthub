from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel, Tenant
from projecthub.projects.models import Project


class Task(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=255, help_text=_("Name of task."))
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text=_("Project to which task belongs."),
    )
    status = models.ForeignKey(
        "TaskStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text=_("Status of task."),
    )
    priority = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0,
        blank=True,
        help_text=_("Priority of task."),
    )
    description = models.CharField(
        max_length=2000, default="", blank=True, help_text=_("Description of task.")
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_tasks",
        help_text=_("Responsible of task."),
    )
    start_date = models.DateTimeField(
        blank=True, null=True, help_text=_("Start date of task (if any).")
    )
    end_date = models.DateTimeField(
        blank=True, null=True, help_text=_("End date of task (if any).")
    )
    close_date = models.DateTimeField(
        blank=True, null=True, help_text=_("Close date of task.")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
        help_text=_("User who created task."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_tasks",
        help_text=_("User who made the last change."),
    )

    class Meta:
        ordering = ["priority"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(start_date__isnull=True)
                    | models.Q(end_date__isnull=True)
                    | models.Q(start_date__lte=models.F("end_date"))
                ),
                name="task_start_date_before_or_equal_to_end_date",
            )
        ]

    def __str__(self):
        status_name = getattr(self.status, "name", "No status")
        return f"{self.name} ({status_name}) in {self.project.name}"

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None

    def set_status(self, code: str, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        status = TaskStatus.objects.filter(
            tenant_id=self.project.tenant_id, code=code
        ).first()

        if not status:
            raise ValidationError(f"No status with code '{code}' found for tenant.")

        now = timezone.now()

        self.status = status
        self.updated_by = updated_by
        self.updated_at = now

        if status.is_done:
            self.close_date = now

        fields = ["status", "updated_by", "updated_at"]
        if status.is_done:
            fields.append("close_date")

        self.save(update_fields=fields)

    def revoke(self, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        self.status = None
        self.responsible = None
        self.updated_by = updated_by
        self.updated_at = timezone.now()
        self.save(update_fields=["status", "responsible", "updated_by", "updated_at"])

    @property
    def is_todo(self):
        return self.status and self.status.is_todo

    @property
    def is_done(self):
        return self.status and self.status.is_done

    @property
    def is_in_progress(self):
        return self.status and self.status.is_in_progress

    @property
    def is_in_review(self):
        return self.status and self.status.is_in_review


class TaskStatus(UUIDModel, TimestampedModel):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="task_statuses",
        help_text=_("Tenant that owns this task status."),
    )
    name = models.CharField(max_length=255, help_text=_("Name of task status."))
    code = models.CharField(max_length=50, unique=False, blank=True, default="")
    order = models.PositiveIntegerField(help_text=_("Order of task status."))
    is_default = models.BooleanField(
        default=False,
        help_text=_(
            "Determines whether task status is default (todo, done, in review, etc)."
        ),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_task_statuses",
        help_text=_("User who created task status."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_task_statuses",
        help_text=_("User who made the last change."),
    )

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "order"], name="unique_task_status_order_for_tenant"
            ),
            models.UniqueConstraint(
                fields=["tenant", "code"], name="unique_task_status_code_for_tenant"
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
