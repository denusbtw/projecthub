from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel, Tenant, TenantMembership
from .project_membership import ProjectMembership


class ProjectQuerySet(models.QuerySet):

    def annotate_role(self, user):
        role_subquery = ProjectMembership.objects.filter(
            project_id=OuterRef("pk"), user=user
        ).values("role")[:1]
        return self.annotate(role=Subquery(role_subquery))

    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

    def visible_to(self, user, tenant):
        if user.is_staff:
            return self

        tenant_membership = TenantMembership.objects.filter(
            tenant=tenant, user=user
        ).first()

        if tenant_membership and tenant_membership.is_owner:
            return self
        return self.filter(members__user=user)


class Project(UUIDModel, TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = ("active", _("Active"))
        PENDING = ("pending", _("Pending"))
        ARCHIVED = ("archived", _("Archived"))

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text=_("Tenant that owns this project."),
    )
    name = models.CharField(max_length=255, help_text=_("Name of project."))
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        blank=True,
        default=Status.ACTIVE,
        help_text=_("Status of project."),
    )
    description = models.CharField(
        max_length=5000, default="", blank=True, help_text=_("Description of project.")
    )
    start_date = models.DateField(
        null=True, blank=True, help_text=_("Start date of project (if any).")
    )
    end_date = models.DateField(
        null=True, blank=True, help_text=_("End date of project (if any).")
    )
    close_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            "Close date and time (if project was archived) and date and time previous close (is project is active)."
        ),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_projects",
        help_text=_("User who created project."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_projects",
        help_text=_("User who made the last change."),
    )

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(start_date__isnull=True)
                    | models.Q(end_date__isnull=True)
                    | models.Q(start_date__lte=models.F("end_date"))
                ),
                name="project_start_date_before_or_equal_to_end_date",
            )
        ]

    def __str__(self):
        status = self.get_status_display()
        return f"{self.name} ({status})"

    def activate(self, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        if not self.status == self.Status.ACTIVE:
            self.status = self.Status.ACTIVE
            self.updated_by = updated_by
            self.updated_at = timezone.now()
            self.save(update_fields=["status", "updated_by", "updated_at"])

    def mark_pending(self, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        if not self.status == self.Status.PENDING:
            self.status = self.Status.PENDING
            self.updated_by = updated_by
            self.updated_at = timezone.now()
            self.save(update_fields=["status", "updated_by", "updated_at"])

    def archive(self, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        if not self.status == self.Status.ARCHIVED:
            now = timezone.now()
            self.status = self.Status.ARCHIVED
            self.updated_by = updated_by
            self.updated_at = now
            self.close_date = now
            self.save(update_fields=["status", "updated_by", "updated_at"])

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_archived(self):
        return self.status == self.Status.ARCHIVED

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None
