# Generated by Django 4.1.5 on 2023-01-22 22:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djupkeep", "0003_location_delete_project"),
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
            ],
            options={
                "verbose_name": "Element category",
                "verbose_name_plural": "Element categories",
            },
        ),
    ]