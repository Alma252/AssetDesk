from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Organization Info", {
            "fields": (
                "employee_id",
                "role",
                "phone_number",
                "department",
                "position",
                "avatar",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Organization Info", {
            "fields": (
                "employee_id",
                "role",
                "phone_number",
                "department",
                "position",
                "avatar",
            )
        }),
    )

    list_display = (
        "username",
        "email",
        "employee_id",
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "employee_id",
    )

    ordering = ("username",)

    filter_horizontal = ()