from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse

# from django.utils.translation import gettext_lazy as _
# DetailView,; ListView,; RedirectView,; DeleteView,; UpdateView,
from django.views.generic import CreateView

from djupkeep.forms import ActivityCreateForm  # ElementUpdateForm
from djupkeep.models import Activity, Category

from .location_views import HxPageTemplateMixin


class ActivityCreateView(PermissionRequiredMixin, HxPageTemplateMixin, CreateView):
    permission_required = "djupkeep.add_activity"
    model = Activity
    form_class = ActivityCreateForm
    template_name = "djupkeep/activities/htmx/create.html"

    def get_initial(self):
        initial = super(ActivityCreateView, self).get_initial()
        self.category = get_object_or_404(Category, id=self.kwargs["pk"])
        initial["category"] = self.category.id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # we can use this to redirect to different pages
        context["discard_url"] = reverse("djupkeep:category_list")
        return context

    def get_success_url(self):
        return reverse("djupkeep:category_list")
