from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from djupkeep.forms import CategoryCreateForm, IntroForm
from djupkeep.models import Category, Location

from .location_views import HxPageTemplateMixin


class HxOnlyTemplateMixin:
    """Restricts view to HTMX requests"""

    def get_template_names(self):
        if not self.request.htmx:
            raise Http404("Request without HTMX headers")
        else:
            return [self.template_name]


class IntroTemplateView(PermissionRequiredMixin, HxPageTemplateMixin, FormView):
    permission_required = "djupkeep.view_location"
    form_class = IntroForm
    template_name = "djupkeep/categories/htmx/intro.html"

    def form_valid(self, form):
        if not form.cleaned_data["target"]:
            raise Http404("No target selected")
        self.id = form.cleaned_data["target"].id
        return super(IntroTemplateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            "djupkeep:category_detail_related",
            kwargs={"pk": self.id},
        )


class CategoryListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_category"
    model = Category
    context_object_name = "categories"
    template_name = "djupkeep/categories/htmx/list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryListView, self).get_context_data()
        context["categories"] = context["categories"].with_tree_fields()
        return context


class CategoryListWrapperView(CategoryListView):
    """Subclasses CategoryListView with different template that adds a wrapper
    with an event catcher around the list. Called only by IntroTemplateView.
    View is restricted to HTMX requests"""

    template_name = "djupkeep/categories/htmx/list_wrapper.html"

    def get_template_names(self):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        else:
            return [self.template_name]


class CategoryCreateView(PermissionRequiredMixin, HxOnlyTemplateMixin, CreateView):
    permission_required = "djupkeep.add_category"
    model = Category
    form_class = CategoryCreateForm
    template_name = "djupkeep/categories/htmx/create.html"

    def form_valid(self, form):
        form.instance.position = form.instance.parent.children.count()
        return super(CategoryCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("djupkeep:category_add_button")


class CategoryCreateDismissView(HxOnlyTemplateMixin, TemplateView):
    template_name = "djupkeep/categories/htmx/create_button.html"

    def dispatch(self, request, *args, **kwargs):
        response = super(CategoryCreateDismissView, self).dispatch(
            request, *args, **kwargs
        )
        response["HX-Trigger-After-Swap"] = "refreshList"
        return response


class CategoryUpdateView(PermissionRequiredMixin, HxOnlyTemplateMixin, UpdateView):
    permission_required = "djupkeep.change_category"
    model = Category
    form_class = CategoryCreateForm
    context_object_name = "category"
    template_name = "djupkeep/categories/htmx/update.html"

    def setup(self, request, *args, **kwargs):
        super(CategoryUpdateView, self).setup(request, *args, **kwargs)
        self.original_parent = None

    def get_object(self, queryset=None):
        obj = super(CategoryUpdateView, self).get_object(queryset=None)
        self.original_parent = obj.parent
        return obj

    def form_valid(self, form):
        if not self.original_parent == form.instance.parent:
            if self.original_parent:
                self.original_parent.move_younger_children(form.instance.position)
            form.instance.position = form.instance.parent.children.count()
        return super(CategoryUpdateView, self).form_valid(form)

    def get_success_url(self):
        if not self.original_parent == self.object.parent:
            return reverse(
                "djupkeep:category_detail_refresh",
                kwargs={"pk": self.object.id},
            )
        return reverse(
            "djupkeep:category_detail",
            kwargs={"pk": self.object.id},
        )


class CategoryMoveDownView(PermissionRequiredMixin, HxOnlyTemplateMixin, RedirectView):
    permission_required = "djupkeep.change_category"

    def setup(self, request, *args, **kwargs):
        super(CategoryMoveDownView, self).setup(request, *args, **kwargs)
        cat = get_object_or_404(Category, id=self.kwargs["pk"])
        next = cat.get_next_sibling()
        if next:
            cat.position += 1
            cat.save()
            next.position -= 1
            next.save()

    def get_redirect_url(self, *args, **kwargs):
        return reverse("djupkeep:category_list")


class CategoryMoveUpView(PermissionRequiredMixin, HxOnlyTemplateMixin, RedirectView):
    permission_required = "djupkeep.change_category"

    def setup(self, request, *args, **kwargs):
        super(CategoryMoveUpView, self).setup(request, *args, **kwargs)
        cat = get_object_or_404(Category, id=self.kwargs["pk"])
        prev = cat.get_previous_sibling()
        if prev:
            cat.position -= 1
            cat.save()
            prev.position += 1
            prev.save()

    def get_redirect_url(self, *args, **kwargs):
        return reverse("djupkeep:category_list")


class CategoryDetailView(PermissionRequiredMixin, HxOnlyTemplateMixin, DetailView):
    permission_required = "djupkeep.view_category"
    model = Category
    context_object_name = "category"
    template_name = "djupkeep/categories/htmx/detail.html"


class CategoryDetailRefreshView(CategoryDetailView):
    """Subclasses CategoryDetailView but triggers event that refreshes
    category list"""

    def dispatch(self, request, *args, **kwargs):
        response = super(CategoryDetailRefreshView, self).dispatch(
            request, *args, **kwargs
        )
        response["HX-Trigger-After-Swap"] = "refreshList"
        return response


class CategoryDetailRelatedView(
    PermissionRequiredMixin, HxPageTemplateMixin, DetailView
):
    permission_required = "djupkeep.view_category"
    model = Category
    context_object_name = "category"
    template_name = "djupkeep/categories/htmx/detail_related.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryDetailRelatedView, self).get_context_data()
        context["locations"] = Location.objects.all()
        return context


class CategoryDetailActivityListView(
    PermissionRequiredMixin, HxPageTemplateMixin, DetailView
):
    permission_required = "djupkeep.view_category"
    model = Category
    context_object_name = "category"
    template_name = "djupkeep/activities/htmx/list.html"


class CategoryDeleteView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.delete_category"

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        category = get_object_or_404(Category, id=self.kwargs["pk"])
        if category.parent:
            category.parent.move_younger_children(category.position)
        category.delete()
        return reverse("djupkeep:category_list")
