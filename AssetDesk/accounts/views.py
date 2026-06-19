from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from assets.models import Asset, AssetAssignment
from tickets.models import Ticket
from maintenance.models import MaintenanceLog
from django.views.generic import TemplateView
from reportlab.pdfgen import canvas
from django.http import HttpResponse


class LoginView(View):

    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)

        messages.error(request, "Username or password is incorrect.")
        return render(request, self.template_name)


class LogoutView(View):

    def post(self, request):
        logout(request)
        return redirect("login")


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        user = request.user

        assignments_qs = (
            AssetAssignment.objects
            .select_related("asset", "asset__category")
            .filter(employee=user)
            .order_by("-assigned_at")
        )

        active_assignments = assignments_qs.filter(returned_at__isnull=True)

        recent_tickets_qs = (
            Ticket.objects
            .select_related("asset", "assigned_to")
            .filter(created_by=user)
            .order_by("-created_at")
        )

        open_tickets_count = Ticket.objects.filter(
            created_by=user,
            status__in=[
                Ticket.Status.OPEN,
                Ticket.Status.IN_PROGRESS,
                Ticket.Status.AWAITING_USER,
            ],
        ).count()

        resolved_tickets_count = Ticket.objects.filter(
            created_by=user,
            status=Ticket.Status.RESOLVED,
        ).count()

        closed_tickets_count = Ticket.objects.filter(
            created_by=user,
            status=Ticket.Status.CLOSED,
        ).count()

        context = {
            "total_assignments_count": assignments_qs.count(),
            "current_assets_count": active_assignments.count(),
            "total_tickets_count": recent_tickets_qs.count(),
            "open_tickets_count": open_tickets_count,
            "resolved_tickets_count": resolved_tickets_count,
            "closed_tickets_count": closed_tickets_count,
            "active_assignments": active_assignments,
            "recent_assignments": assignments_qs[:5],
            "recent_tickets": recent_tickets_qs[:5],
        }

        return render(request, self.template_name, context)

class DashboardView(LoginRequiredMixin, View):

    template_name = "accounts/dashboard.html"

    def get(self, request):

        user = request.user

        if user.is_staff_member:

            total_assets = Asset.objects.count()

            available_assets = Asset.objects.filter(
                status=Asset.AssetStatus.AVAILABLE
            ).count()

            assigned_assets = Asset.objects.filter(
                status=Asset.AssetStatus.ASSIGNED
            ).count()

            repair_assets = Asset.objects.filter(
                status=Asset.AssetStatus.UNDER_REPAIR
            ).count()

            retired_assets = Asset.objects.filter(
                status=Asset.AssetStatus.RETIRED
            ).count()

            recent_assets = Asset.objects.select_related(
                "category",
                "department"
            ).order_by("-created_at")[:5]

            recent_assignments = AssetAssignment.objects.select_related(
                "asset",
                "employee"
            ).order_by("-assigned_at")[:5]

            open_tickets = Ticket.objects.filter(
                status__in=[
                    Ticket.Status.OPEN,
                    Ticket.Status.IN_PROGRESS,
                    Ticket.Status.AWAITING_USER,
                ]
            ).count()

            recent_tickets = Ticket.objects.select_related(
                "created_by",
                "assigned_to",
            ).order_by("-created_at")[:5]

            open_maintenance = MaintenanceLog.objects.filter(
                status__in=[
                    MaintenanceLog.Status.PENDING,
                    MaintenanceLog.Status.IN_PROGRESS,
                ]
            ).count()

        # EMPLOYEE

        else:

            active_assignments = AssetAssignment.objects.filter(
                employee=user,
                returned_at__isnull=True,
            )

            total_assets = active_assignments.count()

            available_assets = 0

            assigned_assets = active_assignments.count()

            repair_assets = Asset.objects.filter(
                assignments__employee=user,
                status=Asset.AssetStatus.UNDER_REPAIR,
            ).distinct().count()

            retired_assets = 0

            recent_assets = Asset.objects.filter(
                assignments__employee=user
            ).distinct().order_by("-created_at")[:5]

            recent_assignments = active_assignments.order_by(
                "-assigned_at"
            )[:5]

            open_tickets = Ticket.objects.filter(
                created_by=user,
                status__in=[
                    Ticket.Status.OPEN,
                    Ticket.Status.IN_PROGRESS,
                    Ticket.Status.AWAITING_USER,
                ]
            ).count()

            recent_tickets = Ticket.objects.filter(
                created_by=user
            ).order_by("-created_at")[:5]

            open_maintenance = None

        context = {

            "total_assets": total_assets,
            "is_staff_dashboard": user.is_staff_member,
            "available_assets": available_assets,
            "assigned_assets": assigned_assets,
            "repair_assets": repair_assets,
            "retired_assets": retired_assets,

            "recent_assets": recent_assets,
            "recent_assignments": recent_assignments,

            "open_tickets": open_tickets,
            "recent_tickets": recent_tickets,

            "open_maintenance": open_maintenance,
        }

        return render(
            request,
            self.template_name,
            context,
        )

class ReportsView(LoginRequiredMixin, TemplateView):

    template_name = "accounts/reports.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_assets"] = Asset.objects.count()

        context["available_assets"] = Asset.objects.filter(
            status=Asset.AssetStatus.AVAILABLE
        ).count()

        context["assigned_assets"] = Asset.objects.filter(
            status=Asset.AssetStatus.ASSIGNED
        ).count()

        context["repair_assets"] = Asset.objects.filter(
            status=Asset.AssetStatus.UNDER_REPAIR
        ).count()

        context["retired_assets"] = Asset.objects.filter(
            status=Asset.AssetStatus.RETIRED
        ).count()

        context["open_tickets"] = Ticket.objects.filter(
            status=Ticket.Status.OPEN
        ).count()

        context["in_progress_tickets"] = Ticket.objects.filter(
            status=Ticket.Status.IN_PROGRESS
        ).count()

        context["resolved_tickets"] = Ticket.objects.filter(
            status=Ticket.Status.RESOLVED
        ).count()

        context["closed_tickets"] = Ticket.objects.filter(
            status=Ticket.Status.CLOSED
        ).count()

        context["pending_maintenance"] = MaintenanceLog.objects.filter(
            status=MaintenanceLog.Status.PENDING
        ).count()

        context["active_maintenance"] = MaintenanceLog.objects.filter(
            status=MaintenanceLog.Status.IN_PROGRESS
        ).count()

        context["completed_maintenance"] = MaintenanceLog.objects.filter(
            status=MaintenanceLog.Status.COMPLETED
        ).count()

        context["asset_chart"] = [
            context["available_assets"],
            context["assigned_assets"],
            context["repair_assets"],
            context["retired_assets"],
        ]

        context["ticket_chart"] = [
            context["open_tickets"],
            context["in_progress_tickets"],
            context["resolved_tickets"],
            context["closed_tickets"],
        ]

        context["maintenance_chart"] = [
            context["pending_maintenance"],
            context["active_maintenance"],
            context["completed_maintenance"],
        ]

        return context


class ReportPDFView(View):

    def get(self, request):

        response = HttpResponse(
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            'attachment; filename="AMS_Report.pdf"'
        )

        p = canvas.Canvas(response)

        y = 800

        p.setFont("Helvetica-Bold", 18)
        p.drawString(
            50,
            y,
            "Asset Management Report"
        )

        y -= 50

        p.setFont("Helvetica", 12)

        p.drawString(
            50,
            y,
            f"Total Assets: {Asset.objects.count()}"
        )

        y -= 25

        p.drawString(
            50,
            y,
            f"Available Assets: {Asset.objects.filter(status='AVAILABLE').count()}"
        )

        y -= 25

        p.drawString(
            50,
            y,
            f"Assigned Assets: {Asset.objects.filter(status='ASSIGNED').count()}"
        )

        y -= 25

        p.drawString(
            50,
            y,
            f"Under Repair: {Asset.objects.filter(status='UNDER_REPAIR').count()}"
        )

        y -= 25

        p.drawString(
            50,
            y,
            f"Open Tickets: {Ticket.objects.filter(status='OPEN').count()}"
        )

        y -= 25

        p.drawString(
            50,
            y,
            f"Maintenance Logs: {MaintenanceLog.objects.count()}"
        )

        p.save()

        return response


class HomeView(View):

    template_name = "home.html"

    def get(self, request):

        if request.user.is_authenticated:
            return redirect("dashboard")

        return render(
            request,
            self.template_name,
        )