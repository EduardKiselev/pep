# Generated by Django 5.0.7 on 2024-08-02 03:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("animal", "0001_initial"),
        ("food", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Rations",
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
                    "pet_name",
                    models.CharField(max_length=50, verbose_name="Имя питомца"),
                ),
                ("pet_weight", models.FloatField()),
                (
                    "ration_name",
                    models.CharField(max_length=50, verbose_name="Название рациона"),
                ),
                (
                    "ration_comment",
                    models.TextField(blank=True, verbose_name="комментарий"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Составитель рациона",
                    ),
                ),
                (
                    "pet_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="animal.petstage",
                        verbose_name="Стадия питомца",
                    ),
                ),
            ],
            options={
                "unique_together": {("owner", "ration_name")},
            },
        ),
        migrations.CreateModel(
            name="FoodData",
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
                ("weight", models.FloatField()),
                (
                    "food_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="food",
                        to="food.food",
                    ),
                ),
                (
                    "ration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ration",
                        to="calc.rations",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecommendedNutrientLevelsDM",
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
                        related_name="nutrient_info",
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
