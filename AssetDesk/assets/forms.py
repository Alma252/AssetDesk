from django import forms
from django.contrib.auth import get_user_model

from .models import Asset, AssetAssignment


User = get_user_model()


class BootstrapFormMixin:
    """
     برای اینکه فرم‌ها Bootstrap-friendly باشد.
    """

    def _add_bootstrap_classes(self):
        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"

            if not widget.attrs.get("placeholder") and not isinstance(
                widget, (forms.Select, forms.SelectMultiple, forms.CheckboxInput)
            ):
                widget.attrs["placeholder"] = field.label


class AssetForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "asset_code",
            "serial_number",
            "brand",
            "model",
            "category",
            "department",
            "status",
            "purchase_date",
            "description",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_bootstrap_classes()

        self.fields["name"].label = "Asset Name"
        self.fields["asset_code"].label = "Asset Code"
        self.fields["serial_number"].label = "Serial Number"
        self.fields["brand"].label = "Brand"
        self.fields["model"].label = "Model"
        self.fields["category"].label = "Category"
        self.fields["department"].label = "Department"
        self.fields["status"].label = "Status"
        self.fields["purchase_date"].label = "Purchase Date"
        self.fields["description"].label = "Description"

    def clean_asset_code(self):
        value = self.cleaned_data["asset_code"].strip()
        return value.upper()

    def clean_serial_number(self):
        value = self.cleaned_data.get("serial_number")
        if value:
            return value.strip()
        return None


class AssetAssignmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AssetAssignment
        fields = ["employee", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        self.asset = kwargs.pop("asset", None)
        super().__init__(*args, **kwargs)

        self._add_bootstrap_classes()

        self.fields["employee"].label = "Employee"
        self.fields["notes"].label = "Notes"

        self.fields["employee"].queryset = (
            User.objects.filter(is_active=True, is_active_employee=True)
            .select_related("department")
            .order_by("last_name", "first_name", "username")
        )

        def employee_label(user):
            full_name = user.get_full_name().strip()
            display_name = full_name if full_name else user.username
            return f"{display_name} ({user.employee_id})"

        self.fields["employee"].label_from_instance = employee_label

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get("employee")

        if employee and not employee.is_active_employee:
            self.add_error("employee", "Selected employee is not active.")

        return cleaned_data