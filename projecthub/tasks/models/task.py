from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import get_object_or_404

from projecthub.core.models import UUIDModel, TimestampedModel
from projecthub.projects.models import ProjectMembership, Project


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

        if user.id == tenant.owner_id:
            return self

        project = get_object_or_404(Project, pk=project_id)
        if user.id in {project.owner_id, project.supervisor_id, project.responsible_id}:
            return self

        project_membership = ProjectMembership.objects.filter(
            project=project, user=user, role=ProjectMembership.Role.USER
        ).first()

        if project_membership:
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
    board = models.ForeignKey(
        "Board",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text=_("Board of task."),
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
        board_name = getattr(self.board, "name", "No board")
        return f"{self.name} ({board_name}) in {self.project.name}"

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None

    def set_board(self, board, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        # TODO: if code is None, it means that user wants to revoke from task
        # so call self.revoke(updated_by)

        now = timezone.now()

        self.board = board
        self.updated_by = updated_by
        self.updated_at = now

        if board.is_done:
            self.close_date = now

        fields = ["board", "updated_by", "updated_at"]
        if board.is_done:
            fields.append("close_date")

        self.save(update_fields=fields)

    def revoke(self, updated_by):
        if not updated_by:
            raise ValidationError("updated_by is required.")

        self.board = None
        self.responsible = None
        # TODO: remove changing updated_by and updated_at here
        self.updated_by = updated_by
        self.updated_at = timezone.now()
        self.save(update_fields=["board", "responsible", "updated_by", "updated_at"])

    @property
    def is_todo(self):
        return self.board and self.board.is_todo

    @property
    def is_done(self):
        return self.board and self.board.is_done

    @property
    def is_in_progress(self):
        return self.board and self.board.is_in_progress

    @property
    def is_in_review(self):
        return self.board and self.board.is_in_review
