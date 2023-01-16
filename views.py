from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView

from .forms import ProjectCreateForm
from .models import Project


class ProjectCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "djupkeep.add_project"
    model = Project
    form_class = ProjectCreateForm
    template_name = "djupkeep/project_create.html"

    def get_success_url(self):
        return reverse("djupkeep:project_create")
