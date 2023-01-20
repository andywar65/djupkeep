from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin  # , LeafletGeoAdminMixin

from .models import Location


class LocationAdmin(LeafletGeoAdmin):
    list_display = ("title", "intro")
    exclude = ("image",)


admin.site.register(Location, LocationAdmin)
