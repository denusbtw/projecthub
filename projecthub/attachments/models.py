from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from projecthub.comments.models import Comment
from projecthub.core.models import UUIDModel
from projecthub.tasks.models import Task


class AttachmentQuerySet(models.QuerySet):

    def for_tenant(self, tenant):
        return self.filter(
            models.Q(task__project__tenant=tenant)
            | models.Q(comment__task__project__tenant=tenant)
        )

    def for_task(self, task_id):
        return self.filter(task_id=task_id)

    def for_comment(self, comment_id):
        return self.filter(comment_id=comment_id)


class Attachment(UUIDModel):
    file = models.FileField(upload_to="attachments/")
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text=_("User who uploaded this attachment."),
    )
    uploaded_at = models.DateTimeField(blank=True, default=timezone.now)

    objects = AttachmentQuerySet.as_manager()

    class Meta:
        ordering = ["-uploaded_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (models.Q(task__isnull=False) & models.Q(comment__isnull=True))
                    | (models.Q(task__isnull=True) & models.Q(comment__isnull=False))
                ),
                name="attachment_task_xor_comment",
            )
        ]

    def __str__(self):
        return self.file.name
