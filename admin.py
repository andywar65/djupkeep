from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin  # , LeafletGeoAdminMixin

from .models import Project


class ProjectAdmin(LeafletGeoAdmin):
    list_display = ("title", "intro")
    exclude = ("image",)


admin.site.register(Project, ProjectAdmin)
