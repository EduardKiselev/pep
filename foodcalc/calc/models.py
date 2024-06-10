from django.db import models

# Create your models here.

class Food(models.Model):
    foodClass = models.CharField(max_length=30)
    description = models.CharField(max_length=30)



class Nutrients(models.Model):
    id = 