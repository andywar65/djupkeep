from datetime import timedelta
from math import pow, sqrt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from djeocad.models import Drawing
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
    drawing = models.ForeignKey(
        Drawing,
        on_delete=models.SET_NULL,
        related_name="locations",
        verbose_name=_("Drawing"),
        null=True,
        blank=True,
    )
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
    __original_meters = None

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_length = self.length
        self.__original_meters = self.meters

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

    def update_element_position(self):
        length = sqrt(
            pow(self.__original_length["coordinates"][1][0], 2)
            + pow(self.__original_length["coordinates"][1][1], 2)
        )
        original_scale = self.__original_meters / length
        length = sqrt(
            pow(self.length["coordinates"][1][0], 2)
            + pow(self.length["coordinates"][1][1], 2)
        )
        scale = self.meters / length
        for e in self.elements.all():
            e.geom["coordinates"][0] = e.geom["coordinates"][0] * original_scale / scale
            e.geom["coordinates"][1] = e.geom["coordinates"][1] * original_scale / scale
            super(Element, e).save()

    def save(self, *args, **kwargs):
        # save and eventually upload image file
        super(Location, self).save(*args, **kwargs)
        if self.image:
            # image is uploaded on the front end, passed to fb_image and deleted
            self.fb_image = FileObject(str(self.image))
            self.image = None
            super(Location, self).save(*args, **kwargs)
            # TODO check_wide_image(self.fb_image)
        if self.length and not self.__original_length == self.length:
            # length has changed, so we set origin...
            coords = [
                self.length["coordinates"][0][0] + self.origin["coordinates"][0],
                self.length["coordinates"][0][1] + self.origin["coordinates"][1],
            ]
            self.origin = {"type": "Point", "coordinates": coords}
            # ... move length ...
            self.length["coordinates"][1] = [
                self.length["coordinates"][1][0] - self.length["coordinates"][0][0],
                self.length["coordinates"][1][1] - self.length["coordinates"][0][1],
            ]
            self.length["coordinates"][0] = [0, 0]
            # ... save new values ...
            super(Location, self).save(*args, **kwargs)
            # ... and eventually update attached elements.
            if self.elements.exists():
                self.update_element_position()
        # if previous conditional was skipped, eventually update attached elements
        elif not self.__original_meters == self.meters and self.elements.exists():
            self.update_element_position()


class Category(TreeNode):

    title = models.CharField(
        _("Name"),
        max_length=50,
    )
    intro = models.CharField(_("Description"), max_length=200, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["position"]

    def __str__(self):
        return self.title

    def move_activities(self, pos):
        """Used when a related activity is deleted.
        Activities with greater position than given (pos) are
        moved up the ladder.
        """
        siblings = self.activities.filter(position__gt=pos)
        for sibling in siblings:
            sibling.position -= 1
            sibling.save()

    def move_younger_children(self, pos):
        """Used when a child is moved to other parent or deleted.
        Children with greater position than child (pos) are
        moved up the ladder.
        """
        siblings = self.children.filter(position__gt=pos)
        for sibling in siblings:
            sibling.position -= 1
            sibling.save()

    def get_next_sibling(self):
        if not self.parent:
            return None
        try:
            next = Category.objects.get(
                parent_id=self.parent.id, position=self.position + 1
            )
            return next
        except Category.DoesNotExist:
            return None

    def get_previous_sibling(self):
        if self.position == 0 or not self.parent:
            return None
        try:
            prev = Category.objects.get(
                parent_id=self.parent.id, position=self.position - 1
            )
            return prev
        except Category.DoesNotExist:
            return None

    def get_punctuated_index(self):
        qs = self.ancestors(include_self=True).with_tree_fields()
        int_list = qs.values_list("position", flat=True)
        str_list = list(map(str, int_list))
        return ".".join(str_list)

    def assign_activity_to(self, maintainer):
        number = 0
        descendants = self.descendants(include_self=True)
        cat_list = descendants.values_list("id", flat=True)
        elements = Element.objects.filter(category_id__in=cat_list)
        for elm in elements:
            tasks = elm.tasks.filter(check_date=None).exclude(
                maintainer_id=maintainer.uuid
            )
            number += tasks.update(maintainer=maintainer)
        return _("Assigned %(number)s task(s)") % {"number": str(number)}

    def has_ancestor_with_activities(self):
        ancestors = self.ancestors()
        for ancestor in ancestors:
            if ancestor.activities.filter(extend=True).exists():
                return True
        return False


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
        url = reverse("djupkeep:element_detail", kwargs={"pk": self.id})
        title_str = '<h5><a href="%(url)s">%(title)s</a></h5>' % {
            "title": self.__str__(),
            "url": url,
        }
        intro_str = "<small>%(intro)s</small>" % {"intro": self.intro}
        image = self.get_thumbnail_path()
        if not image:
            return {
                "content": title_str + intro_str,
                "layer": self.category.title,
            }
        image_str = '<img src="%(image)s">' % {"image": image}
        return {
            "content": title_str + image_str + intro_str,
            "layer": self.category.title,
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


class Activity(models.Model):

    FREQUENCY = [
        ("7", _("Weekly")),
        ("30", _("Monthly")),
        ("60", _("Bimonthly")),
        ("90", _("Quarterly")),
        ("120", _("Four-monthly")),
        ("183", _("Biannual")),
        ("365", _("Annual")),
        ("730", _("Every two years")),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name=_("Category"),
    )
    title = models.CharField(
        _("Name"),
        max_length=50,
    )
    intro = models.TextField(_("Description"), null=True)
    position = models.PositiveIntegerField(default=0)
    frequency = models.CharField(
        max_length=3,
        choices=FREQUENCY,
        default="30",
    )
    extend = models.BooleanField(_("Apply to subcategories only"), default=False)

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ["category", "position"]

    def __str__(self):
        return self.title

    def get_next_sibling(self):
        try:
            next = Activity.objects.get(
                category_id=self.category.id, position=self.position + 1
            )
            return next
        except Activity.DoesNotExist:
            return None

    def get_previous_sibling(self):
        try:
            prev = Activity.objects.get(
                category_id=self.category.id, position=self.position - 1
            )
            return prev
        except Activity.DoesNotExist:
            return None


class Task(models.Model):

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("Activity"),
    )
    element = models.ForeignKey(
        Element,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("Element"),
    )
    maintainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name=_("Maintainer"),
        null=True,
        blank=True,
    )
    due_date = models.DateField(_("Due date"), null=True)
    check_date = models.DateTimeField(_("Check date"), null=True, blank=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)
    read = models.BooleanField(_("Notes have been read"), default=False)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = [
            "due_date",
        ]
        permissions = [
            ("check_task", _("Can perform activity tasks on elements")),
        ]

    def __str__(self):
        return _("Task") + " - " + str(self.id)

    def due_date_color(self):
        if self.due_date < now().date():
            return "red"
        if self.due_date < (now() + timedelta(days=7)).date():
            return "green"
        return None

    def due_date_in_days(self):
        if self.due_date < now().date():
            days = now().date() - self.due_date
            return _("Check was due %(days)s day(s) ago!") % {"days": str(days.days)}
        days = self.due_date - now().date()
        return _("Check is due in %(days)s day(s)") % {"days": str(days.days)}

    def alert_color(self):
        if self.notes:
            return "warning"
        elif self.check_date:
            return "success"
        elif self.due_date < now().date():
            return "danger"
        return "secondary"


def create_tasks_and_generate_report():
    # first check for inconsistent tasks (maybe we moved some categories)
    inconsistent = 0
    for task in Task.objects.filter(check_date=None).prefetch_related(
        "element", "activity"
    ):
        # most common case, get rid of it immediately
        if not task.activity.extend:
            if task.element.category == task.activity.category:
                continue
        # the activity is extended to category descendants
        else:
            descendants = task.activity.category.descendants()
            cat_list = descendants.values_list("id", flat=True)
            if task.element.category.id in cat_list:
                continue
        # task is inconsistent, we delete it
        task.delete()
        inconsistent += 1
    # now let's generate consistent tasks
    number = 0
    for act in Activity.objects.all().prefetch_related("category"):
        if not act.extend:
            elements = Element.objects.filter(category_id=act.category.id)
        else:
            descendants = act.category.descendants()
            cat_list = descendants.values_list("id", flat=True)
            elements = Element.objects.filter(category_id__in=cat_list)
        for elm in elements:
            try:
                Task.objects.get(activity_id=act.id, element_id=elm.id, check_date=None)
            except Task.DoesNotExist:
                task = Task()
                task.activity = act
                task.element = elm
                task.due_date = now() + timedelta(days=int(act.frequency))
                task.save()
                number += 1
    return _(
        "Generated %(number)s task(s). Deleted %(inconsistent)s inconsistent task(s)."
    ) % {"number": str(number), "inconsistent": str(inconsistent)}


def create_task_after_checked(checked):
    task = Task()
    task.activity = checked.activity
    task.element = checked.element
    task.maintainer = checked.maintainer
    task.due_date = now() + timedelta(days=int(checked.activity.frequency))
    task.save()


def get_tasks_by_year_month():
    year = now().year
    month = now().month
    years = []
    all_tasks = Task.objects.all()
    for y in range(year - 1, year + 2):
        months = []
        for m in range(1, 13):
            warning = False
            current = False
            due_tasks = all_tasks.filter(
                due_date__year=y, due_date__month=m, check_date=None
            )
            checked = all_tasks.filter(check_date__year=y, check_date__month=m).exclude(
                notes=""
            )
            if not warning and due_tasks.filter(due_date__lt=now().date()).exists():
                warning = True
            if not warning and checked.exists():
                warning = True
            if y == year and m == month:
                current = True
            months.append(
                {
                    "number": due_tasks.count() + checked.count(),
                    "warning": warning,
                    "current": current,
                }
            )
        years.append({"year": y, "months": months})
    return years
