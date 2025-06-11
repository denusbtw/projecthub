from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.timezone import localtime

from projecthub.tasks.models import Task

User = get_user_model()


@shared_task
def send_task_assignment_email(task_id, user_id):
    task = Task.objects.get(pk=task_id)
    user = User.objects.get(pk=user_id)
    plain_message = (
        f"Вам призначено завдання {task.name} у проєкті {task.project.name}."
    )

    send_mail(
        subject=f"Вам призначено завдання: {task.name}",
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=plain_message,
        fail_silently=False,
    )

    return f"Email sent to {user.email} for task {task.name}"


@shared_task
def send_daily_task_reminders():
    tasks = (
        Task.objects.filter(close_date__isnull=True)
        .select_related("responsible", "project", "board")
        .order_by("end_date")
    )

    user_to_tasks = {}
    for task in tasks:
        user = task.responsible
        if user and user.email:
            user_to_tasks.setdefault(user, []).append(task)

    for user, user_tasks in user_to_tasks.items():
        lines = []
        for task in user_tasks:
            lines.append(
                f"- [Project: {task.project.name}] {task.name} (deadline: {localtime(task.end_date).strftime('%Y-%m-%d %H:%M')})"
            )

        message = "\n".join(lines)
        subject = "Your Tasks for Today"

        send_mail(
            subject=subject,
            message=f"You have the following open tasks: \n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
