from django.urls import path
from . import views

urlpatterns = [
    path("",                  views.TicketListView.as_view(),          name="ticket-list"),
    path("<int:pk>/",         views.TicketDetailView.as_view(),        name="ticket-detail"),
    path("create/",           views.TicketCreateView.as_view(),        name="ticket-create"),
    path("<int:pk>/edit/",    views.TicketUpdateView.as_view(),        name="ticket-update"),
    path("<int:pk>/delete/",  views.TicketDeleteView.as_view(),        name="ticket-delete"),
    path("<int:pk>/assign/",  views.TicketAssignView.as_view(),        name="ticket-assign"),
    path("<int:pk>/resolve/", views.TicketResolveView.as_view(),       name="ticket-resolve"),
    path("<int:pk>/close/",   views.TicketCloseView.as_view(),         name="ticket-close"),
    path("<int:pk>/comment/", views.TicketCommentCreateView.as_view(), name="ticket-comment-create"),
]