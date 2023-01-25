from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import (
    LocationCreateView,
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
]
