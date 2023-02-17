from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from djupkeep.forms import TaskCheckForm
from djupkeep.models import (
    Task,
    create_task_after_checked,
    create_tasks_and_generate_report,
)

from .category_views import HxOnlyTemplateMixin
from .location_views import HxPageTemplateMixin


class TaskListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_task"
    model = Task
    template_name = "djupkeep/tasks/htmx/list.html"

    def get_queryset(self):
        qs = Task.objects.filter(Q(check_date=None) | ~Q(notes=""))
        return qs


class TaskListRefreshView(PermissionRequiredMixin, HxOnlyTemplateMixin, ListView):
    """This view is triggered when the list of tasks is changed"""

    permission_required = "djupkeep.view_task"
    model = Task
    template_name = "djupkeep/tasks/htmx/list_refresh.html"

    def get_queryset(self):
        qs = Task.objects.filter(Q(check_date=None) | ~Q(notes=""))
        return qs


class TaskCreateView(PermissionRequiredMixin, HxOnlyTemplateMixin, TemplateView):
    """Automatically creates tasks, generates a report and triggers list refresh"""

    permission_required = "djupkeep.add_task"
    template_name = "djupkeep/tasks/htmx/report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = create_tasks_and_generate_report()
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super(TaskCreateView, self).dispatch(request, *args, **kwargs)
        response["HX-Trigger-After-Swap"] = "refreshTaskList"
        return response


class TaskDetailView(PermissionRequiredMixin, HxOnlyTemplateMixin, DetailView):
    permission_required = "djupkeep.view_task"
    model = Task
    context_object_name = "task"
    template_name = "djupkeep/tasks/htmx/detail.html"


class TaskCheckView(PermissionRequiredMixin, HxOnlyTemplateMixin, UpdateView):
    permission_required = "djupkeep.check_task"
    model = Task
    form_class = TaskCheckForm
    template_name = "djupkeep/tasks/htmx/check.html"

    def form_valid(self, form):
        form.instance.check_date = now()
        create_task_after_checked(self.object)
        return super(TaskCheckView, self).form_valid(form)

    def get_success_url(self):
        return reverse("djupkeep:task_detail", kwargs={"pk": self.object.id})
