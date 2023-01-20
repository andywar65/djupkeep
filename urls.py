from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import ProjectCreateView, ProjectResetOriginView, ProjectUpdateView

app_name = "djupkeep"
urlpatterns = [
    path(
        _("location/add/"),
        ProjectCreateView.as_view(),
        name="project_create",
    ),
    path(
        _("location/<pk>/change/"),
        ProjectUpdateView.as_view(),
        name="project_change",
    ),
    path(
        _("location/<pk>/reset-origin/"),
        ProjectResetOriginView.as_view(),
        name="project_reset_origin",
    ),
]
