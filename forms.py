from django.forms import ModelForm
from leaflet.forms.widgets import LeafletWidget
from tree_queries.forms import TreeNodeChoiceField

from .models import Category, Location


class LocationCreateForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image"]


class LocationUpdateForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image", "meters", "length"]
        widgets = {
            "length": LeafletWidget(
                attrs={
                    "geom_type": "LineString",
                }
            )
        }

    class Media:
        js = ("djupkeep/js/location_update.js",)


class CategoryCreateForm(ModelForm):
    parent = TreeNodeChoiceField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Category
        fields = "__all__"
