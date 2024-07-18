# Generated by Django 5.0.7 on 2024-07-18 10:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0005_auto_20240717_0514"),
        ("calc", "0002_rations_pet_weight_alter_rations_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rations",
            name="pet_info",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="animal.petstage",
                verbose_name="Стадия питомца",
            ),
        ),
    ]
