from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

from djupkeep.forms import LocationCreateForm, LocationOriginForm, LocationUnitForm
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

    def get_form_class(self):
        if not self.object.origin:
            return LocationOriginForm
        return LocationUnitForm

    def get_template_names(self):
        name = "djupkeep/locations/update.html"
        if not self.object.origin:
            name = "djupkeep/locations/update_origin.html"
        elif not self.object.unit:
            name = "djupkeep/locations/update_unit.html"
        return [name]

    def get_success_url(self):
        if not self.object.origin or not self.object.unit:
            return reverse("djupkeep:location_change", kwargs={"pk": self.object.id})
        else:
            return reverse("djupkeep:location_detail", kwargs={"pk": self.object.id})


class LocationResetOriginView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.change_location"

    def setup(self, request, *args, **kwargs):
        super(LocationResetOriginView, self).setup(request, *args, **kwargs)
        self.object = get_object_or_404(Location, id=self.kwargs["pk"])
        self.object.origin = None
        self.object.save()

    def get_redirect_url(self, *args, **kwargs):
        return reverse("djupkeep:location_change", kwargs={"pk": self.object.id})
