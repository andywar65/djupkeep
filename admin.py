from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin  # , LeafletGeoAdminMixin

from .models import Category, Location


class LocationAdmin(LeafletGeoAdmin):
    list_display = ("title", "intro")
    exclude = ("image",)


admin.site.register(Location, LocationAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "intro", "parent")
