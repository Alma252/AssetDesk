# maintenance/urls.py

from django.urls import path
from . import views

urlpatterns = [

    path("logs/",  views.MaintenanceLogListView.as_view(),name="maintenance-log-list"),
    path("logs/<int:pk>/",   views.MaintenanceLogDetailView.as_view(),name="maintenance-log-detail"),
    path("logs/create/",  views.MaintenanceLogCreateView.as_view(), name="maintenance-log-create"),
    path("logs/<int:pk>/edit/",  views.MaintenanceLogUpdateView.as_view(), name="maintenance-log-update"),
    path("logs/<int:pk>/delete/", views.MaintenanceLogDeleteView.as_view(), name="maintenance-log-delete"),
    path("logs/<int:pk>/complete/", views.MaintenanceLogCompleteView.as_view(), name="maintenance-log-complete"),

    path("schedules/",views.MaintenanceScheduleListView.as_view(),   name="maintenance-schedule-list"),
    path("schedules/create/",  views.MaintenanceScheduleCreateView.as_view(), name="maintenance-schedule-create"),
    path("schedules/<int:pk>/edit/", views.MaintenanceScheduleUpdateView.as_view(), name="maintenance-schedule-update"),
    path("schedules/<int:pk>/delete/",views.MaintenanceScheduleDeleteView.as_view(), name="maintenance-schedule-delete"),
]