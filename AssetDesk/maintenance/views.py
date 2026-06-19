from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import MaintenanceSchedule, MaintenanceLog
from .forms import MaintenanceScheduleForm, MaintenanceLogForm, MaintenanceLogUpdateForm


class CanManageMaintenanceMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff_member


# MAINTENANCE LOG

class MaintenanceLogListView(LoginRequiredMixin, CanManageMaintenanceMixin, ListView):
    model = MaintenanceLog
    template_name = "maintenance/log_list.html"
    context_object_name = "logs"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            MaintenanceLog.objects
            .select_related("asset", "schedule", "reported_by", "performed_by")
            .order_by("-planned_date")
        )

        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        search = self.request.GET.get("search")

        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if search:
            qs = qs.filter(
                Q(asset__asset_code__icontains=search)
                | Q(asset__name__icontains=search)
                | Q(vendor__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = MaintenanceLog.Status.choices
        context["priority_choices"] = MaintenanceLog.Priority.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["current_priority"] = self.request.GET.get("priority", "")
        context["search"] = self.request.GET.get("search", "")
        return context


class MaintenanceLogDetailView(LoginRequiredMixin, CanManageMaintenanceMixin, DetailView):
    model = MaintenanceLog
    template_name = "maintenance/log_detail.html"
    context_object_name = "log"

    def get_queryset(self):
        return MaintenanceLog.objects.select_related(
            "asset", "schedule", "reported_by", "performed_by"
        )


class MaintenanceLogCreateView(LoginRequiredMixin, CanManageMaintenanceMixin, CreateView):
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = "maintenance/log_form.html"

    def get_initial(self):
        initial = super().get_initial()
        asset_id = self.request.GET.get("asset")
        if asset_id:
            initial["asset"] = asset_id
        return initial

    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        messages.success(self.request, "Maintenance log created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "New Maintenance Log"
        context["btn_label"] = "Create Log"
        return context

    def get_success_url(self):
        return reverse_lazy("maintenance-log-detail", kwargs={"pk": self.object.pk})


class MaintenanceLogUpdateView(LoginRequiredMixin, CanManageMaintenanceMixin, UpdateView):
    model = MaintenanceLog
    form_class = MaintenanceLogUpdateForm
    template_name = "maintenance/log_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Maintenance log updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Edit Log — {self.object.asset.asset_code}"
        context["btn_label"] = "Save Changes"
        return context

    def get_success_url(self):
        return reverse_lazy("maintenance-log-detail", kwargs={"pk": self.object.pk})


class MaintenanceLogDeleteView(LoginRequiredMixin, CanManageMaintenanceMixin, DeleteView):
    model = MaintenanceLog
    template_name = "maintenance/log_confirm_delete.html"
    success_url = reverse_lazy("maintenance-log-list")

    def form_valid(self, form):
        messages.success(self.request, "Maintenance log deleted.")
        return super().form_valid(form)


class MaintenanceLogCompleteView(LoginRequiredMixin, CanManageMaintenanceMixin, View):

    def post(self, request, pk):
        log = get_object_or_404(MaintenanceLog, pk=pk)

        log.status = MaintenanceLog.Status.COMPLETED
        log.completed_date = log.completed_date or timezone.now().date()
        log.performed_by = log.performed_by or request.user
        log.save()

        messages.success(request, f"Maintenance for «{log.asset}» marked as completed.")
        return redirect("maintenance-log-detail", pk=pk)


# MAINTENANCE SCHEDULE (برنامه‌ریزی دوره‌ای)

class MaintenanceScheduleListView(LoginRequiredMixin, CanManageMaintenanceMixin, ListView):
    model = MaintenanceSchedule
    template_name = "maintenance/schedule_list.html"
    context_object_name = "schedules"
    paginate_by = 20

    def get_queryset(self):
        qs = MaintenanceSchedule.objects.select_related("asset").order_by("next_due_date")

        is_active = self.request.GET.get("is_active")
        search = self.request.GET.get("search")

        if is_active == "1":
            qs = qs.filter(is_active=True)
        elif is_active == "0":
            qs = qs.filter(is_active=False)

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(asset__asset_code__icontains=search)
                | Q(asset__name__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_is_active"] = self.request.GET.get("is_active", "")
        context["search"] = self.request.GET.get("search", "")
        context["today"] = timezone.now().date()
        return context


class MaintenanceScheduleCreateView(LoginRequiredMixin, CanManageMaintenanceMixin, CreateView):
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/schedule_form.html"
    success_url = reverse_lazy("maintenance-schedule-list")

    def form_valid(self, form):
        messages.success(self.request, "Maintenance schedule created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "New Maintenance Schedule"
        context["btn_label"] = "Create Schedule"
        return context


class MaintenanceScheduleUpdateView(LoginRequiredMixin, CanManageMaintenanceMixin, UpdateView):
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/schedule_form.html"
    success_url = reverse_lazy("maintenance-schedule-list")

    def form_valid(self, form):
        messages.success(self.request, "Maintenance schedule updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Edit Schedule — {self.object.asset.asset_code}"
        context["btn_label"] = "Save Changes"
        return context


class MaintenanceScheduleDeleteView(LoginRequiredMixin, CanManageMaintenanceMixin, DeleteView):
    model = MaintenanceSchedule
    template_name = "maintenance/schedule_confirm_delete.html"
    success_url = reverse_lazy("maintenance-schedule-list")

    def form_valid(self, form):
        messages.success(self.request, "Maintenance schedule deleted.")
        return super().form_valid(form)