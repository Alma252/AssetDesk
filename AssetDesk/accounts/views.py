from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from assets.models import Asset, AssetAssignment


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
        return render(request, self.template_name, {"user": request.user})


class DashboardView(LoginRequiredMixin, View):
    template_name = "accounts/dashboard.html"

    def get(self, request):

        context = {
            "user": request.user,

            "total_assets":
                Asset.objects.count(),

            "available_assets":
                Asset.objects.filter(
                    status=Asset.AssetStatus.AVAILABLE
                ).count(),

            "assigned_assets":
                Asset.objects.filter(
                    status=Asset.AssetStatus.ASSIGNED
                ).count(),

            "repair_assets":
                Asset.objects.filter(
                    status=Asset.AssetStatus.UNDER_REPAIR
                ).count(),

            "retired_assets":
                Asset.objects.filter(
                    status=Asset.AssetStatus.RETIRED
                ).count(),

            "recent_assets":
                Asset.objects.select_related(
                    "category",
                    "department"
                ).order_by("-created_at")[:5],

            "recent_assignments":
                AssetAssignment.objects.select_related(
                    "asset",
                    "employee"
                ).order_by("-assigned_at")[:5],
        }

        return render(
            request,
            self.template_name,
            context,
        )