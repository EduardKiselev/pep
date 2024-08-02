from django.contrib import admin
from food.models import Food, NutrientsName, NutrientsQuantity, NutrientGroup
from animal.models import Animal, AnimalType, PetStage
from calc.models import Rations, RecommendedNutrientLevelsDM


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('description', 'ndbNumber',
                    'fdcId',  'is_published', 'author', 'text')
    list_editable = ('is_published', 'author', 'text')
    search_fields = ('description',)
    list_filter = ('is_published',)


@admin.register(NutrientsName)
class NutrientsNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_name', 'is_published',
                    'order', 'nutr_group', 'short_name')
    list_editable = ('is_published', 'order', 'nutr_group', 'short_name')
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
    list_display = ('ration_name', 'owner', 'pet_info',
                    'ration_comment', 'pet_weight')
    list_editable = ('owner', 'ration_comment', 'pet_weight')


@admin.register(PetStage)
class PetStage(admin.ModelAdmin):
    list_display = ('description', 'pet_type', 'pet_stage', 'sterilized',
                    'nursing', 'age_start', 'age_finish', 'MER_power')
    list_editable = ('age_start', 'age_finish', 'MER_power')


@admin.register(NutrientGroup)
class NutrientGroup(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(RecommendedNutrientLevelsDM)
class RecommendedNutrientLevelsDM(admin.ModelAdmin):
    list_display = ('pet_type', 'pet_stage', 'nutrient_amount',
                    'nutrient_name')
    list_editable = ('nutrient_amount',)


admin.site.empty_value_display = 'Не задано'
