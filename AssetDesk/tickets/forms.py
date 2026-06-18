# tickets/forms.py

from django import forms
from django.contrib.auth import get_user_model

from assets.models import Asset
from .models import Ticket, TicketComment

User = get_user_model()


class BootstrapFormMixin:
    def _add_bootstrap_classes(self):
        for field in self.fields.values():

            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"

            elif isinstance(
                field.widget,
                (forms.Select, forms.SelectMultiple)
            ):
                field.widget.attrs["class"] = "form-select"

            else:
                field.widget.attrs["class"] = "form-control"


class TicketForm(BootstrapFormMixin, forms.ModelForm):
    """
    Employee creates a ticket.
    """

    class Meta:
        model = Ticket
        fields = [
            "title",
            "description",
            "asset",
            "priority",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self._add_bootstrap_classes()

        self.fields["title"].label = "Title"
        self.fields["description"].label = "Description"
        self.fields["asset"].label = "Related Asset"
        self.fields["priority"].label = "Priority"

        if user:
            self.fields["asset"].queryset = (
                Asset.objects.filter(
                    assignments__employee=user,
                    assignments__returned_at__isnull=True,
                )
                .distinct()
                .order_by("asset_code")
            )
        else:
            self.fields["asset"].queryset = Asset.objects.none()

    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean_description(self):
        value = self.cleaned_data["description"].strip()

        if len(value) < 10:
            raise forms.ValidationError(
                "Please provide a more detailed description."
            )

        return value


class TicketUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """
    Used by Admin / Manager / IT Expert.
    """

    class Meta:
        model = Ticket
        fields = [
            "title",
            "description",
            "asset",
            "priority",
            "status",
            "assigned_to",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_bootstrap_classes()

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                is_active=True,
                role__in=[
                    User.Roles.ADMIN,
                    User.Roles.MANAGER,
                    User.Roles.IT_EXPERT,
                ],
            )
            .order_by(
                "last_name",
                "first_name",
                "username",
            )
        )

        self.fields["title"].label = "Title"
        self.fields["description"].label = "Description"
        self.fields["asset"].label = "Related Asset"
        self.fields["priority"].label = "Priority"
        self.fields["status"].label = "Status"
        self.fields["assigned_to"].label = "Assigned To"

    def clean_title(self):
        return self.cleaned_data["title"].strip()


class TicketAssignForm(BootstrapFormMixin, forms.ModelForm):
    """
    Quick assignment form.
    """

    class Meta:
        model = Ticket
        fields = [
            "assigned_to",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_bootstrap_classes()

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                is_active=True,
                role__in=[
                    User.Roles.ADMIN,
                    User.Roles.MANAGER,
                    User.Roles.IT_EXPERT,
                ],
            )
            .order_by(
                "last_name",
                "first_name",
                "username",
            )
        )

        self.fields["status"].choices = [
            (
                Ticket.Status.IN_PROGRESS,
                "In Progress",
            ),
            (
                Ticket.Status.AWAITING_USER,
                "Awaiting User",
            ),
        ]


class TicketCommentForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = TicketComment

        fields = [
            "message",
            "attachment",
        ]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Write your comment...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_bootstrap_classes()

        self.fields["message"].label = "Comment"
        self.fields["attachment"].label = "Attachment"

    def clean_message(self):
        value = self.cleaned_data["message"].strip()

        if not value:
            raise forms.ValidationError(
                "Comment cannot be empty."
            )

        return value