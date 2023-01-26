from django.forms import ModelForm
from leaflet.forms.widgets import LeafletWidget
from tree_queries.forms import TreeNodeChoiceField

from .models import Category, Location


class LocationCreateForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image"]


class LocationOriginForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image", "origin"]
        widgets = {
            "origin": LeafletWidget(
                attrs={
                    "geom_type": "Point",
                }
            )
        }

    class Media:
        js = ("djupkeep/js/location_update.js",)


class LocationUnitForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image", "unit"]
        widgets = {
            "unit": LeafletWidget(
                attrs={
                    "geom_type": "Point",
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
