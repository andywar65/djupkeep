from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _

# from django.urls import reverse
from django.views.generic import ListView

# from djupkeep.forms import TaskCheckForm
# from djupkeep.models import
# from .category_views import HxOnlyTemplateMixin
from .location_views import HxPageTemplateMixin

User = get_user_model()


class MaintainerListView(PermissionRequiredMixin, HxPageTemplateMixin, ListView):
    permission_required = "djupkeep.change_task"
    model = User
    template_name = "djupkeep/maintainers/htmx/list.html"

    def get_queryset(self):
        qs = User.objects.filter(groups__name=_("Maintainer"))
        return qs
