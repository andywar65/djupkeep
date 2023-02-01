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
from djupkeep.models import Element

from .location_views import HxPageTemplateMixin


class ElementCreateView(PermissionRequiredMixin, HxPageTemplateMixin, CreateView):
    permission_required = "djupkeep.add_element"
    model = Element
    form_class = ElementCreateForm
    template_name = "djupkeep/elements/htmx/create.html"

    def get_success_url(self):
        return reverse("djupkeep:element_change", kwargs={"pk": self.object.id})


class ElementUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "djupkeep.change_element"
    model = Element
    form_class = ElementUpdateForm
    template_name = "djupkeep/elements/update.html"

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
