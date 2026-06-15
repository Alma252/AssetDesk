from django.urls import path
from . import views

urlpatterns = [
    # Asset CRUD
    path("",views.AssetListView.as_view(),name="asset-list"),
    path("<int:pk>/",views.AssetDetailView.as_view(),name="asset-detail"),
    path("create/",views.AssetCreateView.as_view(),name="asset-create"),
    path("<int:pk>/edit/",views.AssetUpdateView.as_view(),name="asset-update"),
    path("<int:pk>/delete/",views.AssetDeleteView.as_view(),name="asset-delete"),

    # Assignment
    path("<int:pk>/assign/",views.AssetAssignView.as_view(),  name="asset-assign"),
    path("assignment/<int:pk>/return/", views.AssetReturnView.as_view(), name="asset-return"),
]