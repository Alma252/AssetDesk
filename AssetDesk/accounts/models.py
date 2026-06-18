from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel


class Department(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class User(AbstractUser ,TimeStampedModel):

    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        IT_EXPERT = "it_expert", "IT Expert"
        EMPLOYEE = "employee", "Employee"

    email = models.EmailField(
        unique=True
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Employee ID"
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EMPLOYEE,
        db_index=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    position = models.CharField(
        max_length=100,
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_manager(self):
        return self.role == self.Roles.MANAGER

    @property
    def is_it_expert(self):
        return self.role == self.Roles.IT_EXPERT

    @property
    def is_employee(self):
        return self.role == self.Roles.EMPLOYEE



    def clean(self):
        super().clean()

        if not self.employee_id:
            raise ValidationError(
                {"employee_id": "Employee ID is required."}
            )

    def __str__(self):
        full_name = self.get_full_name().strip()

        if full_name:
            return f"{full_name} ({self.employee_id})"

        return f"{self.username} ({self.employee_id})"

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"]),
        ]

    @property
    def is_staff_member(self):
        if self.is_superuser:
            return True

        return self.role in (
            self.Roles.ADMIN,
            self.Roles.MANAGER,
            self.Roles.IT_EXPERT,
        )

    @property
    def can_manage_assets(self):
        return self.is_staff_member

    @property
    def can_manage_tickets(self):
        return self.is_staff_member