from django.contrib import admin
from .models import Ticket, TicketComment

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    fields = ("author", "message", "attachment", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_no",
        "title",
        "created_by",
        "assigned_to",
        "asset",
        "priority",
        "status",
        "created_at",
        "resolved_at",
        "closed_at",
        "is_open_display",
        "is_overdue_display",
    )

    list_filter = (
        "status",
        "priority",
        "created_at",
        "resolved_at",
        "closed_at",
    )

    search_fields = (
        "ticket_no",
        "title",
        "description",
        "created_by__username",
        "created_by__employee_id",
        "assigned_to__username",
        "assigned_to__employee_id",
        "asset__asset_code",
        "asset__name",
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("ticket_no", "resolved_at", "closed_at", "created_at", "updated_at")
    autocomplete_fields = ("created_by", "assigned_to", "asset")
    inlines = [TicketCommentInline]

    fieldsets = (
        ("Ticket Info", {
            "fields": (
                "ticket_no",
                "title",
                "description",
                "asset",
                "priority",
                "status",
            )
        }),
        ("Assignment", {
            "fields": (
                "created_by",
                "assigned_to",
            )
        }),
        ("Timestamps", {
            "fields": (
                "resolved_at",
                "closed_at",
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(boolean=True, description="Open")
    def is_open_display(self, obj):
        return obj.is_open

    @admin.display(boolean=True, description="Overdue")
    def is_overdue_display(self, obj):
        return obj.is_overdue


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = (
        "ticket",
        "author",
        "created_at",
        "has_attachment",
    )

    list_filter = (
        "created_at",
        "author",
    )

    search_fields = (
        "ticket__ticket_no",
        "ticket__title",
        "author__username",
        "author__employee_id",
        "message",
    )

    ordering = ("-created_at",)
    autocomplete_fields = ("ticket", "author")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(boolean=True, description="Attachment")
    def has_attachment(self, obj):
        return bool(obj.attachment)