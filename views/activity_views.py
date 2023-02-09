from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from djupkeep.forms import ActivityCreateForm  # ElementUpdateForm
from djupkeep.models import Activity, Category

from .category_views import HxOnlyTemplateMixin


class ActivityCreateView(PermissionRequiredMixin, HxOnlyTemplateMixin, CreateView):
    permission_required = "djupkeep.add_activity"
    model = Activity
    form_class = ActivityCreateForm
    template_name = "djupkeep/activities/htmx/create.html"

    def setup(self, request, *args, **kwargs):
        super(ActivityCreateView, self).setup(request, *args, **kwargs)
        self.category = get_object_or_404(Category, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context

    def form_valid(self, form):
        form.instance.category = self.category
        form.instance.position = self.category.activities.count()
        return super(ActivityCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("djupkeep:activity_list", kwargs={"pk": self.category.id})


class ActivityCreateDismissView(HxOnlyTemplateMixin, TemplateView):
    template_name = "djupkeep/activities/htmx/create_button.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, id=self.kwargs["pk"])
        return context


class ActivityDetailView(HxOnlyTemplateMixin, DetailView):
    permission_required = "djupkeep.view_activity"
    model = Activity
    context_object_name = "activity"
    template_name = "djupkeep/activities/htmx/detail.html"


class ActivityUpdateView(PermissionRequiredMixin, HxOnlyTemplateMixin, UpdateView):
    permission_required = "djupkeep.change_activity"
    model = Activity
    form_class = ActivityCreateForm
    context_object_name = "activity"
    template_name = "djupkeep/activities/htmx/update.html"

    def get_success_url(self):
        return reverse(
            "djupkeep:activity_detail",
            kwargs={"pk": self.object.id},
        )


class ActivityMoveDownView(PermissionRequiredMixin, HxOnlyTemplateMixin, RedirectView):
    permission_required = "djupkeep.change_activity"

    def setup(self, request, *args, **kwargs):
        super(ActivityMoveDownView, self).setup(request, *args, **kwargs)
        self.object = get_object_or_404(Activity, id=self.kwargs["pk"])
        next = self.object.get_next_sibling()
        if next:
            self.object.position += 1
            self.object.save()
            next.position -= 1
            next.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.object.category
        return context

    def get_redirect_url(self, *args, **kwargs):
        return reverse("djupkeep:activity_list", kwargs={"pk": self.object.category.id})


class ActivityMoveUpView(PermissionRequiredMixin, HxOnlyTemplateMixin, RedirectView):
    permission_required = "djupkeep.change_activity"

    def setup(self, request, *args, **kwargs):
        super(ActivityMoveUpView, self).setup(request, *args, **kwargs)
        self.object = get_object_or_404(Activity, id=self.kwargs["pk"])
        prev = self.object.get_previous_sibling()
        if prev:
            self.object.position -= 1
            self.object.save()
            prev.position += 1
            prev.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.object.category
        return context

    def get_redirect_url(self, *args, **kwargs):
        return reverse("djupkeep:activity_list", kwargs={"pk": self.object.category.id})


class ActivityDeleteView(PermissionRequiredMixin, RedirectView):
    permission_required = "djupkeep.delete_activity"

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.htmx:
            raise Http404(_("Request without HTMX headers"))
        activity = get_object_or_404(Activity, id=self.kwargs["pk"])
        category = activity.category
        category.move_activities(activity.position)
        activity.delete()
        return reverse("djupkeep:activity_list", kwargs={"pk": category.id})
