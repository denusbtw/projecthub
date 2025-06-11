from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

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
