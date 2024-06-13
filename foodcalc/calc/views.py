from django.shortcuts import render, redirect
from calc.models import Food
from django import forms


RESETFORM = 'RESETFORM'


class FoodForm(forms.Form):
    food = forms.CharField(max_length=150)


def index(request, chosen_food=[]):
    template = 'calc/calc.html'

    if request.GET:
        form = FoodForm(request.GET)
        print('GET', request.GET)
        if form.is_valid():
            print('111111',chosen_food)
            food_to_add = form.cleaned_data['food']
            print('food_to_add', food_to_add)
            if food_to_add not in chosen_food:
                chosen_food.append(food_to_add)
                print('22222',chosen_food)
    else:
        print('REDIRECT')
        chosen_food = []
        redirect('calc:index')

    foodlist = Food.objects.all()
    form = FoodForm()
    context = {"form": form, "showfood": foodlist, 'chosen': chosen_food}
    print("form:", form, '\ncontext:', context['chosen'], '\n', chosen_food)
    return render(request, template, context)
