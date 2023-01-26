from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from djupkeep.models import Category

from .location_views import HxPageTemplateMixin


class CategoryListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_category"
    model = Category
    context_object_name = "categories"
    template_name = "djupkeep/categories/htmx/list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryListView, self).get_context_data()
        context["categories"] = context["categories"].with_tree_fields()
        return context
