# tickets/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import TimeStampedModel
from accounts.models import User
from assets.models import Asset


class Ticket(TimeStampedModel):

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        AWAITING_USER = "awaiting_user", "Awaiting User"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    ticket_no = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tickets_created",
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_assigned",
        limit_choices_to={
            "role__in": [
                "admin",
                "manager",
                "it_expert",
            ]
        },
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        help_text="Related asset (optional)",
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
        default=Status.OPEN,
        db_index=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self.status in (
            self.Status.OPEN,
            self.Status.IN_PROGRESS,
            self.Status.AWAITING_USER,
        )

    @property
    def is_overdue(self) -> bool:
        if not self.is_open:
            return False

        return (
            timezone.now() - self.created_at
        ).days > 3

    @property
    def resolution_time_days(self):
        if not self.resolved_at:
            return None

        return (
            self.resolved_at - self.created_at
        ).days

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    def clean(self):
        super().clean()

        if (
            self.status in (
                self.Status.RESOLVED,
                self.Status.CLOSED,
            )
            and not self.assigned_to
        ):
            raise ValidationError(
                {
                    "assigned_to":
                    "Resolved/Closed tickets must have an assignee."
                }
            )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        self.full_clean()

        super().save(*args, **kwargs)

        if is_new and not self.ticket_no:
            self.ticket_no = f"TCK-{self.pk:05d}"

            Ticket.objects.filter(
                pk=self.pk
            ).update(
                ticket_no=self.ticket_no
            )

        updates = []

        if (
            self.status == self.Status.RESOLVED
            and not self.resolved_at
        ):
            self.resolved_at = timezone.now()
            updates.append("resolved_at")

        if (
            self.status == self.Status.CLOSED
            and not self.closed_at
        ):
            self.closed_at = timezone.now()
            updates.append("closed_at")

        if updates:
            super().save(
                update_fields=updates
            )

    def __str__(self):
        return (
            f"{self.ticket_no} - "
            f"{self.title}"
        )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "priority"]
            ),
            models.Index(
                fields=["assigned_to", "status"]
            ),
        ]


class TicketComment(TimeStampedModel):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ticket_comments",
    )

    message = models.TextField()

    attachment = models.FileField(
        upload_to="tickets/comments/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return (
            f"Comment by "
            f"{self.author} "
            f"on {self.ticket.ticket_no}"
        )

    class Meta:
        verbose_name = "Ticket Comment"
        verbose_name_plural = "Ticket Comments"
        ordering = ["created_at"]