from django.shortcuts import render, get_object_or_404, redirect
from calc.models import Food, NutrientsName, NutrientsQuantity, User, Animal, RecommendedNutrientLevelsDM, PetStage, Rations, FoodData
from calc.forms import FoodForm, RemoveFoodForm, NutrinentForm, RemoveNutrinentForm, ProfileForm, PetForm, RationNameForm
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django import forms
from calc.utils import pet_stage_calculate
import datetime

import os

import pprint


class FoodDetailView(DetailView):
    model = Food
    template_name = 'calc/detail.html'
    pk_url_kwarg = 'food_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nutrients = NutrientsQuantity.objects.select_related('nutrient', 'food').filter(
            food_id=self.kwargs.get(self.pk_url_kwarg), nutrient__is_published=True).order_by('nutrient__order')
        context['nutrients'] = nutrients
        return context


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    fields = ['name', 'type', 'nursing', 'sterilized', 'weight', 'birthday']
    template_name = 'animal/create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        sterilized = form.cleaned_data.get('sterilized')
        nursing = form.cleaned_data.get('nursing')
        if sterilized*nursing:
            form.add_error('nursing', forms.ValidationError('не возможно быть одновременно стерилизованным и кормящим/беременным'))
            return super().form_invalid(form)

        name = form.cleaned_data.get('name')
        if len(Animal.objects.filter(name=name, owner=self.request.user)) == 1:
            form.add_error('name', forms.ValidationError('У вас уже есть питомец с этим именем'))
            return super().form_invalid(form)

        form.instance.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('calc:calc')


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    model = Animal
    template_name = 'animal/create.html'
    fields = ['name', 'type', 'nursing', 'sterilized', 'weight', 'birthday']

    def form_valid(self, form):
        self.object = form.save(commit=False)

        sterilized = form.cleaned_data.get('sterilized')
        nursing = form.cleaned_data.get('nursing')
        if sterilized*nursing:
            form.add_error('nursing', forms.ValidationError('не возможно быть одновременно стерилизованным и кормящим/беременным'))
            return super().form_invalid(form)

        form.instance.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))


class AnimalDeleteView(LoginRequiredMixin, DeleteView):
    model = Animal
    template_name = 'animal/create.html'

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))


def profile(request, username):
    template = 'animal/profile.html'

    if request.GET:
        return redirect(reverse('calc:calc', kwargs={'chosen_food':[1,2]}))

    profile = get_object_or_404(User, username=username)
    animals = Animal.objects.filter(owner=profile)
    foods = FoodData.objects.select_related('ration','food_name').filter(ration__owner=profile)
    rations_list = set()
    rations = Rations.objects.filter(id__in=rations_list)
    for elem in foods.values('ration'):
        rations_list.add(elem['ration'])
    rations = Rations.objects.filter(id__in=rations_list)
    print(rations)
    context = {'profile': profile, 'animals': animals,'foods':foods,'rations':rations}
    return render(request, template, context)


@login_required
def calc(request, chosen_food=[], mass_dict={}, chosen_pet=[]):
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
        elif 'chose_pet' in request.GET:
            form = PetForm(request.GET or None)
            if form.is_valid():
                pet_name = form.cleaned_data['chose_pet']
                chosen_pet.append(get_object_or_404(Animal, name=pet_name, owner=request.user))
        elif 'pet_reset' in request.GET:
            chosen_pet = []

    if request.POST:
        for food_id in chosen_food:
            if 'mass_' + str(food_id) in request.POST.keys() and request.POST['mass_' + str(food_id)]:
                mass = int(request.POST['mass_' + str(food_id)])
                if mass > 0:
                    mass_dict[food_id] = mass
        # if 'make_file' in request.POST.keys():
        #     path  = Path(__file__).resolve().parent.parent
        #     print(type(path))
        #     base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        #     filename = chosen_pet[0].name+'_'+str(datetime.datetime.now().date())
        #     file_path = base_dir+'/files/'+filename+'.txt'
        #     print('time to make file!')
        #     with open(file_path,'w') as file:
        #         pprint.pp(context,file)

    foodlist = Food.objects.exclude(id__in=chosen_food)
    pet_list = Animal.objects.filter(owner=request.user)
    form = FoodForm()
    delete_list = []
    nutrients = []
    items_name = []
    totals = {}

    # Pet
    if chosen_pet:
        tmp = pet_stage_calculate(chosen_pet[0])
        if not tmp:
            return redirect('calc:index')
        else:
            pet_stage, weight = tmp
            pet_stage_info = get_object_or_404(PetStage, id=pet_stage.id)
            rec_nutr = RecommendedNutrientLevelsDM.objects.filter(pet_stage__id=pet_stage.id).select_related('nutrient_name')
            recommended = {}
            for nutr in rec_nutr.iterator():
                recommended[nutr.nutrient_name] = nutr.nutrient_amount
                if nutr.nutrient_name.name == 'Energy':
                    recommended[nutr.nutrient_name] = round(get_object_or_404(rec_nutr,nutrient_name__name='Energy').nutrient_amount*(weight)**(0.75),2)
                if nutr.nutrient_name.name == 'Water':
                    recommended[nutr.nutrient_name] = ' '


    # Food
    if chosen_food:
        mass_dict[0] = sum(mass_dict.values())-mass_dict.get(0,0)

        # Totals
        for food_id in chosen_food:
            all_nutr = NutrientsQuantity.objects.select_related(
                'nutrient').filter(
                    food__id=food_id, nutrient__is_published=True)
            for nutr in all_nutr.iterator():
                totals[nutr.nutrient.name] = round(
                    totals.get(nutr.nutrient.name, 0)
                    + mass_dict[food_id] * nutr.amount/100, 2
                                                )

        # Food nutrients
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
    
        # Dry_matter
        total_mass = mass_dict[0]
        total_water = totals['Water']
        on_dry_matter = {}
        for nutr in totals:
            if nutr != 'Water' and nutr != 'Energy':
                measure = round(100*totals[nutr]/(total_mass-total_water),2)
                if measure >= 10: measure = round(measure,1)
                if measure >= 100: measure = int(measure)
                on_dry_matter[nutr] = measure
        pprint.pp(on_dry_matter)
        if chosen_pet:
            on_dry_matter['Energy'] = totals['Energy']
    
    # context
    context = {"form": form, "showfood": foodlist, "mass_dict": mass_dict, 'pet_list': pet_list}
    if chosen_food:
        context |= {
            'delete_list': delete_list,
            'columns': columns,
            'items': nutrients,
            'items_name': items_name,
            'totals': totals,
            'on_dry_matter': on_dry_matter
                   }
    if chosen_pet:
        context |= {
            'pet_stage': pet_stage_info,
            'chosen_pet': chosen_pet[0],
            'recommended_nutr': recommended,
        }

    if 'make_file' in request.POST.keys():
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filename = chosen_pet[0].name+'_'+str(datetime.datetime.now().date())
            file_path = base_dir+'/files/'+filename+'.txt'
            print('time to make file!')
            with open(file_path, 'w') as file:
                pprint.pp(context, file)

    if 'ration_name' in request.POST.keys():
        form = RationNameForm(request.POST or None)
        if form.is_valid():
            ration_instance = Rations.objects.create(pet_name=chosen_pet[0].name, pet_info=pet_stage, ration_name=request.POST['ration_name'],owner=request.user)
            print(mass_dict)
            print(chosen_food)
            food_instance = Food.objects.filter(id__in=chosen_food)
            foods = (FoodData(ration=ration_instance, food_name=food, weight=mass_dict[food.id]) for food in food_instance)
        FoodData.objects.bulk_create(foods)

        return redirect('calc:profile', username=request.user)

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
            if str(nutrient_id) in request.POST.keys():
                mass = int(request.POST[str(nutrient_id)])
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
            objects = NutrientsQuantity.objects.select_related(
                'food').filter(nutrient__id=nutrient)
            for object in objects:
                totals[object.food] = round(
                    totals.get(object.food, 0) +
                    mass_dict[nutrient] * object.amount, 2)
                nutrients[nutrient][object.food] = object.amount
        all_food = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:75]
        paginator = Paginator(all_food, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        add_context = {'delete_list': delete_list, 'page_obj': page_obj, 'nutrients': nutrients}

    context = {'nutrient_list': nutrient_list, 'chosen_nutrients': chosen_nutrients, 'mass_dict': mass_dict}
    if chosen_nutrients:
        context |= add_context
    return render(request, template, context)


def index(request):
    template = 'pages/about.html'
    return render(request, template)



@login_required
def profile_update(request):
    template = 'animal/user.html'
    instance = get_object_or_404(User, username=request.user)
    form = ProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('calc:index')
    return render(request, template, context)


def recnutrlvl(request):
    template = 'calc/recnutrlvl.html'
    pet_stages = PetStage.objects.all().select_related('pet_type')
    nutrients = RecommendedNutrientLevelsDM.objects.all().select_related('nutrient_name')
    nutrients_name = NutrientsName.objects.exclude(name='Water').filter(is_published=True).order_by('order')
    nutrient_dict = {}

    for stage in pet_stages:
        nutrient_dict[stage.pet_stage] = {}
        object = nutrients.filter(pet_stage=stage.id)
        for obj in object:
            measure = obj.nutrient_amount
            if measure >= 100:
                measure = int(measure)
            nutrient_dict[stage.pet_stage][obj.nutrient_name] = measure
    context = {
        'pet_stages': pet_stages,
        'nutrient_dict': nutrient_dict,
        'nutrients_name': nutrients_name
    }
    return render(request, template, context)
