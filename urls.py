from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views.category_views import CategoryCreateView, CategoryListView
from .views.location_views import (
    LocationCreateView,
    LocationDeleteView,
    LocationDetailView,
    LocationListView,
    LocationResetOriginView,
    LocationUpdateView,
)

app_name = "djupkeep"
urlpatterns = [
    path(
        _("location/list/"),
        LocationListView.as_view(),
        name="location_list",
    ),
    path(
        _("location/add/"),
        LocationCreateView.as_view(),
        name="location_create",
    ),
    path(
        _("location/<pk>/"),
        LocationDetailView.as_view(),
        name="location_detail",
    ),
    path(
        _("location/<pk>/change/"),
        LocationUpdateView.as_view(),
        name="location_change",
    ),
    path(
        _("location/<pk>/reset-origin/"),
        LocationResetOriginView.as_view(),
        name="location_reset_origin",
    ),
    path(
        _("location/<pk>/delete/"),
        LocationDeleteView.as_view(),
        name="location_delete",
    ),
    path(
        _("category/list/"),
        CategoryListView.as_view(),
        name="category_list",
    ),
    path(
        _("category/add/"),
        CategoryCreateView.as_view(),
        name="category_create",
    ),
]
