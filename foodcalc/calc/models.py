from django.db import models


class Food(models.Model):
    description = models.CharField(max_length=150)
    ndbNumber = models.IntegerField()
    fdcId = models.IntegerField()
<<<<<<< HEAD
#    foodCategory = models.CharField(max_length=50, default=None)
=======
    foodCategory = models.CharField(max_length=50)
>>>>>>> 3d50df2bfad1492f3674c35c012d319c2d19f671
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
