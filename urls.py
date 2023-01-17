from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import ProjectCreateView, ProjectUpdateView

app_name = "djupkeep"
urlpatterns = [
    path(
        _("project/add/"),
        ProjectCreateView.as_view(),
        name="project_create",
    ),
    path(
        _("project/<pk>/change/"),
        ProjectUpdateView.as_view(),
        name="project_change",
    ),
]
