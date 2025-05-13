from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import UUIDModel, TimestampedModel


class Tenant(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=255, help_text=_("Name of tenant."))
    sub_domain = models.CharField(
        max_length=255, unique=True, help_text=_("Subdomain of tenant.")
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Determines whether tenant is active.")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tenants",
        help_text=_("User who created tenant."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_tenants",
        help_text=_("User who made the last change."),
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.sub_domain})"


class TenantMembership(UUIDModel, TimestampedModel):
    class Role(models.TextChoices):
        OWNER = ("owner", _("Owner"))
        USER = ("user", _("User"))

    tenant = models.ForeignKey(
        "Tenant",
        on_delete=models.CASCADE,
        related_name="members",
        help_text=_("Tenant that owns this member."),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenants",
        help_text=_("User that is member of tenant."),
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        blank=True,
        help_text=_("Role of user in tenant."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tenant_memberships",
        help_text=_("User who created tenant membership."),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_tenant_memberships",
        help_text=_("User who made the last change."),
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user"], name="unique_tenant_user"
            )
        ]

    def __str__(self):
        role = self.get_role_display()
        return f"{self.user.username} ({role}) in {self.tenant.name}"
