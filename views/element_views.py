from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (  # DetailView,; ListView,; ;
    CreateView,
    RedirectView,
    UpdateView,
)

from djupkeep.forms import ElementCreateForm, ElementUpdateForm
from djupkeep.models import Category, Element, Location

from .location_views import HxPageTemplateMixin


class ElementCreateView(PermissionRequiredMixin, HxPageTemplateMixin, CreateView):
    permission_required = "djupkeep.add_element"
    model = Element
    form_class = ElementCreateForm
    template_name = "djupkeep/elements/htmx/create.html"

    def get_initial(self):
        initial = super(ElementCreateView, self).get_initial()
        if "category" in self.request.GET:
            cat = get_object_or_404(Category, id=self.request.GET["category"])
            initial["category"] = cat.id
        elif "location" in self.request.GET:
            loc = get_object_or_404(Location, id=self.request.GET["location"])
            initial["location"] = loc.id
        return initial

    def get_success_url(self):
        return reverse("djupkeep:element_update", kwargs={"pk": self.object.id})


class ElementUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "djupkeep.change_element"
    model = Element
    form_class = ElementUpdateForm
    template_name = "djupkeep/elements/update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = self.object.location
        return context

    def get_success_url(self):
        return reverse(
            "djupkeep:location_detail", kwargs={"pk": self.object.location.id}
        )


class ElementDeleteView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.delete_element"

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        element = get_object_or_404(Element, id=self.kwargs["pk"])
        location = element.location
        element.delete()
        return reverse("djupkeep:location_detail", kwargs={"pk": location.id})
