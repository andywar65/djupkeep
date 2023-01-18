from django.conf import settings
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
        max_length=50,
    )
    intro = models.TextField(_("Description"), null=True)
    fb_image = FileBrowseField(
        _("Plan"),
        max_length=200,
        extensions=[".jpg", ".png", ".jpeg", ".gif", ".tif", ".tiff"],
        directory="images/upkeep/",
        null=True,
        help_text=_("Plan of your project"),
    )
    image = models.ImageField(
        _("Plan"),
        max_length=200,
        null=True,
        blank=True,
        upload_to="uploads/images/upkeep/",
        help_text=_("Plan of your project"),
    )
    origin = PointField(_("Origin of axis"), null=True)
    unit = PointField(_("Unit length"), null=True)

    __original_origin = None

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_origin = self.origin

    def __str__(self):
        return self.title

    def get_image_path(self):
        if not self.fb_image:
            return
        path = self.fb_image.path
        return settings.MEDIA_URL + path

    def get_image_size(self):
        if not self.fb_image:
            return
        y = self.fb_image.height
        x = self.fb_image.width
        if x >= y * 2:
            return (180 * y / x, 180)
        return (90, 90 * x / y)

    def save(self, *args, **kwargs):
        # save and eventually upload image file
        super(Project, self).save(*args, **kwargs)
        if self.image:
            # image is uploaded on the front end, passed to fb_image and deleted
            self.fb_image = FileObject(str(self.image))
            self.image = None
            # image has changed, so we delete origin and unit
            self.origin = None
            self.unit = None
            super(Project, self).save(*args, **kwargs)
            # check_wide_image(self.fb_image)
        if not self.__original_origin == self.origin:
            # origin has changed, so we delete unit
            self.unit = None
            super(Project, self).save(*args, **kwargs)
