from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from projecthub.core.admin import BaseAdmin
from .models import ProjectMembership, Project


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    fields = ("user", "role")
    autocomplete_fields = ("user",)
    fk_name = "project"
    extra = 1


# TODO: call `create_default_boards` after project created
@admin.register(Project)
class ProjectAdmin(BaseAdmin):
    list_display = (
        "id",
        "name",
        "status",
        "tenant_link",
        "start_date",
        "end_date",
        "close_date",
    )
    list_select_related = ("tenant",)
    search_fields = ("name", "tenant__name")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("tenant",)
    inlines = (ProjectMembershipInline,)

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name",
                    "owner",
                    "supervisor",
                    "status",
                    "description",
                    "start_date",
                    "end_date",
                    "close_date",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "tenant",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    ]

    @admin.display(description="Tenant")
    def tenant_link(self, obj):
        url = reverse("admin:core_tenant_change", args=(obj.tenant_id,))
        return format_html("<a href={}>{}</a>", url, obj.tenant.name)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(BaseAdmin):
    list_display = ("id", "project_link", "user_link", "role")
    list_select_related = ("project", "user")
    search_fields = ("project__name", "user__username")
    list_filter = ("role",)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("project", "user")

    fieldsets = [
        (None, {"fields": ("project", "user", "role")}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at", "created_by", "updated_by")},
        ),
    ]

    @admin.display(description="Project")
    def project_link(self, obj):
        url = reverse("admin:projects_project_change", args=(obj.project_id,))
        return format_html('<a href="{}">{}</a>', url, obj.project.name)

    @admin.display(description="User")
    def user_link(self, obj):
        url = reverse("admin:users_user_change", args=(obj.user_id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
