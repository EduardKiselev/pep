from rest_framework import serializers
from food.models import Food, NutrientsQuantity


class NutrientsQuantitySerializer(serializers.ModelSerializer):

    food = serializers.StringRelatedField()
    nutrient = serializers.StringRelatedField()

    class Meta:
        model = NutrientsQuantity
        fields = ('food', 'nutrient', 'amount')


class FoodSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    nutrients = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = ('description', 'text', 'author', 'foodCategory', 'nutrients')
        read_only_fields = ('author',)

    def get_nutrients(self, obj):
