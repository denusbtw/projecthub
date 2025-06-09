import textwrap

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from projecthub.core.admin import BaseAdmin
from .models import Comment


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ("body", "created_by")
    readonly_fields = ("created_by",)
    fk_name = "parent"
    extra = 1
    verbose_name = "Reply"
    verbose_name_plural = "Replies"


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ("id", "body_short", "created_by_link", "parent_link", "task_link")
    list_select_related = ("created_by", "parent", "task")
    search_fields = ("body", "created_by__username", "parent__body", "task__name")
    readonly_fields = ("created_at", "updated_at", "created_by")
    autocomplete_fields = ("parent", "task")
    inlines = (CommentInline,)

    fieldsets = [
        (
            None,
            {
                "fields": ("task", "parent", "body")
            }
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at")
            }
        )
    ]

    @admin.display(description="Body")
    def body_short(self, obj):
        return textwrap.shorten(obj.body, 50)

    @admin.display(description="Author")
    def created_by_link(self, obj):
        url = reverse("admin:users_user_change", args=(obj.created_by_id,))
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.created_by.username
        )

    @admin.display(description="Parent")
    def parent_link(self, obj):
        if obj.parent is None:
            return None

        url = reverse("admin:comments_comment_change", args=(obj.parent_id,))
        return format_html(
            '<a href="{}">{}</a>',
            url, textwrap.shorten(obj.parent.body, 30)
        )

    @admin.display(description="Task")
    def task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=(obj.task_id,))
        return format_html(
            '<a href="{}">{}</a>',
            url, textwrap.shorten(obj.task.name, 30)
        )