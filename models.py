from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from djgeojson.fields import PointField
from filebrowser.base import FileObject
from filebrowser.fields import FileBrowseField

User = get_user_model()


class Project(models.Model):

    title = models.CharField(
        _("Name"),
        help_text=_("Name of the project"),
        max_length=50,
    )
    intro = models.TextField(_("Description"), null=True)
    fb_image = FileBrowseField(
        _("Image"),
        max_length=200,
        extensions=[".jpg", ".png", ".jpeg", ".gif", ".tif", ".tiff"],
        directory="images/upkeep/",
        null=True,
    )
    image = models.ImageField(
        _("Image"),
        max_length=200,
        null=True,
        blank=True,
        upload_to="uploads/images/upkeep/",
    )
    origin = PointField(_("Origin of axis"), null=True)
    unit = PointField(_("Unit length"), null=True)

    __original_fb_image = None
    __original_origin = None
    __original_unit = None

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_fb_image = self.fb_image
        self.__original_origin = self.origin
        self.__original_unit = self.unit

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # save and eventually upload image file
        super(Project, self).save(*args, **kwargs)
        if self.image:
            # image is uploaded on the front end, passed to fb_image and deleted
            self.fb_image = FileObject(str(self.image))
            self.image = None
            super(Project, self).save(*args, **kwargs)
            # check_wide_image(self.fb_image)
