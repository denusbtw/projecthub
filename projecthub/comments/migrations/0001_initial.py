# Generated by Django 5.2.1 on 2025-05-13 20:07

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tasks", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "body",
                    models.CharField(help_text="Body of comment.", max_length=2000),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="Author of comment",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        help_text="Parent comment.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="replies",
                        to="comments.comment",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        help_text="Task that owns this comment.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="tasks.task",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("parent_id", models.F("id")), _negated=True
                        ),
                        name="prevent_self_parent",
                    )
                ],
            },
        ),
    ]
