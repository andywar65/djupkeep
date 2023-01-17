from django.forms import ModelForm
from leaflet.forms.widgets import LeafletWidget

from .models import Project


class ProjectCreateForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "intro", "image"]


class ProjectOriginForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "intro", "image", "origin"]
        widgets = {
            "origin": LeafletWidget(
                attrs={
                    "geom_type": "Point",
                }
            )
        }
