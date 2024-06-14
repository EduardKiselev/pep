from django.shortcuts import render, redirect, get_object_or_404
from calc.models import Food, NutrientsName, NutrientsQuantity
from django import forms


class FoodForm(forms.Form):
    food = forms.CharField(max_length=150)


class RemoveFoodForm(forms.Form):
    remove_food = forms.CharField(max_length=150)


class MassForm(forms.Form):
    mass = forms.IntegerField()

def index(request, chosen_food=[], mass_dict={}):
    template = 'calc/calc.html'

    if request.GET:
        if 'food' in request.GET:
            form = FoodForm(request.GET or None)

            if form.is_valid():

                food_to_add = form.cleaned_data['food']
                food_class = get_object_or_404(Food, description=food_to_add)
                if food_class.id not in chosen_food:
                    chosen_food.append(food_class.id)
                    print('ADDD111111', chosen_food)
                    mass_dict[food_class.id] = 100
               # print('22222',type(food_class))

        elif 'remove_food' in request.GET:
            remove_form = RemoveFoodForm(request.GET)
      #      print('================================GET', request.GET,request)
            if remove_form.is_valid():
       #         print('3333333',chosen_food)
                food_to_remove = remove_form.cleaned_data['remove_food']
      #          print('food_to_remove', food_to_remove)
                id = get_object_or_404(Food,description=food_to_remove).id
                index = chosen_food.index(id)
      #          print(index)
                chosen_food.pop(index)
                del mass_dict[id]
        del request.GET

    
    if request.POST:
        print('!!!!POST!!!!', request.POST.keys())
        for food_id in chosen_food:
            if 'mass_'+str(food_id) in request.POST.keys() and request.POST['mass_'+str(food_id)]:
                mass = int(request.POST['mass_'+str(food_id)])
                if mass > 0:
                    mass_dict[food_id] = mass
                print('TYPEE!!!!!', str(food_id), type(mass_dict[food_id]))
    print('mass_dict:', mass_dict,'\n','chosen_food:',chosen_food)

    foodlist = Food.objects.exclude(id__in=chosen_food)
    print(foodlist)
    form = FoodForm()
    delete_list = []
    nutrients = []
    items_name = []
    totals = {}
    if chosen_food:
        delete_list = Food.objects.filter(id__in=chosen_food)
        for elem in chosen_food:
            item = [NutrientsQuantity.objects.select_related('food', 'nutrient').filter(food__id=elem, nutrient__is_published=True)]
            print('ITEMS\n\n', item[0].values('nutrient_id', 'amount'))
            print('~~~~~~~~~~~~~',item[0].values('nutrient_id'),item[0].values('amount'))
            nutrients += item
            item_name = get_object_or_404(Food, id=elem)
            items_name += [item_name]



    columns = NutrientsName.objects.filter(is_published=True).order_by('name')
    print('\COLUMNS:', columns.values(), '\n')
    for food_id in chosen_food:
        all_nutr = NutrientsQuantity.objects.select_related('nutrient').filter(food__id=food_id, nutrient__is_published=True)
        for nutr in all_nutr.iterator():
            print('nutrient', nutr.nutrient, type(nutr.nutrient.name))
            totals[nutr.nutrient.name] = round(totals.get(nutr.nutrient.name, 0) + mass_dict[food_id]*nutr.amount/100,2)
    print('TOTASLS', totals)
    for elem in mass_dict:
        print(type(elem))
    print('CHOSEN FOOD', chosen_food)
    context = {"form": form, "showfood": foodlist, "mass_dict": mass_dict}
    if chosen_food:
        context |= {'delete_list': delete_list, 'columns': columns, 'items': nutrients,'items_name': items_name,'totals':totals}
        print('ITEMS NAME[0]:', items_name[0].id)

    print("form:", form, '\ncontext[mass_dict]:', context['mass_dict'], '\n')
    return render(request, template, context)
