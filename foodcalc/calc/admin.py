from django.contrib import admin
from calc.models import Food


class FoodAdmin(admin.ModelAdmin):
    list_display = ('description', 'number')


admin.site.empty_value_display = 'Не задано'
admin.site.register(Food, FoodAdmin)
