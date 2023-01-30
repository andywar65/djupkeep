from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

from djupkeep.forms import LocationCreateForm, LocationUpdateForm
from djupkeep.models import Location


class HxPageTemplateMixin:
    """Switches template depending on request.htmx"""

    def get_template_names(self):
        if not self.request.htmx:
            return [self.template_name.replace("htmx/", "")]
        return [self.template_name]


class LocationListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_location"
    model = Location
    context_object_name = "locations"
    template_name = "djupkeep/locations/htmx/list.html"


class LocationDetailView(PermissionRequiredMixin, HxPageTemplateMixin, DetailView):
    permission_required = "djupkeep.view_location"
    model = Location
    template_name = "djupkeep/locations/htmx/detail.html"


class LocationCreateView(PermissionRequiredMixin, HxPageTemplateMixin, CreateView):
    permission_required = "djupkeep.add_location"
    model = Location
    form_class = LocationCreateForm
    template_name = "djupkeep/locations/htmx/create.html"

    def get_success_url(self):
        return reverse("djupkeep:location_change", kwargs={"pk": self.object.id})


class LocationUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "djupkeep.change_location"
    model = Location
    form_class = LocationUpdateForm
    template_name = "djupkeep/locations/update.html"

    def get_success_url(self):
        return reverse("djupkeep:location_detail", kwargs={"pk": self.object.id})


class LocationDeleteView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.delete_location"

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        location = get_object_or_404(Location, id=self.kwargs["pk"])
        location.delete()
        return reverse("djupkeep:location_list")
