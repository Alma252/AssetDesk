from django.urls import path
from . import views

urlpatterns = [
    path("login/",views.LoginView.as_view(),name="login"),
    path("logout/",views.LogoutView.as_view(),name="logout"),
    path("profile/",views.ProfileView.as_view(),name="profile"),
    path("dashboard/",views.DashboardView.as_view(), name="dashboard"),
    path("reports/",views.ReportsView.as_view(),name="reports"),
    path("reports/pdf/",views.ReportPDFView.as_view(),name="report-pdf"),
]