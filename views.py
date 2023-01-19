from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, RedirectView, UpdateView

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

    def get_form_class(self):
        if not self.object.origin:
            return ProjectOriginForm
        return ProjectUnitForm

    def get_template_names(self):
        if not self.object.origin:
            return "djupkeep/project_origin.html"
        elif not self.object.unit:
            return "djupkeep/project_unit.html"
        return "djupkeep/project_update.html"

    def get_success_url(self):
        if not self.object.origin:
            return reverse("djupkeep:project_change", kwargs={"pk": self.object.id})
        else:
            # temporary, we will revert to project detail
            return reverse("djupkeep:project_change", kwargs={"pk": self.object.id})


class ProjectResetOriginView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.change_project"

    def setup(self, request, *args, **kwargs):
        super(ProjectResetOriginView, self).setup(request, *args, **kwargs)
        self.object = get_object_or_404(Project, id=self.kwargs["pk"])
        self.object.origin = None
        self.object.save()

    def get_redirect_url(self, *args, **kwargs):
        return reverse("djupkeep:project_change", kwargs={"pk": self.object.id})
