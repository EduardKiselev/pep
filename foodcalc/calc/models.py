from django.db import models


class Food(models.Model):
    description = models.CharField(max_length=30)
    number = models.IntegerField()
