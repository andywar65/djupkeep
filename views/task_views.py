from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.http import Http404
# from django.shortcuts import get_object_or_404
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

# from djupkeep.forms import ActivityCreateForm  # ElementUpdateForm
from djupkeep.models import Task

# from .category_views import HxOnlyTemplateMixin
from .location_views import HxPageTemplateMixin


class TaskListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.view_task"
    model = Task
    template_name = "djupkeep/tasks/htmx/list.html"
