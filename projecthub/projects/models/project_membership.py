from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel


class ProjectMembershipQuerySet(models.QuerySet):

    def for_tenant(self, tenant):
        return self.filter(project__tenant=tenant)

    def for_project(self, project_id):
        return self.filter(project_id=project_id)


class ProjectMembership(UUIDModel, TimestampedModel):
    class Role(models.TextChoices):
        USER = ("user", _("User"))
        GUEST = ("guest", _("Guest"))
        READER = ("reader", _("Reader"))

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

    objects = ProjectMembershipQuerySet.as_manager()

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

    @property
    def is_user(self):
        return self.role == self.Role.USER

    @property
    def is_guest(self):
        return self.role == self.Role.GUEST

    @property
    def is_reader(self):
        return self.role == self.Role.READER

    def set_role(self, role, updated_by):
        self.role = role
        self.updated_by = updated_by
        self.updated_at = timezone.now()
