from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import HomeView

urlpatterns = [
    path("admin/",admin.site.urls),
    path("", HomeView.as_view(),name="home"),
    path("", include("accounts.urls")),
    path("assets/", include("assets.urls")),
    path("tickets/", include("tickets.urls")),
    path("maintenance/", include("maintenance.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
