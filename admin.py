from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin  # , LeafletGeoAdminMixin

from .models import Activity, Category, Element, Location, Task


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
    list_display = ("title", "category", "position")
    list_filter = ("category",)
    list_editable = ("position",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "element", "activity")
    list_filter = (
        "element",
        "activity",
    )
