from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from projecthub.core.models import TenantMembership, Tenant


class BaseAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    fields = ("user", "role")
    autocomplete_fields = ("user",)
    extra = 1


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "sub_domain", "name", "is_active", "created_at")
    search_fields = ("sub_domain", "name")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    inlines = (TenantMembershipInline,)

    fieldsets = [
        (
            None,
            {
                "fields": ("name", "sub_domain", "is_active")
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at"
                )
            }
        )
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TenantMembership)
class TenantMembershipAdmin(BaseAdmin):
    list_display = ("id", "tenant_link", "user_link", "role")
    list_select_related = ("tenant", "user")
    search_fields = (
        "tenant__name",
        "tenant__sub_domain",
        "user__username",
        "user__email",
    )
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    autocomplete_fields = ("tenant", "user")
    list_filter = ("role", "tenant")

    fieldsets = [
        (
            None,
            {
                "fields": ("tenant", "user", "role"),
            }
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at"
                ),
            },
        ),
    ]

    @admin.display(description="Tenant")
    def tenant_link(self, obj):
        url = reverse("admin:core_tenant_change", args=(obj.tenant_id,))
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.tenant.sub_domain
        )

    @admin.display(description="User")
    def user_link(self, obj):
        url = reverse("admin:users_user_change", args=(obj.user_id,))
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.user.username
        )
