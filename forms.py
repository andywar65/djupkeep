from django.forms import ModelForm
from leaflet.forms.widgets import LeafletWidget

from .models import Location


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


class LocationOriginHtmxForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image", "origin"]
        widgets = {
            "origin": LeafletWidget(
                attrs={
                    "geom_type": "Point",
                    "loadevent": "",
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


class LocationUnitHtmxForm(ModelForm):
    class Meta:
        model = Location
        fields = ["title", "intro", "image", "unit"]
        widgets = {
            "unit": LeafletWidget(
                attrs={
                    "geom_type": "Point",
                    "loadevent": "",
                }
            )
        }

    class Media:
        js = ("djupkeep/js/location_update.js",)
