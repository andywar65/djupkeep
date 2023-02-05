from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (  # ; ; RedirectView,
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from djupkeep.forms import ElementCreateForm, ElementUpdateForm
from djupkeep.models import Category, Element, Location

from .location_views import HxPageTemplateMixin


class ElementListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_element"
    model = Element
    template_name = "djupkeep/elements/htmx/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by("category")
        return qs


class ElementDetailView(PermissionRequiredMixin, HxPageTemplateMixin, DetailView):
    permission_required = "djupkeep.view_element"
    model = Element
    template_name = "djupkeep/elements/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = self.object.location
        context["category_list"] = [_("Category - ") + self.object.category.title]
        return context


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
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["discard_url"] = reverse("djupkeep:element_list")
        if "category" in self.request.GET:
            context["discard_url"] = reverse("djupkeep:category_list")
        return context

    def get_success_url(self):
        return reverse("djupkeep:element_update", kwargs={"pk": self.object.id})


class ElementCreateLocatedView(PermissionRequiredMixin, CreateView):
    permission_required = "djupkeep.add_element"
    model = Element
    form_class = ElementUpdateForm
    template_name = "djupkeep/elements/create_located.html"

    def get_initial(self):
        initial = super(ElementCreateLocatedView, self).get_initial()
        self.location = get_object_or_404(Location, id=self.kwargs["pk"])
        initial["location"] = self.location.id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = self.location
        return context

    def get_success_url(self):
        return reverse(
            "djupkeep:location_detail", kwargs={"pk": self.object.location.id}
        )


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


class ElementDeleteView(PermissionRequiredMixin, DeleteView):
    model = Element
    permission_required = "djupkeep.delete_element"
    template_name = "djupkeep/elements/htmx/element_confirm_delete.html"

    def setup(self, request, *args, **kwargs):
        super(ElementDeleteView, self).setup(request, *args, **kwargs)
        if not request.htmx and not request.POST:
            raise Http404(_("Request without HTMX headers"))

    def get_success_url(self, *args, **kwargs):
        return reverse(
            "djupkeep:location_detail", kwargs={"pk": self.object.location.id}
        )
