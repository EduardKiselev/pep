from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Food(models.Model):
    description = models.CharField(max_length=150, unique=True,
                                   verbose_name='Название продукта')
    ndbNumber = models.IntegerField()
    fdcId = models.IntegerField()
    foodCategory = models.CharField(default='None', max_length=150)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Составитель нутриентов продукта')
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы не выводить продукт.')

    def __str__(self):
        return 'CLASS ' + self.description

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class NutrientsName(models.Model):
    name = models.CharField(max_length=50)
    unit_name = models.CharField(max_length=10)
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы не выводить нутриент.')
    order = models.IntegerField(default=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


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
        return '&cls ' + str(self.food) +\
            ': ' + str(self.nutrient) + '=' + str(self.amount) + '&'
