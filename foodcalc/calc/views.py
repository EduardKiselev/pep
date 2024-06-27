from django.shortcuts import render, get_object_or_404
from calc.models import Food, NutrientsName, NutrientsQuantity, User, Animals
from django import forms
from django.views.generic import DetailView


class FoodForm(forms.Form):
    food = forms.CharField(max_length=150)


class RemoveFoodForm(forms.Form):
    remove_food = forms.CharField(max_length=150)


class MassForm(forms.Form):
    mass = forms.IntegerField()


class NutrinentForm(forms.Form):
    nutr_add = forms.CharField(max_length=50)


class RemoveNutrinentForm(forms.Form):
    remove_nutr = forms.CharField(max_length=50)




class FoodDetailView(DetailView):
    model = Food
    template_name = 'calc/detail.html'
    pk_url_kwarg = 'food_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nutrients = NutrientsQuantity.objects.select_related('nutrient', 'food').filter(
            food_id=self.kwargs.get(self.pk_url_kwarg)).order_by('nutrient__order')
        context['nutrients'] = nutrients
        print(context['nutrients'])
        return context


def calc(request, chosen_food=[], mass_dict={}):
    template = 'calc/calc.html'

    if request.GET:
        if 'food' in request.GET:
            form = FoodForm(request.GET or None)
            if form.is_valid():
                food_to_add = form.cleaned_data['food']
                food_class = get_object_or_404(Food, description=food_to_add)
                if food_class.id not in chosen_food:
                    chosen_food.append(food_class.id)
                    mass_dict[food_class.id] = 100
        elif 'remove_food' in request.GET:
            remove_form = RemoveFoodForm(request.GET)
            if remove_form.is_valid():
                food_to_remove = remove_form.cleaned_data['remove_food']
                id = get_object_or_404(Food, description=food_to_remove).id
                index = chosen_food.index(id)
                chosen_food.pop(index)
                del mass_dict[id]

    if request.POST:
        for food_id in chosen_food:
            if 'mass_' + str(food_id) in request.POST.keys() and request.POST['mass_' + str(food_id)]:
                mass = int(request.POST['mass_' + str(food_id)])
                if mass > 0:
                    mass_dict[food_id] = mass

    foodlist = Food.objects.exclude(id__in=chosen_food)
    form = FoodForm()
    delete_list = []
    nutrients = []
    items_name = []
    totals = {}
    if chosen_food:
        delete_list = Food.objects.filter(id__in=chosen_food)
        for elem in chosen_food:
            item = [NutrientsQuantity.objects.select_related(
                'food', 'nutrient').filter(
                    food__id=elem,
                    nutrient__is_published=True)]
            nutrients += item
            item_name = get_object_or_404(Food, id=elem)
            items_name += [item_name]
    columns = NutrientsName.objects.filter(is_published=True).order_by('order')
    for food_id in chosen_food:
        all_nutr = NutrientsQuantity.objects.select_related(
            'nutrient').filter(
                food__id=food_id, nutrient__is_published=True)
        for nutr in all_nutr.iterator():
            totals[nutr.nutrient.name] = round(
                totals.get(nutr.nutrient.name, 0)
                + mass_dict[food_id] * nutr.amount/100, 2
                                              )

    context = {"form": form, "showfood": foodlist, "mass_dict": mass_dict}
    if chosen_food:
        context |= {
            'delete_list': delete_list,
            'columns': columns,
            'items': nutrients,
            'items_name': items_name,
            'totals': totals
                   }
    return render(request, template, context)


def food_search(request, chosen_nutrients=[], mass_dict={}):

    if request.GET:
        if 'nutr_add' in request.GET:
            form = NutrinentForm(request.GET or None)
            if form.is_valid():
                nutr_to_add = form.cleaned_data['nutr_add']
                nutr_class = get_object_or_404(NutrientsName, name=nutr_to_add)
                if nutr_class.id not in chosen_nutrients:
                    chosen_nutrients.append(nutr_class.id)
                    mass_dict[nutr_class.id] = 1
        elif 'remove_nutr' in request.GET:
            remove_nutr = RemoveNutrinentForm(request.GET)
            if remove_nutr.is_valid():
                nutr_to_remove = remove_nutr.cleaned_data['remove_nutr']
                id = get_object_or_404(NutrientsName, name=nutr_to_remove).id
                index = chosen_nutrients.index(id)
                chosen_nutrients.pop(index)
                del mass_dict[id]
 
    if request.POST:
        for nutrient_id in chosen_nutrients:
            print(nutrient_id)
            if str(nutrient_id) in request.POST.keys():
                mass = int(request.POST[str(nutrient_id)])
                if mass > 0:
                    mass_dict[nutrient_id] = mass

    template = 'calc/func.html'
    nutrient_list = NutrientsName.objects.filter(is_published=True).exclude(id__in=chosen_nutrients)
    form = NutrinentForm()

    if chosen_nutrients:
        delete_list = NutrientsName.objects.filter(id__in=chosen_nutrients)
        totals = {}
        nutrients = {}
        for nutrient in chosen_nutrients:
            nutrients[nutrient] = {}
            objects = NutrientsQuantity.objects.filter(nutrient_id=nutrient)
            for object in objects:
                totals[object.food_id] = round(totals.get(object.food_id,0) + mass_dict[nutrient] * object.amount, 2)
                nutrients[nutrient][object.food_id] = object.amount

        res = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:10]
        print('FOOD RATING:')
        rating = {}
        for elem in res:
            name = get_object_or_404(Food, id=elem[0])
            rating[name] = elem[1]
            print(name, ':', elem[1])
        add_context = {'delete_list': delete_list, 'rating': rating, 'nutrients': nutrients}
    
    print('chosen nutrients', chosen_nutrients, '\nmass_dict:', mass_dict)

    if chosen_nutrients:
        print('deletelist', delete_list, '\nnutrients:', nutrients)
    context = {'nutrient_list': nutrient_list, 'chosen_nutrients': chosen_nutrients, 'mass_dict': mass_dict}
    if chosen_nutrients:
        context |= add_context
    return render(request, template, context)


def profile(request, username):
    template = 'calc/profile.html'
    profile = get_object_or_404(User, username=username)
    animals = Animals.objects.filter(owner=username)
    context = {'profile': profile, 'animals': animals}
    return render(request, template, context)
