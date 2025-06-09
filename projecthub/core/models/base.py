import uuid

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(blank=True, default=timezone.now)
    updated_at = models.DateTimeField(blank=True, default=timezone.now)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=models.Q(updated_at__gte=models.F("created_at")),
                name="%(app_label)s_%(class)s_updated_after_created",
            )
        ]


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


# TODO: maybe create base model that uses custom base queryset
#  that demands to define `for_tenant` method