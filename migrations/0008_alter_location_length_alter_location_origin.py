# Generated by Django 4.1.5 on 2023-01-31 12:07

import djgeojson.fields
from django.db import migrations

import djupkeep.models


class Migration(migrations.Migration):

    dependencies = [
        ("djupkeep", "0007_alter_location_length"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="length",
            field=djgeojson.fields.LineStringField(
                blank=True, null=True, verbose_name="Reference length on the map"
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="origin",
            field=djgeojson.fields.PointField(
                default=djupkeep.models.get_default_origin,
                verbose_name="Origin of axis",
            ),
        ),
    ]