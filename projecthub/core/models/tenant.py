from django.conf import settings
from django.core.exceptions import ValidationError
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

    @property
    def is_inactive(self):
        return not self.is_active

    def activate(self, updated_by):
        if not updated_by:
            raise ValueError("updated_by is required.")

        if self.is_inactive:
            self.is_active = True
            self.updated_by = updated_by
            self.save(update_fields=["is_active", "updated_by"])

    def deactivate(self, updated_by):
        if not updated_by:
            raise ValueError("updated_by is required.")

        if self.is_active:
            self.is_active = False
            self.updated_by = updated_by
            self.save(update_fields=["is_active", "updated_by"])


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

    def clean(self):
        if self.role == self.Role.OWNER:
            existing_owner = TenantMembership.objects.filter(
                tenant=self.tenant, role=self.Role.OWNER
            ).exclude(pk=self.pk)
            if existing_owner.exists():
                raise ValidationError("Each tenant can have only one owner.")

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_user(self):
        return self.role == self.Role.USER
