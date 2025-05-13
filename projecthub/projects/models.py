from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel, Tenant


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

    # TODO
    # def archive(self):
    #     self.status = Project.Status.ARCHIVED
    #     self.close_date = timezone.now()
    #     self.save()


class ProjectMembership(UUIDModel, TimestampedModel):
    class Role(models.TextChoices):
        OWNER = ("owner", _("Owner"))
        SUPERVISOR = ("supervisor", _("Supervisor"))
        RESPONSIBLE = ("responsible", _("Responsible"))
        USER = ("user", _("User"))
        GUEST = ("guest", _("Guest"))
        READER = ("reader", _("Reader"))

    SINGLE_USER_ROLES = {Role.OWNER, Role.SUPERVISOR, Role.RESPONSIBLE}

    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="members",
        help_text=_("Project that owns this member."),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text=_("User that is member of project."),
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        blank=True,
        help_text=_("Role of user in project."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_project_memberships",
        help_text=_("User who created project membership."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_project_memberships",
        help_text=_("User who made the last change."),
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_project_user_membership"
            )
        ]

    def __str__(self):
        role = self.get_role_display()
        return f"{self.user.username} ({role}) in {self.project.name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        # TODO: винести у функцію-валідатор
        if self.role in self.SINGLE_USER_ROLES:
            qs = ProjectMembership.objects.filter(
                project_id=self.project_id, role=self.role
            )
            qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {"role": "Project already has a user with role '{value}'."}
                )
