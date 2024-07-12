from django.db import models
from django.contrib.auth import get_user_model
from food.models import Food, NutrientsName
from animal.models import AnimalType, PetStage

User = get_user_model()


class RecommendedNutrientLevelsDM(models.Model):
    pet_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE,
                                 verbose_name='тип питомца')
    pet_stage = models.ForeignKey(PetStage, on_delete=models.CASCADE,)
    nutrient_amount = models.FloatField(verbose_name='Количество')
    nutrient_name = models.ForeignKey(
        NutrientsName, on_delete=models.CASCADE,
        related_name='nutrient_info', verbose_name='Нутриент')

    def __str__(self):
        return str(self.pet_stage) + ' ' + str(self.nutrient_name)


class Rations(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Составитель рациона')
    pet_name = models.CharField(verbose_name='Имя питомца', max_length=50)
    pet_info = models.ForeignKey(PetStage, on_delete=models.CASCADE)
    ration_name = models.CharField(verbose_name='Название рациона',
                                   max_length=50)
    ration_comment = models.TextField(verbose_name='комментарий', blank=True)


class FoodData(models.Model):
    ration = models.ForeignKey(Rations, on_delete=models.CASCADE,
                               related_name='ration')
    food_name = models.ForeignKey(Food, on_delete=models.CASCADE,
                                  related_name='food')
    weight = models.FloatField()
