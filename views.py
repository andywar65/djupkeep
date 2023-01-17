from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from .forms import ProjectCreateForm, ProjectOriginForm
from .models import Project


class ProjectCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "djupkeep.add_project"
    model = Project
    form_class = ProjectCreateForm
    template_name = "djupkeep/project_create.html"

    def get_success_url(self):
        return reverse("djupkeep:project_change", kwargs={"pk": self.object.id})


class ProjectUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "djupkeep.change_project"
    model = Project

    def get_form_class(self):
        return ProjectOriginForm

    def get_template_names(self):
        return "djupkeep/project_origin.html"

    def get_success_url(self):
        return reverse("djupkeep:project_change", kwargs={"pk": self.object.id})
