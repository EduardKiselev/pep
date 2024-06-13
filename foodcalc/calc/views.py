from django.shortcuts import render, redirect, get_object_or_404
from calc.models import Food, NutrientsName, NutrientsQuantity
from django import forms

RESETFORM = 'RESETFORM'


class FoodForm(forms.Form):
    food = forms.CharField(max_length=150)


class RemoveFoodForm(forms.Form):
    remove_food = forms.CharField(max_length=150)

def index(request, chosen_food=[]):
    template = 'calc/calc.html'

    if request.GET:
        if 'food' in request.GET:
            form = FoodForm(request.GET)
            print(form)
            print('---------------------------GET', request.GET['food'],request)
            if form.is_valid():
                print('111111',chosen_food)
                food_to_add = form.cleaned_data['food']
                print('food_to_add', food_to_add)
                if food_to_add not in chosen_food:
                    chosen_food.append(food_to_add)
                    print('22222',chosen_food)
        elif 'remove_food' in request.GET:
            remove_form = RemoveFoodForm(request.GET)
            print('================================GET', request.GET,request)
            if remove_form.is_valid():
                print('3333333',chosen_food)
                food_to_remove = remove_form.cleaned_data['remove_food']
                print('food_to_remove', food_to_remove)
                index = chosen_food.index(food_to_remove)
                print(index)
                chosen_food.pop(index)

    else:
        print('REDIRECT')
        chosen_food = []
        redirect('calc:index')

    foodlist = Food.objects.all()
    form = FoodForm()
    delete_list = []
    items=[]
    if chosen_food:
        for elem in chosen_food:
            delete_list = Food.objects.filter(description__in=chosen_food)

            item = NutrientsQuantity.objects.filter(food__description=elem, nutrient__is_published=True).order_by('nutrient__name')
            print('\nITEM:', item.values(), '\n')
            items.append(item)
    columns = NutrientsName.objects.filter(is_published=True).order_by('name')
    print('\COLUMNS:', columns.values(), '\n')
    context = {"form": form, "showfood": foodlist, 'chosen': chosen_food}
    if chosen_food:
        context |= {'delete_list': delete_list, 'columns': columns, 'items': items}
     #   print('DELETE LIST:', delete_list)




    #print("form:", form, '\ncontext:', context['chosen'], '\n')
    return render(request, template, context)
