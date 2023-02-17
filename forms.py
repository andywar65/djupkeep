from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelChoiceField, ModelForm
from django.utils.translation import gettext_lazy as _
from leaflet.forms.widgets import LeafletWidget
from tree_queries.forms import TreeNodeChoiceField

from .models import Activity, Category, Element, Location, Task

User = get_user_model()


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


class IntroForm(forms.Form):
    target = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label=_("Maintenance procedures by Category:"),
    )


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
    class Meta:
        model = Activity
        exclude = (
            "category",
            "position",
        )


class TaskCheckForm(ModelForm):
    class Meta:
        model = Task
        fields = ("notes",)


class MaintainerCreateForm(forms.Form):
    user = ModelChoiceField(
        queryset=User.objects.exclude(groups__name=_("Maintainer")).exclude(
            is_superuser=True
        ),
        required=True,
    )
