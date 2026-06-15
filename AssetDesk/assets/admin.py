from django.contrib import admin

from .models import AssetCategory, Asset, AssetAssignment


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = (
        "asset_code",
        "name",
        "category",
        "status",
        "brand",
        "model",
    )

    list_filter = (
        "status",
        "category",
        "brand",
    )

    search_fields = (
        "asset_code",
        "name",
        "serial_number",
    )

    readonly_fields = ("created_at", "updated_at")

    ordering = ("asset_code",)


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "asset",
        "employee",
        "assigned_at",
        "returned_at",
    )

    list_filter = (
        "assigned_at",
        "returned_at",
    )

    search_fields = (
        "asset__asset_code",
        "employee__username",
        "employee__employee_id",
    )

    ordering = ("-assigned_at",)