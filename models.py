from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from djgeojson.fields import LineStringField, PointField
from filebrowser.base import FileObject
from filebrowser.fields import FileBrowseField
from tree_queries.models import TreeNode

User = get_user_model()


def get_default_origin():
    return dict(type="Point", coordinates=[0, 0])


def get_default_length_field():
    # legacy method, maybe I should smash some migrations
    return


class Location(models.Model):

    title = models.CharField(
        _("Name"),
        max_length=50,
    )
    intro = models.CharField(_("Description"), max_length=200, null=True)
    fb_image = FileBrowseField(
        _("Plan"),
        max_length=200,
        extensions=[".jpg", ".png", ".jpeg", ".gif", ".tif", ".tiff"],
        directory="images/upkeep/",
        null=True,
        help_text=_("Plan of your location"),
    )
    image = models.ImageField(
        _("Plan"),
        max_length=200,
        null=True,
        blank=True,
        upload_to="uploads/images/upkeep/",
        help_text=_("Plan of your location"),
    )
    origin = PointField(_("Origin of axis"), default=get_default_origin)
    length = LineStringField(
        _("Reference length on the map"),
        null=True,
        blank=True,
    )
    meters = models.FloatField(
        _("Reference length in meters"),
        default=1,
    )

    __original_length = None

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_length = self.length

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
        x = self.fb_image.width
        y = self.fb_image.height
        if x >= y * 2:
            return (180, 180 * y / x)
        return (90 * x / y, 90)

    def save(self, *args, **kwargs):
        # save and eventually upload image file
        super(Location, self).save(*args, **kwargs)
        if self.image:
            # image is uploaded on the front end, passed to fb_image and deleted
            self.fb_image = FileObject(str(self.image))
            self.image = None
            # image has changed, so we delete length and origin
            self.length = None
            self.origin = {"type": "Point", "coordinates": [0, 0]}
            super(Location, self).save(*args, **kwargs)
            # check_wide_image(self.fb_image)
        elif self.length and not self.__original_length == self.length:
            # length has changed, so we set origin...
            coords = [
                self.length["coordinates"][0][0] + self.origin["coordinates"][0],
                self.length["coordinates"][0][1] + self.origin["coordinates"][1],
            ]
            self.origin = {"type": "Point", "coordinates": coords}
            # and move length
            self.length["coordinates"][1] = [
                self.length["coordinates"][1][0] - self.length["coordinates"][0][0],
                self.length["coordinates"][1][1] - self.length["coordinates"][0][1],
            ]
            self.length["coordinates"][0] = [0, 0]
            super(Location, self).save(*args, **kwargs)


class Category(TreeNode):

    title = models.CharField(
        _("Name"),
        max_length=50,
    )
    intro = models.CharField(_("Description"), max_length=200, null=True)

    class Meta:
        verbose_name = _("Element category")
        verbose_name_plural = _("Element categories")

    def __str__(self):
        return self.title


class Element(models.Model):

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="elements",
        verbose_name=_("Location"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="elements",
        verbose_name=_("Category"),
    )
    intro = models.CharField(_("Description"), max_length=200, null=True)
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
    geom = PointField(_("Position"), null=True)

    class Meta:
        verbose_name = _("Element")
        verbose_name_plural = _("Elements")

    def __str__(self):
        return self.category.title + " - " + str(self.id)

    @property
    def popupContent(self):
        url = ""
        title_str = '<h5><a href="%(url)s">%(title)s</a></h5>' % {
            "title": self.__str__(),
            "url": url,
        }
        intro_str = "<small>%(intro)s</small>" % {"intro": self.intro}
        image = self.get_thumbnail_path()
        if not image:
            return {
                "content": title_str + intro_str,
                "layer": _("Category - ") + self.category.title,
            }
        image_str = '<img src="%(image)s">' % {"image": image}
        return {
            "content": title_str + image_str + intro_str,
            "layer": _("Category - ") + self.category.title,
        }

    def get_thumbnail_path(self):
        if not self.fb_image:
            return
        path = self.fb_image.version_generate("popup").path
        return settings.MEDIA_URL + path

    def save(self, *args, **kwargs):
        # save and eventually upload image file
        super(Element, self).save(*args, **kwargs)
        if self.image:
            # image is uploaded on the front end, passed to fb_image and deleted
            self.fb_image = FileObject(str(self.image))
            self.image = None
            super(Element, self).save(*args, **kwargs)
