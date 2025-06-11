from celery import shared_task
from django.db.models import OuterRef, Exists
from django.utils import timezone

from projecthub.projects.models import Project
from projecthub.tasks.models import Task


@shared_task
def archive_ended_projects():
    open_tasks = Task.objects.filter(project=OuterRef("pk"), close_date__isnull=True)

    ended_projects = Project.objects.filter(
        end_date__lte=timezone.now(), close_date__isnull=True
    )
    ended_projects = ended_projects.annotate(has_open_tasks=Exists(open_tasks))
    ended_projects = ended_projects.filter(has_open_tasks=False)

    ended_projects.update(status=Project.Status.ARCHIVED, close_date=timezone.now())


@shared_task
def activate_pending_projects():
    pending_projects = Project.objects.filter(start_date__lte=timezone.now())
    pending_projects.update(status=Project.Status.ACTIVE)
