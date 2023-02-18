from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext as _


def create_djupkeep_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    types = ContentType.objects.filter(app_label="djupkeep").values_list(
        "id", flat=True
    )
    grp, created = Group.objects.get_or_create(name=_("Upkeep Manager"))
    if created:
        permissions = Permission.objects.filter(content_type_id__in=types)
        grp.permissions.set(permissions)
    grp, created = Group.objects.get_or_create(name=_("Maintainer"))
    if created:
        codes = [
            "view_element",
            "view_location",
            "view_task",
            "check_task",
        ]
        permissions = Permission.objects.filter(
            content_type_id__in=types, codename__in=codes
        )
        grp.permissions.set(permissions)


class DjupkeepConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djupkeep"

    def ready(self):
        post_migrate.connect(create_djupkeep_groups, sender=self)
