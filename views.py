from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from .forms import ProjectCreateForm, ProjectOriginForm, ProjectUnitForm
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
    form_class = ProjectCreateForm
    # temporary, we need a project_update.html
    template_name = "djupkeep/project_create.html"

    def get_form_class(self):
        if not self.object.origin:
            return ProjectOriginForm
        elif not self.object.unit:
            return ProjectUnitForm
        super(ProjectUpdateView, self).get_form_class()

    def get_template_names(self):
        if not self.object.origin:
            return "djupkeep/project_origin.html"
        elif not self.object.unit:
            return "djupkeep/project_unit.html"
        super(ProjectUpdateView, self).get_template_names()

    def get_success_url(self):
        if not self.object.origin or not self.object.unit:
            return reverse("djupkeep:project_change", kwargs={"pk": self.object.id})
        else:
            # temporary, we will revert to project detail
            return reverse("djupkeep:project_create")
