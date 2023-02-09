from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse

# from django.utils.translation import gettext_lazy as _
# DetailView,; ListView,; RedirectView,; DeleteView,; UpdateView,
from django.views.generic import CreateView, TemplateView

from djupkeep.forms import ActivityCreateForm  # ElementUpdateForm
from djupkeep.models import Activity, Category

from .category_views import HxOnlyTemplateMixin


class ActivityCreateView(PermissionRequiredMixin, HxOnlyTemplateMixin, CreateView):
    permission_required = "djupkeep.add_activity"
    model = Activity
    form_class = ActivityCreateForm
    template_name = "djupkeep/activities/htmx/create.html"

    def setup(self, request, *args, **kwargs):
        super(ActivityCreateView, self).setup(request, *args, **kwargs)
        self.category = get_object_or_404(Category, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context

    def form_valid(self, form):
        form.instance.category = self.category
        return super(ActivityCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("djupkeep:activity_list", kwargs={"pk": self.category.id})


class ActivityCreateDismissView(HxOnlyTemplateMixin, TemplateView):
    template_name = "djupkeep/activities/htmx/create_button.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, id=self.kwargs["pk"])
        return context
