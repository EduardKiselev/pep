from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Food(models.Model):
    description = models.CharField(max_length=150)
    ndbNumber = models.IntegerField()
    fdcId = models.IntegerField()
#    foodCategory = models.CharField(max_length=50)

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы не выводить продукт.')

    def __str__(self):
        return 'CLASS ' + self.description


class NutrientsName(models.Model):
    name = models.CharField(max_length=50)
    unit_name = models.CharField(max_length=10)
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы не выводить нутриент.')
    order = models.IntegerField(default=100)

    def __str__(self):
        return 'CLASS ' + self.name


class NutrientsQuantity(models.Model):
    food = models.ForeignKey(
        Food,
        verbose_name="Продукт",
        on_delete=models.CASCADE,
        related_name='quan')
    nutrient = models.ForeignKey(
        NutrientsName,
        verbose_name='Имя нутриента',
        on_delete=models.CASCADE,
        related_name='quan')
    amount = models.FloatField(verbose_name='Количество')

    def __str__(self):
        return '&CLASS ' + str(self.food) +\
            ': ' + str(self.nutrient) + '=' + str(self.amount) + '&'


class AnimalType(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Animal(models.Model):
    name = models.CharField(verbose_name='Имя питомца', max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Хозяин')
    type = models.ForeignKey(AnimalType, on_delete=models.CASCADE, related_name='type', verbose_name='Тип питомца')
    nursing = models.BooleanField(verbose_name='Является ли питомец кормящей')
    sterilized = models.BooleanField(verbose_name='питомец стерилизован?')
    weight = models.FloatField(verbose_name='Вес', help_text='Масса питомца, в кг')
    birthday = models.DateField(verbose_name='Дата рождения', help_text='При возрасте более года достаточно указать год')

    def __str__(self):
        return 'cls ' + self.name


class PetStage(models.Model):
    description = models.CharField(verbose_name='Описание стадии', max_length=50)
    pet_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE, verbose_name='тип питомца')
    pet_stage = models.CharField(verbose_name='Стадия питомца', max_length=50)
    sterilized = models.BooleanField(verbose_name='питомец стерилизован?')
    nursing = models.BooleanField(verbose_name='Является ли питомец кормящей')
    age_start = models.IntegerField(verbose_name='начало стадии', help_text='с какого возраста начинается эта стадия')
    age_finish = models.IntegerField(verbose_name='конец стадии', help_text='до какого возраста длится эта стадия')

    def __str__(self):
        return 'cls ' + str(self.pet_type) + ' ' + str(self.pet_stage) +' ster:'+str(self.sterilized)


class RecommendedNutrientLevelsDM(models.Model):
    pet_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE,
                                 verbose_name='тип питомца')
    pet_stage = models.ForeignKey(PetStage, on_delete=models.CASCADE,)
    nutrient_amount = models.FloatField(verbose_name='Количество')
    nutrient_name = models.ForeignKey(NutrientsName, on_delete=models.CASCADE,
                                 related_name='nutrient_info', verbose_name='Нутриент')

    def __str__(self):
        return str(self.pet_stage) + ' ' + str(self.nutrient_name)


class Rations(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Составитель рациона')
    pet_name = models.CharField(verbose_name='Имя питомца', max_length=50)
    pet_info = models.ForeignKey(PetStage, on_delete=models.CASCADE)
    ration_name = models.CharField(verbose_name='Название рациона', max_length=50)
    ration_comment = models.TextField(verbose_name='комментарий', blank=True)


class FoodData(models.Model):
    ration = models.ForeignKey(Rations, on_delete=models.CASCADE,
                                related_name='ration')
    food_name = models.ForeignKey(Food, on_delete=models.CASCADE,
                                related_name='food')
    weight = models.IntegerField()
