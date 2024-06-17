from django.contrib import admin
from calc.models import Food, NutrientsName, NutrientsQuantity


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('description', 'ndbNumber',
<<<<<<< HEAD
                    'fdcId',  'is_published')
=======
                    'fdcId', 'foodCategory', 'is_published')
>>>>>>> 3d50df2bfad1492f3674c35c012d319c2d19f671
    list_editable = ('is_published', )
    search_fields = ('description',)
    list_filter = ('is_published',)


@admin.register(NutrientsName)
class NutrientsNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_name', 'is_published')
    list_editable = ('is_published', )
    list_filter = ('is_published', )
    search_fields = ('name',)


@admin.register(NutrientsQuantity)
class NutrientsQuantity(admin.ModelAdmin):
    list_display = ('food_id', 'nutrient_id', 'amount')
    list_filter = ('food_id', )
    search_fields = ('food_id',)


admin.site.empty_value_display = 'Не задано'
