from rest_framework import viewsets
from food.models import Food, NutrientsQuantity
from calc.models import Rations
from .serializers import FoodSerializer, NutrientsQuantitySerializer, RationSerializer
from .permissions import ReadOnly


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Food.objects.filter(author=user)
        return queryset


class NutrientQuantityViewSet(viewsets.ModelViewSet):
    queryset = NutrientsQuantity.objects.all()
    serializer_class = NutrientsQuantitySerializer
    permission_classes = [ReadOnly]


class RationViewSet(viewsets.ModelViewSet):
    queryset = Rations.objects.all()
    serializer_class = RationSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Rations.objects.filter(owner=user)
        return queryset