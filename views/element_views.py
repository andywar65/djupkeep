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
from djeocad.models import Insertion

from djupkeep.forms import (
    ElementCreateForm,
    ElementUpdateDrawingForm,
    ElementUpdateForm,
)
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
    template_name = "djupkeep/elements/htmx/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.has_perm("djupkeep.add_task"):
            context["tasks"] = self.object.tasks.filter(
                check_date=None, maintainer_id=self.request.user.uuid
            )
            context["past_tasks"] = (
                self.object.tasks.filter(maintainer_id=self.request.user.uuid)
                .exclude(check_date=None)
                .order_by("-check_date")
            )
        else:
            context["tasks"] = self.object.tasks.filter(check_date=None)
            context["past_tasks"] = self.object.tasks.exclude(check_date=None).order_by(
                "-check_date"
            )
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
    template_name = "djupkeep/elements/create_located.html"

    def setup(self, request, *args, **kwargs):
        super(ElementCreateLocatedView, self).setup(request, *args, **kwargs)
        self.location = get_object_or_404(Location, id=self.kwargs["pk"])

    def get_initial(self):
        initial = super(ElementCreateLocatedView, self).get_initial()
        initial["location"] = self.location.id
        return initial

    def get_form_class(self):
        if self.location.drawing:
            return ElementUpdateDrawingForm
        return ElementUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = self.location
        if self.location.drawing:
            context["lines"] = self.location.drawing.related_layers.filter(
                is_block=False
            )
            id_list = context["lines"].values_list("id", flat=True)
            context["insertions"] = Insertion.objects.filter(layer_id__in=id_list)
        return context

    def get_success_url(self):
        return reverse(
            "djupkeep:location_detail", kwargs={"pk": self.object.location.id}
        )


class ElementCreateCategorizedView(PermissionRequiredMixin, CreateView):
    permission_required = "djupkeep.add_element"
    model = Element
    template_name = "djupkeep/elements/create_categorized.html"

    def setup(self, request, *args, **kwargs):
        super(ElementCreateCategorizedView, self).setup(request, *args, **kwargs)
        self.category = get_object_or_404(Category, id=self.kwargs["pk"])
        if "location" in self.request.GET:
            self.location = get_object_or_404(Location, id=self.request.GET["location"])

    def get_initial(self):
        initial = super(ElementCreateCategorizedView, self).get_initial()
        initial["category"] = self.category.id
        initial["location"] = self.location.id
        return initial

    def get_form_class(self):
        if self.location.drawing:
            return ElementUpdateDrawingForm
        return ElementUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["location"] = self.location
        if self.location.drawing:
            context["lines"] = self.location.drawing.related_layers.filter(
                is_block=False
            )
            id_list = context["lines"].values_list("id", flat=True)
            context["insertions"] = Insertion.objects.filter(layer_id__in=id_list)
        return context

    def get_success_url(self):
        if "add_another" in self.request.POST:
            return (
                reverse(
                    "djupkeep:element_create_categorized",
                    kwargs={"pk": self.category.id},
                )
                + f"?location={ self.location.id }"
            )
        return reverse(
            "djupkeep:category_detail_related", kwargs={"pk": self.category.id}
        )


class ElementUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "djupkeep.change_element"
    model = Element
    template_name = "djupkeep/elements/update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = self.object.location
        if self.object.location.drawing:
            context["lines"] = self.object.location.drawing.related_layers.filter(
                is_block=False
            )
            id_list = context["lines"].values_list("id", flat=True)
            context["insertions"] = Insertion.objects.filter(layer_id__in=id_list)
        return context

    def get_form_class(self):
        if self.object.location.drawing:
            return ElementUpdateDrawingForm
        return ElementUpdateForm

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
