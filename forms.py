from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm
from django.utils.translation import gettext_lazy as _
from leaflet.forms.widgets import LeafletWidget
from tree_queries.forms import TreeNodeChoiceField

from .models import Activity, Category, Element, Location, Task

User = get_user_model()


class LocationCreateForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "drawing", "image"]

    def clean(self):
        cleaned_data = super().clean()
        drw = cleaned_data.get("drawing")
        img = cleaned_data.get("image")

        if not drw and not img:
            # One of two fields must exist.
            raise ValidationError(
                _("You must insert Drawing (DXF) or Plan (image)"),
                code="no_drw_no_img",
            )


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


class ElementUpdateDrawingForm(ModelForm):
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
        js = ("djupkeep/js/element_update.js",)


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
        fields = (
            "notes",
            "image",
        )


class TaskBulkUpdateForm(forms.Form):
    user = ModelChoiceField(
        queryset=User.objects.filter(groups__name="Maintainer"),
        required=False,
    )


class MaintainerCreateForm(forms.Form):
    user = ModelChoiceField(
        queryset=User.objects.exclude(groups__name="Maintainer").exclude(
            is_superuser=True
        ),
        required=True,
    )


class MaintainerAssignForm(forms.Form):
    category = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label=_("Assign activities to maintainer by Category:"),
    )
