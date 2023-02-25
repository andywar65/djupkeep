# Generated by Django 4.1.5 on 2023-02-25 16:58

import django.db.models.deletion
import djgeojson.fields
import filebrowser.fields
from django.conf import settings
from django.db import migrations, models

import djupkeep.models


class Migration(migrations.Migration):

    replaces = [
        ("djupkeep", "0001_initial"),
        ("djupkeep", "0002_alter_project_fb_image_alter_project_image_and_more"),
        ("djupkeep", "0003_location_delete_project"),
        ("djupkeep", "0004_category"),
        ("djupkeep", "0005_location_length_location_meters"),
        ("djupkeep", "0006_remove_location_unit"),
        ("djupkeep", "0007_alter_location_length"),
        ("djupkeep", "0008_alter_location_length_alter_location_origin"),
        ("djupkeep", "0009_element"),
        ("djupkeep", "0010_alter_element_geom"),
        ("djupkeep", "0011_activity"),
        ("djupkeep", "0012_alter_category_options_category_position"),
        ("djupkeep", "0013_activity_position"),
        ("djupkeep", "0014_alter_activity_options_alter_category_options_and_more"),
        ("djupkeep", "0015_alter_activity_frequency_task"),
        ("djupkeep", "0016_alter_task_options"),
        ("djupkeep", "0017_alter_task_options_location_drawing"),
        ("djupkeep", "0018_activity_extend_task_read_alter_activity_frequency"),
        ("djupkeep", "0019_activity_once_activity_repeat"),
    ]

    initial = True

    dependencies = [
        ("djeocad", "0016_drawing_designx_drawing_designy_alter_insertion_geom"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=50, verbose_name="Name")),
                (
                    "intro",
                    models.CharField(
                        max_length=200, null=True, verbose_name="Description"
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="djupkeep.category",
                        verbose_name="parent",
                    ),
                ),
                ("position", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Category",
                "verbose_name_plural": "Categories",
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=50, verbose_name="Name")),
                (
                    "intro",
                    models.CharField(
                        max_length=200, null=True, verbose_name="Description"
                    ),
                ),
                (
                    "fb_image",
                    filebrowser.fields.FileBrowseField(
                        help_text="Plan of your location",
                        max_length=200,
                        null=True,
                        verbose_name="Plan",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Plan of your location",
                        max_length=200,
                        null=True,
                        upload_to="uploads/images/upkeep/",
                        verbose_name="Plan",
                    ),
                ),
                (
                    "origin",
                    djgeojson.fields.PointField(
                        default=djupkeep.models.get_default_origin,
                        verbose_name="Origin of axis",
                    ),
                ),
                (
                    "length",
                    djgeojson.fields.LineStringField(
                        blank=True,
                        null=True,
                        verbose_name="Reference length on the map",
                    ),
                ),
                (
                    "meters",
                    models.FloatField(
                        default=1, verbose_name="Reference length in meters"
                    ),
                ),
                (
                    "drawing",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="locations",
                        to="djeocad.drawing",
                        verbose_name="Drawing",
                    ),
                ),
            ],
            options={
                "verbose_name": "Location",
                "verbose_name_plural": "Locations",
            },
        ),
        migrations.CreateModel(
            name="Element",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "intro",
                    models.CharField(
                        max_length=200, null=True, verbose_name="Description"
                    ),
                ),
                (
                    "fb_image",
                    filebrowser.fields.FileBrowseField(
                        max_length=200, null=True, verbose_name="Image"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        max_length=200,
                        null=True,
                        upload_to="uploads/images/upkeep/",
                        verbose_name="Image",
                    ),
                ),
                (
                    "geom",
                    djgeojson.fields.PointField(null=True, verbose_name="Position"),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="elements",
                        to="djupkeep.category",
                        verbose_name="Category",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="elements",
                        to="djupkeep.location",
                        verbose_name="Location",
                    ),
                ),
            ],
            options={
                "verbose_name": "Element",
                "verbose_name_plural": "Elements",
            },
        ),
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=50, verbose_name="Name")),
                ("intro", models.TextField(null=True, verbose_name="Description")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="djupkeep.category",
                        verbose_name="Category",
                    ),
                ),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("7", "Weekly"),
                            ("30", "Monthly"),
                            ("60", "Bimonthly"),
                            ("90", "Quarterly"),
                            ("120", "Four-monthly"),
                            ("183", "Biannual"),
                            ("365", "Annual"),
                            ("730", "Every two years"),
                        ],
                        default="30",
                        max_length=3,
                    ),
                ),
                (
                    "extend",
                    models.BooleanField(
                        default=False, verbose_name="Apply to subcategories only"
                    ),
                ),
                (
                    "once",
                    models.BooleanField(default=False, verbose_name="Apply only once"),
                ),
                ("repeat", models.BooleanField(default=True, editable=False)),
            ],
            options={
                "verbose_name": "Activity",
                "verbose_name_plural": "Activities",
                "ordering": ["category", "position"],
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("due_date", models.DateField(null=True, verbose_name="Due date")),
                (
                    "check_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Check date"
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, null=True, verbose_name="Notes"),
                ),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="djupkeep.activity",
                        verbose_name="Activity",
                    ),
                ),
                (
                    "element",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="djupkeep.element",
                        verbose_name="Element",
                    ),
                ),
                (
                    "maintainer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Maintainer",
                    ),
                ),
                (
                    "read",
                    models.BooleanField(
                        default=False, verbose_name="Notes have been read"
                    ),
                ),
            ],
            options={
                "verbose_name": "Task",
                "verbose_name_plural": "Tasks",
                "ordering": ["due_date"],
                "permissions": [
                    ("check_task", "Can perform activity tasks on elements")
                ],
            },
        ),
    ]
