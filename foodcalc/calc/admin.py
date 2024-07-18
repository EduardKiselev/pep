from django.contrib import admin
from food.models import Food, NutrientsName, NutrientsQuantity
from animal.models import Animal, AnimalType
from calc.models import Rations


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('description', 'ndbNumber',
                    'fdcId',  'is_published')
    list_editable = ('is_published', )
    search_fields = ('description',)
    list_filter = ('is_published',)


@admin.register(NutrientsName)
class NutrientsNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_name', 'is_published', 'order')
    list_editable = ('is_published', 'order')
    list_filter = ('is_published', )
    search_fields = ('name',)


@admin.register(NutrientsQuantity)
class NutrientsQuantity(admin.ModelAdmin):
    list_display = ('food_id', 'nutrient_id', 'amount')
    list_filter = ('food_id', )
    search_fields = ('food_id',)


@admin.register(AnimalType)
class AnimalType(admin.ModelAdmin):
    list_display = ('title', 'description')
    list_editable = ('description',)


@admin.register(Animal)
class Animal(admin.ModelAdmin):
    list_display = ('name', 'owner', 'type', 'nursing', 'weight', 'birthday')
    list_editable = ('owner', 'type', 'nursing', 'weight', 'birthday')


@admin.register(Rations)
class Rations(admin.ModelAdmin):
    list_display = ('ration_name', 'owner', 'pet_info',)


admin.site.empty_value_display = 'Не задано'
