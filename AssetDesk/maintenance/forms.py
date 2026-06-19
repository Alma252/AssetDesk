from django import forms

from .models import MaintenanceSchedule, MaintenanceLog


class BootstrapFormMixin:
    def _add_bootstrap_classes(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"


class MaintenanceScheduleForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = MaintenanceSchedule
        fields = ["asset", "title", "description", "frequency", "next_due_date", "is_active"]
        widgets = {
            "description":  forms.Textarea(attrs={"rows": 3}),
            "next_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()


class MaintenanceLogForm(BootstrapFormMixin, forms.ModelForm):


    class Meta:
        model = MaintenanceLog
        fields = [
            "asset", "schedule", "maintenance_type", "priority",
            "planned_date", "vendor", "notes",
        ]
        widgets = {
            "planned_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()
        self.fields["schedule"].required = False
        self.fields["schedule"].queryset = MaintenanceSchedule.objects.filter(is_active=True)


class MaintenanceLogUpdateForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = MaintenanceLog
        fields = [
            "asset", "schedule", "maintenance_type", "priority", "status",
            "performed_by", "planned_date", "completed_date",
            "vendor", "cost", "notes",
        ]
        widgets = {
            "planned_date":   forms.DateInput(attrs={"type": "date"}),
            "completed_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()
        self.fields["schedule"].required = False

        from accounts.models import User
        self.fields["performed_by"].queryset = User.objects.filter(
            is_active=True,
            role__in=[User.Roles.ADMIN, User.Roles.MANAGER, User.Roles.IT_EXPERT],
        ).order_by("last_name", "first_name", "username")