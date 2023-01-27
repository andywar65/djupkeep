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
    TemplateView,
    UpdateView,
)

from djupkeep.forms import CategoryCreateForm
from djupkeep.models import Category

from .location_views import HxPageTemplateMixin


class HxOnlyTemplateMixin:
    """Restricts view to HTMX requests"""

    def get_template_names(self):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        else:
            return [self.template_name]


class CategoryListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_category"
    model = Category
    context_object_name = "categories"
    template_name = "djupkeep/categories/htmx/list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryListView, self).get_context_data()
        context["categories"] = context["categories"].with_tree_fields()
        return context


class CategoryCreateView(PermissionRequiredMixin, HxOnlyTemplateMixin, CreateView):
    permission_required = "djupkeep.add_category"
    model = Category
    form_class = CategoryCreateForm
    template_name = "djupkeep/categories/htmx/create.html"

    def get_success_url(self):
        return reverse("djupkeep:category_list")


class CategoryCreateDismissView(HxOnlyTemplateMixin, TemplateView):
    template_name = "djupkeep/categories/htmx/create_button.html"


class CategoryUpdateView(PermissionRequiredMixin, HxOnlyTemplateMixin, UpdateView):
    permission_required = "djupkeep.change_category"
    model = Category
    form_class = CategoryCreateForm
    context_object_name = "category"
    template_name = "djupkeep/categories/htmx/update.html"

    def setup(self, request, *args, **kwargs):
        super(CategoryUpdateView, self).setup(request, *args, **kwargs)
        self.retarget = False

    def dispatch(self, request, *args, **kwargs):
        response = super(CategoryUpdateView, self).dispatch(request, *args, **kwargs)
        if self.retarget:
            response["HX-Retarget"] = "#content"
        return response

    def get_success_url(self):
        self.retarget = True
        return reverse("djupkeep:category_list")


class CategoryUpdateDismissView(HxOnlyTemplateMixin, DetailView):
    model = Category
    context_object_name = "category"
    template_name = "djupkeep/categories/htmx/detail.html"


class CategoryDeleteView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.delete_category"

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        category = get_object_or_404(Category, id=self.kwargs["pk"])
        category.delete()
        return reverse("djupkeep:category_list")
