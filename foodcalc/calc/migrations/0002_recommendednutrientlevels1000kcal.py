# Generated by Django 5.0.7 on 2024-08-02 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0001_initial"),
        ("calc", "0001_initial"),
        ("food", "0007_rename_group_nutrientgroup_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecommendedNutrientLevels1000kcal",
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
                ("nutrient_amount", models.FloatField(verbose_name="Количество")),
                (
                    "nutrient_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nutrient_name",
                        to="food.nutrientsname",
                        verbose_name="Нутриент",
                    ),
                ),
                (
                    "pet_stage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="animal.petstage",
                    ),
                ),
                (
                    "pet_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="animal.animaltype",
                        verbose_name="тип питомца",
                    ),
                ),
            ],
        ),
    ]
