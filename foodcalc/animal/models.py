from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AnimalType(models.Model):
    title = models.CharField(max_length=50,verbose_name='Название на латинском')
    description = models.TextField(verbose_name='Название на русском')

    def __str__(self):
        return self.description


class Animal(models.Model):
    name = models.CharField(verbose_name='Имя питомца', max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              verbose_name='Хозяин')
    type = models.ForeignKey(AnimalType, on_delete=models.CASCADE,
                             related_name='type', verbose_name='Тип питомца')
    nursing = models.BooleanField(verbose_name='Является ли питомец кормящей')
    sterilized = models.BooleanField(verbose_name='питомец стерилизован?')
    weight = models.FloatField(
        verbose_name='Вес',
        help_text='Масса питомца, в кг')
    birthday = models.DateField(
        verbose_name='Дата рождения',
        help_text='''При возрасте более года рацион
        рассчитывается для взрослых собак'''
        )

    def __str__(self):
        return 'cls ' + self.name


class PetStage(models.Model):
    description = models.CharField(verbose_name='Описание стадии',
                                   max_length=50)
    pet_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE,
                                 verbose_name='тип питомца')
    pet_stage = models.CharField(verbose_name='Стадия питомца', max_length=50)
    sterilized = models.BooleanField(verbose_name='питомец стерилизован?')
    nursing = models.BooleanField(verbose_name='Является ли питомец кормящей')
    age_start = models.IntegerField(
        verbose_name='начало стадии',
        help_text='с какого возраста начинается эта стадия')
    age_finish = models.IntegerField(
        verbose_name='конец стадии',
        help_text='до какого возраста длится эта стадия')

    def __str__(self):
        return 'cls ' + str(self.pet_type) + ' ' +\
              str(self.pet_stage) + ' ster:'+str(self.sterilized)
