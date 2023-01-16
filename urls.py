from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import ProjectCreateView

app_name = "djupkeep"
urlpatterns = [
    path(
        _("project/add/"),
        ProjectCreateView.as_view(),
        name="project_create",
    ),
]
