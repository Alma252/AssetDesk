from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from assets.models import Asset, AssetAssignment
from tickets.models import Ticket



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

        # =====================================================
        # STAFF
        # =====================================================

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

        # =====================================================
        # EMPLOYEE
        # =====================================================

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
        }

        return render(
            request,
            self.template_name,
            context,
        )