# assets/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import TimeStampedModel
from accounts.models import User


class AssetCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Asset Category"
        verbose_name_plural = "Asset Categories"
        ordering = ["name"]


class Asset(TimeStampedModel):
    class AssetStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        ASSIGNED = "assigned", "Assigned"
        UNDER_REPAIR = "under_repair", "Under Repair"
        RETIRED = "retired", "Retired"

    name = models.CharField(max_length=255)

    asset_code = models.CharField(
        max_length=50,
        unique=True,  # unique خودش index می‌سازه
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT,
        related_name="assets",
    )

    department = models.ForeignKey(
        "accounts.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.AVAILABLE,
        db_index=True,
    )

    purchase_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    # Properties

    @property
    def is_available(self) -> bool:
        return self.status == self.AssetStatus.AVAILABLE

    @property
    def current_assignment(self):
        return self.assignments.filter(returned_at__isnull=True).first()

    @property
    def current_holder(self):
        assignment = self.current_assignment
        return assignment.employee if assignment else None


    def __str__(self) -> str:
        return f"{self.asset_code} - {self.name}"

    def __repr__(self) -> str:
        return f"<Asset code={self.asset_code!r} status={self.status!r}>"

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        ordering = ["asset_code"]


class AssetAssignment(TimeStampedModel):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="asset_assignments",
    )

    assigned_at = models.DateTimeField(default=timezone.now)  # ← default اضافه شد
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Validation
    def clean(self):
        super().clean()

        # asset نباید همزمان پیش دو نفر باشه
        if not self.returned_at:
            active_qs = AssetAssignment.objects.filter(
                asset=self.asset,
                returned_at__isnull=True,
            )
            if self.pk:
                active_qs = active_qs.exclude(pk=self.pk)

            if active_qs.exists():
                raise ValidationError(
                    {"asset": f"Asset «{self.asset}» is currently assigned to someone else."}
                )

        #  زمان برگشت نباید قبل از زمان تحویل باشه
        if self.returned_at and self.assigned_at:
            if self.returned_at < self.assigned_at:
                raise ValidationError(
                    {"returned_at": "Return date cannot be before assignment date."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # آپدیت خودکار status روی Asset
        if self.returned_at:
            self.asset.status = Asset.AssetStatus.AVAILABLE
        else:
            self.asset.status = Asset.AssetStatus.ASSIGNED

        self.asset.save(update_fields=["status", "updated_at"])


    # Properties
    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    @property
    def duration_days(self) -> int | None:

        if not self.assigned_at:
            return None
        end = self.returned_at or timezone.now()
        return (end - self.assigned_at).days

    def __str__(self) -> str:
        status = "active" if self.is_active else "returned"
        return f"{self.asset.asset_code} → {self.employee} [{status}]"

    class Meta:
        verbose_name = "Asset Assignment"
        verbose_name_plural = "Asset Assignments"
        ordering = ["-assigned_at"]
        indexes = [
            models.Index(
                fields=["asset", "returned_at"],
                name="idx_assignment_asset_active",
            ),
            models.Index(
                fields=["employee", "returned_at"],
                name="idx_assignment_employee_active",
            ),
        ]
