from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .base import UUIDModel, TimestampedModel


class TenantQuerySet(models.QuerySet):

    def visible_to(self, user):
        if user.is_staff:
            return self
        return self.filter(Q(owner=user) | Q(members__user=user))


class Tenant(UUIDModel, TimestampedModel):
    # PROTECT захищає від видалення користувача, якщо він є owner хоча б одного Tenant
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_tenants",
        help_text=_("Owner of tenant"),
    )
    name = models.CharField(max_length=255, help_text=_("Name of tenant."))
    sub_domain = models.CharField(
        max_length=63,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9]+(-[a-z0-9]+)*$",
                message=_(
                    "Subdomain must contain only lowercase letters, numbers and hyphens, and cannot start or end with a hyphen."
                ),
            )
        ],
        help_text=_("Subdomain of tenant."),
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

    objects = TenantQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("owner", "name"), name="unique_tenant_name_for_owner"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.sub_domain})"

    @property
    def is_inactive(self):
        return not self.is_active

    def _change_active_state(self, active: bool, updated_by):
        if not updated_by:
            raise ValueError("updated_by is required.")

        if self.is_active != active:
            self.is_active = active
            self.updated_by = updated_by
            self.save(update_fields=["is_active", "updated_by"])

    def activate(self, updated_by):
        self._change_active_state(True, updated_by)

    def deactivate(self, updated_by):
        self._change_active_state(False, updated_by)
