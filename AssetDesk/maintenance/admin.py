from django.contrib import admin
from django.utils.html import format_html

from .models import MaintenanceSchedule, MaintenanceLog


class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    fields = (
        "maintenance_type",
        "priority",
        "status",
        "planned_date",
        "completed_date",
        "performed_by",
    )
    readonly_fields = ("completed_date",)
    autocomplete_fields = ("performed_by", "reported_by")
    show_change_link = True


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "asset",
        "frequency",
        "next_due_date",
        "is_active",
        "is_overdue_display",
    )
    list_filter = (
        "frequency",
        "is_active",
        "next_due_date",
    )
    search_fields = (
        "title",
        "description",
        "asset__asset_code",
        "asset__name",
    )
    ordering = ("next_due_date",)
    date_hierarchy = "next_due_date"
    autocomplete_fields = ("asset",)
    inlines = [MaintenanceLogInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Schedule", {
            "fields": (
                "asset",
                "title",
                "description",
                "frequency",
                "next_due_date",
                "is_active",
            )
        }),
        ("System Information", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(boolean=True, description="Overdue")
    def is_overdue_display(self, obj):
        return obj.is_active and obj.next_due_date < timezone.now().date()


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "maintenance_type",
        "priority_badge",
        "status_badge",
        "planned_date",
        "completed_date",
        "reported_by",
        "performed_by",
        "vendor",
        "cost",
        "is_overdue_display",
    )
    list_filter = (
        "maintenance_type",
        "priority",
        "status",
        "planned_date",
        "completed_date",
        "asset",
    )
    search_fields = (
        "asset__asset_code",
        "asset__name",
        "vendor",
        "notes",
        "reported_by__username",
        "reported_by__employee_id",
        "performed_by__username",
        "performed_by__employee_id",
    )
    ordering = ("-planned_date",)
    date_hierarchy = "planned_date"
    autocomplete_fields = (
        "asset",
        "schedule",
        "reported_by",
        "performed_by",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Maintenance Information", {
            "fields": (
                "asset",
                "schedule",
                "maintenance_type",
                "priority",
                "status",
            )
        }),
        ("People", {
            "fields": (
                "reported_by",
                "performed_by",
            )
        }),
        ("Dates", {
            "fields": (
                "planned_date",
                "completed_date",
            )
        }),
        ("Vendor & Cost", {
            "fields": (
                "vendor",
                "cost",
            )
        }),
        ("Notes", {
            "fields": ("notes",)
        }),
        ("System Information", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    actions = ["mark_completed"]

    @admin.display(description="Priority")
    def priority_badge(self, obj):
        colors = {
            "low": "secondary",
            "medium": "info",
            "high": "warning",
            "critical": "danger",
        }
        color = colors.get(obj.priority, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_priority_display(),
        )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "pending": "secondary",
            "in_progress": "primary",
            "completed": "success",
            "cancelled": "danger",
        }
        color = colors.get(obj.status, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(boolean=True, description="Overdue")
    def is_overdue_display(self, obj):
        return obj.is_overdue

    @admin.action(description="Mark selected maintenance logs as completed")
    def mark_completed(self, request, queryset):
        for item in queryset:
            item.mark_completed()