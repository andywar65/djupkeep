from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from leaflet.forms.widgets import LeafletWidget
from tree_queries.forms import TreeNodeChoiceField

from .models import Activity, Category, Element, Location


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
        exclude = [
            "position",
        ]


class ElementCreateForm(ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Element
        fields = ["location", "category", "intro", "image"]


class ElementUpdateForm(ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Element
        fields = ["location", "category", "intro", "image", "geom"]
        labels = {"image": _("Upload / change image")}
        widgets = {
            "geom": LeafletWidget(
                attrs={
                    "geom_type": "Point",
                }
            )
        }

    class Media:
        js = ("djupkeep/js/location_update.js",)


class ActivityCreateForm(ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Activity
        fields = "__all__"
