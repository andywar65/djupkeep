from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, ListView, TemplateView

from djupkeep.forms import MaintainerCreateForm

from .category_views import HxOnlyTemplateMixin
from .location_views import HxPageTemplateMixin

User = get_user_model()


class MaintainerListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.change_task"
    model = User
    template_name = "djupkeep/maintainers/htmx/list.html"

    def get_queryset(self):
        qs = User.objects.filter(groups__name=_("Maintainer")).exclude(
            is_superuser=True
        )
        return qs


class MaintainerListRefreshView(PermissionRequiredMixin, HxOnlyTemplateMixin, ListView):
    permission_required = "djupkeep.change_task"
    model = User
    template_name = "djupkeep/maintainers/htmx/list_refresh.html"

    def get_queryset(self):
        qs = User.objects.filter(groups__name=_("Maintainer")).exclude(
            is_superuser=True
        )
        return qs


class MaintainerDeactivateView(MaintainerListRefreshView):
    def setup(self, request, *args, **kwargs):
        super(MaintainerDeactivateView, self).setup(request, *args, **kwargs)
        maint = get_object_or_404(User, id=kwargs["pk"])
        if maint.is_superuser:
            return
        elif not maint.groups.filter(name=_("Maintainer")).exists():
            return
        maint.is_active = False
        maint.save()


class MaintainerActivateView(MaintainerListRefreshView):
    def setup(self, request, *args, **kwargs):
        super(MaintainerActivateView, self).setup(request, *args, **kwargs)
        maint = get_object_or_404(User, id=kwargs["pk"])
        if maint.is_superuser:
            return
        elif not maint.groups.filter(name=_("Maintainer")).exists():
            return
        maint.is_active = True
        maint.save()


class MaintainerAddButtonView(
    PermissionRequiredMixin, HxOnlyTemplateMixin, TemplateView
):
    permission_required = "djupkeep.change_task"
    template_name = "djupkeep/maintainers/htmx/add_button.html"

    def dispatch(self, request, *args, **kwargs):
        response = super(MaintainerAddButtonView, self).dispatch(
            request, *args, **kwargs
        )
        response["HX-Trigger-After-Swap"] = "refreshMaintainerList"
        return response


class MaintainerCreateView(PermissionRequiredMixin, HxOnlyTemplateMixin, FormView):
    permission_required = "djupkeep.change_task"
    form_class = MaintainerCreateForm
    template_name = "djupkeep/maintainers/htmx/create.html"

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        grp = Group.objects.get(name=_("Maintainer"))
        grp.user_set.add(user)
        return super(MaintainerCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("djupkeep:maintainer_add_button")
