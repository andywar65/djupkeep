from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin  # , LeafletGeoAdminMixin

from .models import Activity, Category, Element, Location


class LocationAdmin(LeafletGeoAdmin):
    list_display = ("title", "intro")
    exclude = ("image", "origin")


admin.site.register(Location, LocationAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "parent", "position")
    list_filter = ("parent",)
    list_editable = ("position",)


class ElementAdmin(LeafletGeoAdmin):
    list_display = ("__str__", "intro", "location")
    exclude = ("image",)


admin.site.register(Element, ElementAdmin)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
