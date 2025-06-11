from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from projecthub.core.models import UUIDModel, TimestampedModel, Tenant


class ProjectQuerySet(models.QuerySet):

    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

    def visible_to(self, user, tenant):
        if user.is_staff or tenant.owner_id == user.id:
            return self

        return self.filter(
            models.Q(owner=user)
            | models.Q(supervisor=user)
            | models.Q(responsible=user)
            | models.Q(members__user=user)
        )


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
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_projects",
        help_text=_("Owner of project"),
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_projects",
        help_text=_("Supervisor of project"),
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_projects",
        help_text=_("Responsible of project"),
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

    # TODO:
    # add search vector: `search_vector = SearchVectorField(null=True)`
    # create index for it `GinIndex(fields=["search_vector"]`
    # override save method: `self.search_vector = SearchVector("body")
    # in views:
    # def get_queryset(self):
    #   queryset = super().get_queryset()
    #   query = self.request.query_params.get('search')
    #   if query:
    #       search_query = SearchQuery(query)
    #       queryset = queryset.annotate(
    #           rank=SearchRank(F('search_vector'), search_query)
    #       ).filter(search_vector=search_query).order_by('-rank')
    #   return queryset

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

    def set_start_date(self, start_date):
        self.start_date = start_date
        now = timezone.now()

        if start_date > now.date():
            self.status = self.Status.PENDING
        elif start_date <= now.date():
            self.status = self.Status.ACTIVE

        self.close_date = None
        self.save(update_fields=["status", "close_date"])

    def archive(self, updated_by):
        if updated_by is None:
            raise ValidationError("updated_by is required.")

        if self.is_archived:
            raise ValidationError("Project is already archived.")

        now = timezone.now()
        self.status = self.Status.ARCHIVED
        self.updated_by = updated_by
        self.updated_at = now
        self.close_date = now
        self.save(update_fields=["status", "updated_by", "updated_at", "close_date"])

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
