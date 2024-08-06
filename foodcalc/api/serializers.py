from rest_framework import serializers
from food.models import Food, NutrientsQuantity
from calc.models import Rations, FoodData


class NutrientsQuantitySerializer(serializers.ModelSerializer):

    nutrient = serializers.StringRelatedField()

    class Meta:
        model = NutrientsQuantity
        fields = ('nutrient', 'amount')


class FoodSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    nutrients_data = NutrientsQuantitySerializer(many=True, source='quan')

    class Meta:
        model = Food
        fields = ('description', 'text', 'author', 'foodCategory', 'nutrients_data')
        read_only_fields = ('author',)


class FoodDataSerializer(serializers.ModelSerializer):
    food_name = serializers.StringRelatedField()

    class Meta:
        model = FoodData
        fields = ('food_name', 'weight')


class RationSerializer(serializers.ModelSerializer):
    pet_info = serializers.StringRelatedField()
    ration_data = FoodDataSerializer(many=True, source='ration')

    class Meta:
        model = Rations
        fields = ('ration_name', 'ration_comment', 'pet_info', 'ration_data')
