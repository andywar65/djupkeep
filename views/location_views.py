from django.conf import settings
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
from djeocad.models import Insertion

from djupkeep.forms import LocationCreateForm, LocationUpdateForm
from djupkeep.models import Category, Location


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


class LocationDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "djupkeep.view_location"
    model = Location
    context_object_name = "location"
    template_name = "djupkeep/locations/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.drawing:
            context["mapbox_token"] = None
            if hasattr(settings, "MAPBOX_TOKEN"):
                context["mapbox_token"] = settings.MAPBOX_TOKEN
            context["lines"] = self.object.drawing.related_layers.filter(is_block=False)
            id_list = context["lines"].values_list("id", flat=True)
            context["insertions"] = Insertion.objects.filter(layer_id__in=id_list)
        context["elements"] = self.object.elements.all().prefetch_related("category")
        cat_list = context["elements"].values_list("category_id", flat=True)
        # TODO see if we can avoid next query as we use prefetch_related above
        categories = Category.objects.filter(id__in=cat_list)
        name_list = categories.values_list("title", flat=True)
        context["category_list"] = list(dict.fromkeys(name_list))
        return context


class LocationCreateView(PermissionRequiredMixin, HxPageTemplateMixin, CreateView):
    permission_required = "djupkeep.add_location"
    model = Location
    form_class = LocationCreateForm
    template_name = "djupkeep/locations/htmx/create.html"

    def get_success_url(self):
        if self.object.drawing:
            return reverse("djupkeep:location_detail", kwargs={"pk": self.object.id})
        return reverse("djupkeep:location_change", kwargs={"pk": self.object.id})


class LocationUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "djupkeep.change_location"
    model = Location
    context_object_name = "location"

    def get_form_class(self):
        if self.object.drawing:
            return LocationCreateForm
        return LocationUpdateForm

    def get_template_names(self):
        if self.object.drawing:
            return ["djupkeep/locations/update_drawing.html"]
        return ["djupkeep/locations/update.html"]

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
