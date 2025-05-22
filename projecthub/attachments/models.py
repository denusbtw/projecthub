from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from projecthub.comments.models import Comment
from projecthub.core.models import UUIDModel
from projecthub.tasks.models import Task


class Attachment(UUIDModel):
    # TODO: add validators
    file = models.FileField(upload_to="attachments/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text=_("User who uploaded this attachment.")
    )
    uploaded_at = models.DateTimeField(blank=True, default=timezone.now)

    class Meta:
        abstract = True
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.file.name


class TaskAttachment(Attachment):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments"
    )


class CommentAttachment(Attachment):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
