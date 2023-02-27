from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from djupkeep.forms import TaskBulkUpdateForm, TaskCheckForm
from djupkeep.models import (
    Task,
    create_task_after_checked,
    create_tasks_and_generate_report,
    get_tasks_by_year_month,
)

from .category_views import HxOnlyTemplateMixin
from .location_views import HxPageTemplateMixin


class TaskListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_task"
    model = Task
    paginate_by = 20
    template_name = "djupkeep/tasks/htmx/list.html"

    def get_queryset(self):
        if "year" in self.request.GET:
            year = self.request.GET["year"]
            month = self.request.GET["month"]
            qs1 = Task.objects.filter(
                check_date=None, due_date__year=year, due_date__month=month
            ).prefetch_related("activity", "element", "maintainer")
            qs2 = (
                Task.objects.filter(
                    check_date__year=year, check_date__month=month, read=False
                )
                .exclude(notes="")
                .prefetch_related("activity", "element", "maintainer")
            )
        else:
            qs1 = Task.objects.filter(check_date=None).prefetch_related(
                "activity", "element", "maintainer"
            )
            qs2 = (
                Task.objects.filter(read=False)
                .exclude(notes="")
                .prefetch_related("activity", "element", "maintainer")
            )
        qs = qs1 | qs2
        if not self.request.user.has_perm("djupkeep.add_task"):
            qs.filter(maintainer_id=self.request.user.uuid)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "year" in self.request.GET:
            context["year"] = self.request.GET["year"]
            context["month"] = self.request.GET["month"]
        return context


class TaskListRefreshView(TaskListView, HxOnlyTemplateMixin):
    """This view is triggered when the list of tasks is changed.
    It subclasses TaskListView, replacing template and forcing use of HTMX"""

    template_name = "djupkeep/tasks/htmx/list_refresh.html"


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

    def get_object(self, queryset=None):
        obj = super(TaskCheckView, self).get_object(queryset=None)
        if (
            not obj.maintainer == self.request.user
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        form.instance.check_date = now()
        create_task_after_checked(self.object)
        return super(TaskCheckView, self).form_valid(form)

    def get_success_url(self):
        return reverse("djupkeep:task_detail", kwargs={"pk": self.object.id})


class TaskBulkUpdateView(PermissionRequiredMixin, HxOnlyTemplateMixin, FormView):
    permission_required = "djupkeep.change_task"
    form_class = TaskBulkUpdateForm
    template_name = "djupkeep/tasks/htmx/bulk_update.html"

    def get_success_url(self):
        return reverse("djupkeep:task_bulk_button")


class TaskBulkButtonView(HxOnlyTemplateMixin, TemplateView):
    template_name = "djupkeep/tasks/htmx/bulk_button.html"

    def dispatch(self, request, *args, **kwargs):
        response = super(TaskBulkButtonView, self).dispatch(request, *args, **kwargs)
        response["HX-Trigger-After-Swap"] = "refreshTaskList"
        return response


class TaskCalendarView(PermissionRequiredMixin, HxPageTemplateMixin, TemplateView):
    permission_required = "djupkeep.add_task"
    template_name = "djupkeep/tasks/htmx/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = get_tasks_by_year_month()
        return context


class TaskCalendarRefreshView(TaskCalendarView, HxOnlyTemplateMixin):
    """This view is triggered when the list of tasks is changed.
    It subclasses TaskCalendarView, replacing template and forcing use of HTMX"""

    template_name = "djupkeep/tasks/htmx/calendar_refresh.html"


class TaskReadDetailView(PermissionRequiredMixin, HxOnlyTemplateMixin, DetailView):
    permission_required = "djupkeep.change_task"
    model = Task
    context_object_name = "task"
    template_name = "djupkeep/tasks/htmx/list_row.html"

    def get_object(self, queryset=None):
        task = super(TaskReadDetailView, self).get_object(queryset=None)
        if task.notes == "":
            raise Http404("Task has no notes to read")
        task.read = True
        task.save()
        return task


class TaskDeleteView(PermissionRequiredMixin, HxOnlyTemplateMixin, TemplateView):
    permission_required = "djupkeep.delete_task"
    template_name = "djupkeep/tasks/htmx/list_row_deleted.html"

    def setup(self, request, *args, **kwargs):
        super(TaskDeleteView, self).setup(request, *args, **kwargs)
        task = get_object_or_404(Task, id=self.kwargs["pk"])
        task.delete()
