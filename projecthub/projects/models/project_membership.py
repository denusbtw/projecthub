from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel


class ProjectMembershipQuerySet(models.QuerySet):

    def for_tenant(self, tenant):
        return self.filter(project__tenant=tenant)

    def for_project(self, project_id):
        return self.filter(project_id=project_id)


class ProjectMembership(UUIDModel, TimestampedModel):
    class Role(models.TextChoices):
        OWNER = ("owner", _("Owner"))
        SUPERVISOR = ("supervisor", _("Supervisor"))
        RESPONSIBLE = ("responsible", _("Responsible"))
        USER = ("user", _("User"))
        GUEST = ("guest", _("Guest"))
        READER = ("reader", _("Reader"))

    SINGLE_USER_ROLES = {Role.OWNER, Role.SUPERVISOR, Role.RESPONSIBLE}
    STAFF_USER_ROLES = {Role.OWNER, Role.SUPERVISOR, Role.RESPONSIBLE}

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

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_supervisor(self):
        return self.role == self.Role.SUPERVISOR

    @property
    def is_responsible(self):
        return self.role == self.Role.RESPONSIBLE

    @property
    def is_user(self):
        return self.role == self.Role.USER

    @property
    def is_guest(self):
        return self.role == self.Role.GUEST

    @property
    def is_reader(self):
        return self.role == self.Role.READER

    @property
    def is_staff(self):
        return self.role in self.STAFF_USER_ROLES
