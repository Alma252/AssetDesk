from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from core.models import TimeStampedModel
from accounts.models import User
from assets.models import Asset


class MaintenanceSchedule(TimeStampedModel):
    class Frequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMI_ANNUAL = "semi_annual", "Every 6 Months"
        ANNUAL = "annual", "Annual"
        ONE_TIME = "one_time", "One-Time"

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="maintenance_schedules",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.SEMI_ANNUAL,
    )
    next_due_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.asset.asset_code} - {self.title}"

    class Meta:
        verbose_name = "Maintenance Schedule"
        verbose_name_plural = "Maintenance Schedules"
        ordering = ["next_due_date"]
        indexes = [
            models.Index(fields=["is_active", "next_due_date"]),
        ]


class MaintenanceLog(TimeStampedModel):
    class MaintenanceType(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled Maintenance"
        REPAIR = "repair", "Repair"
        INSPECTION = "inspection", "Inspection"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="maintenance_logs",
    )

    schedule = models.ForeignKey(
        MaintenanceSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )

    maintenance_type = models.CharField(
        max_length=20,
        choices=MaintenanceType.choices,
        default=MaintenanceType.SCHEDULED,
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_maintenance",
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_maintenance",
    )

    planned_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)

    vendor = models.CharField(max_length=255, blank=True)

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()

        if self.completed_date and self.completed_date < self.planned_date:
            raise ValidationError(
                {"completed_date": "Completion date cannot be before planned date."}
            )

        if self.status == self.Status.COMPLETED and not self.completed_date:
            raise ValidationError(
                {"completed_date": "Completed maintenance requires completion date."}
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.COMPLETED and not self.completed_date:
            self.completed_date = timezone.now().date()

        self.full_clean()
        super().save(*args, **kwargs)

        if self.status == self.Status.COMPLETED and self.schedule and self.schedule.is_active:
            self.schedule.next_due_date = self.calculate_next_due_date()
            self.schedule.save(update_fields=["next_due_date", "updated_at"])

    def calculate_next_due_date(self):
        if not self.schedule:
            return None

        if self.schedule.frequency == self.schedule.Frequency.ONE_TIME:
            return self.schedule.next_due_date

        base_date = self.completed_date or timezone.now().date()

        mapping = {
            self.schedule.Frequency.MONTHLY: relativedelta(months=1),
            self.schedule.Frequency.QUARTERLY: relativedelta(months=3),
            self.schedule.Frequency.SEMI_ANNUAL: relativedelta(months=6),
            self.schedule.Frequency.ANNUAL: relativedelta(years=1),
        }

        delta = mapping.get(self.schedule.frequency, relativedelta(months=6))
        return base_date + delta

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        if not self.completed_date:
            self.completed_date = timezone.now().date()
        self.save()

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED

    @property
    def is_overdue(self):
        return (
            self.status != self.Status.COMPLETED
            and self.planned_date < timezone.now().date()
        )

    @property
    def responsible_person(self):
        return self.performed_by or self.reported_by

    @property
    def has_cost(self):
        return bool(self.cost and self.cost > 0)

    def __str__(self):
        return f"{self.asset.asset_code} - {self.get_maintenance_type_display()} [{self.get_status_display()}]"

    def __repr__(self):
        return f"<MaintenanceLog id={self.pk} asset={self.asset.asset_code!r} status={self.status!r}>"

    class Meta:
        verbose_name = "Maintenance Log"
        verbose_name_plural = "Maintenance Logs"
        ordering = ["-planned_date"]
        indexes = [
            models.Index(fields=["status", "planned_date"]),
            models.Index(fields=["priority", "status"]),
            models.Index(fields=["asset", "status"]),
        ]