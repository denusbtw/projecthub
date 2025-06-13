from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from projecthub.comments.models import Comment
from projecthub.core.admin import BaseAdmin
from projecthub.tasks.models import Task, Board


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ("body", "created_by")
    readonly_fields = ("created_by",)
    fk_name = "task"
    extra = 1


@admin.register(Task)
class TaskAdmin(BaseAdmin):
    list_display = (
        "name",
        "project_link",
        "board_link",
        "priority",
        "responsible_link",
        "created_at",
    )
    list_select_related = ("project", "board", "responsible")
    search_fields = ("name", "project__name", "responsible__username")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("project", "board", "responsible")
    inlines = (CommentInline,)

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "project",
                    "name",
                    "priority",
                    "description",
                    "responsible",
                    "start_date",
                    "end_date",
                    "close_date",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("created_by", "updated_by", "created_at", "updated_at")},
        ),
    ]

    def save_model(self, request, obj, form, change):
        responsible = form.cleaned_data.pop("responsible")
        obj.assign_responsible(responsible)
        super().save_model(request, obj, form, change)

    @admin.display(description="Project")
    def project_link(self, obj):
        url = reverse("admin:projects_project_change", args=(obj.project_id,))
        return format_html('<a href="{}">{}</a>', url, obj.project.name)

    @admin.display(description="Board")
    def board_link(self, obj):
        if obj.board is None:
            return None

        url = reverse("admin:tasks_board_change", args=(obj.board_id,))
        return format_html('<a href="{}">{}</a>', url, obj.board.name)

    @admin.display(description="Responsible")
    def responsible_link(self, obj):
        if obj.responsible is None:
            return None

        url = reverse("admin:users_user_change", args=(obj.responsible_id,))
        return format_html('<a href="{}">{}</a>', url, obj.responsible.username)


@admin.register(Board)
class BoardAdmin(BaseAdmin):
    list_display = ("name", "project_link", "order")
    list_select_related = ("project",)
    search_fields = ("name", "project__name")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("project",)

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "project",
                    "name",
                    "order",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at")},
        ),
    ]

    @admin.display(description="Project")
    def project_link(self, obj):
        url = reverse("admin:projects_project_change", args=(obj.project_id,))
        return format_html('<a href="{}">{}</a>', url, obj.project.name)
