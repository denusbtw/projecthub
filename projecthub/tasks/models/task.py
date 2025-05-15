from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel, TenantMembership
from projecthub.projects.models import ProjectMembership, Project
from .task_status import TaskStatus


class TaskQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(project__tenant=tenant)

    def for_project(self, project_id):
        return self.filter(project_id=project_id)

    def for_responsible(self, user):
        return self.filter(responsible=user)

    def visible_to(self, user, tenant, project_id):
        if user.is_staff:
            return self

        tenant_membership = TenantMembership.objects.filter(
            tenant=tenant, user=user
        ).first()
        if tenant_membership and tenant_membership.is_owner:
            return self

        project_membership = ProjectMembership.objects.filter(
            project_id=project_id, user=user
        ).first()
        if project_membership and project_membership.is_staff:
            return self

        if project_membership and project_membership.is_user:
            return self.for_responsible(user)

        return self.none()


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

    objects = TaskQuerySet.as_manager()

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
