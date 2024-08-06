from rest_framework import viewsets
from food.models import Food, NutrientsQuantity
from .serializers import FoodSerializer, NutrientsQuantitySerializer


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class NutrientQuantityViewSet(viewsets.ModelViewSet):
    queryset = NutrientsQuantity.objects.all()
    serializer_class = NutrientsQuantitySerializer
