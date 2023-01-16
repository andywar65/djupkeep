from django.forms import ModelForm

from .models import Project


class ProjectCreateForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "intro", "image"]
