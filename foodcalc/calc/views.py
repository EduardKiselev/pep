from django.shortcuts import render, get_object_or_404, redirect
from calc.models import User, RecommendedNutrientLevelsDM, \
    Rations, FoodData, RecommendedNutrientLevels1000kcal
from animal.models import Animal, PetStage
from food.models import Food, NutrientsName, NutrientsQuantity, NutrientGroup
from calc.forms import FoodForm, RemoveFoodForm, ProfileForm, \
    PetForm, RationCreateForm, FileForm
from django.views.generic import DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from calc.utils import pet_stage_calculate, import_from_file, \
    export_to_file, initialize, round_rules
# import pprint
from pages.urls import csrf_failure
from pathlib import Path
from django_filters.views import FilterView
from calc.filters import RationFilter
from datetime import datetime
import csv
from django.db.models import Sum


class RationDetailView(UpdateView):
    model = Rations
    template_name = 'calc/detail.html'
    pk_url_kwarg = 'ration_id'
    fields = ['ration_comment']

    def get(self, *args, **kwargs):
        if 'open_in_calc' in self.request.GET:
            return redirect(reverse('calc:calc',
                                    args=(self.kwargs.get(
                                        self.pk_url_kwarg),)))
        if 'delete' in self.request.GET:
            return redirect(reverse('calc:ration_delete',
                                    args=(self.kwargs.get(
                                        self.pk_url_kwarg),)))
        if 'export' in self.request.GET:
            return redirect(reverse('calc:ration_export',
                                    args=(self.kwargs.get(
                                        self.pk_url_kwarg),)))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        food_data = FoodData.objects.select_related(
            'food_name', 'ration').filter(
            ration__id=self.kwargs.get(self.pk_url_kwarg))
        context['food_data'] = food_data
        return context

    def get_success_url(self):
        print(self.request.user.username)
        return reverse_lazy('calc:profile',
                            args=(self.request.user.username,))


def ration_csv_export(request, ration_id,flag_detail):
    instance = get_object_or_404(Rations, id=ration_id)
    pet_stage = instance.pet_info
    food_data = FoodData.objects.filter(
        ration=instance).select_related('food_name')
    directory = str(Path(__file__).resolve().parent.parent)
    filename = '/files/'+request.user.username + '_' + instance.ration_name +\
        str(datetime.now().date())+'.csv'
    file = directory + filename

    nutr_groups = NutrientGroup.objects.all()
    food_list = [food.food_name.description for food in food_data]
    nutrients = NutrientsName.objects.filter(is_published=True)
    chosen_food = Food.objects.filter(description__in=food_list)
    nutr_quan = NutrientsQuantity.objects.filter(food__in=chosen_food)
    recommended = RecommendedNutrientLevelsDM.objects.filter(
        pet_stage=pet_stage)

    # Dry_matter
    total_mass = food_data.aggregate(Sum('weight'))['weight__sum']
    total_water = 0
    water = NutrientsName.objects.filter(name='Water').get()
    for food in chosen_food:
        total_water += nutr_quan.filter(
            food=food, nutrient=water).get().amount * food_data.filter(
                food_name=food).get().weight/100

    result = []
    for group in nutr_groups:
        print(group)
        result.append([group.name])
        group_nutrients = nutrients.filter(nutr_group=group)
        totals = {nutr: 0 for nutr in group_nutrients}
        row = ['', ]
        for nutr in group_nutrients:
            if nutr.short_name:
                row.append(nutr.short_name+', '+nutr.unit_name)
            else:
                row.append(nutr.name+', '+nutr.unit_name)
        result.append(row)
        for food in chosen_food:
            row = []
            row.append(food.description)
            for nutr in group_nutrients:
                curr_nutr = nutr_quan.filter(food=food, nutrient=nutr)
                if curr_nutr:
                    amount = round_rules(
                        curr_nutr.get().amount * food_data.filter(
                            food_name=food).get().weight/100)
                    row.append(amount)
                    totals[nutr] += amount
                else:
                    row.append('')
            result.append(row)
        totals_row = ['Итого', ]
        totals_row.extend([totals[nutr] for nutr in group_nutrients])
        result.append(totals_row)

        dry_matter_row = ['на 100гр. сухого', ]
        dry_matter_row.extend(round_rules(totals*100/(total_mass-total_water))
                              for totals in totals_row[1:])
        result.append(dry_matter_row)

        recomm_curr = recommended.filter(nutrient_name__in=group_nutrients)
        recomm_row = ['Норма', ]
        recomm_row.extend([elem.nutrient_amount for elem in recomm_curr])
        result.append(recomm_row)
    print(*result, sep='\n')
    if flag_detail:
        with open(file, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            for row in result:
                writer.writerow(row)
    else:
        pass
    return redirect(reverse('calc:ration_detail', args=(ration_id,)))


class RationDeleteView(DeleteView):
    model = Rations
    template_name = 'calc/delete.html'
    pk_url_kwarg = 'ration_id'
    success_url = reverse_lazy('calc:index')


class SearchRationListView(FilterView):
    model = Rations
    template_name = 'calc/search_rations.html'
    filterset_class = RationFilter
    context_object_name = 'rations'
    paginate_by = 10

    def get_queryset(self):
        return Rations.objects.filter(owner=self.request.user)


def profile(request, username):
    template = 'animal/profile.html'

    if request.GET:
        ration_id = list(request.GET.keys())[0]
        return redirect(reverse('calc:ration_detail', args=(ration_id,)))
    profile = get_object_or_404(User, username=username)
    animals = Animal.objects.filter(owner=profile)
    foods = FoodData.objects.select_related(
        'ration', 'food_name').filter(ration__owner=profile)
    rations_list = set()
    for elem in foods.values('ration'):
        rations_list.add(elem['ration'])
    rations = Rations.objects.filter(id__in=rations_list)
    context = {'profile': profile,
               'animals': animals,
               'foods': foods,
               'rations': rations}
    return render(request, template, context)


@login_required
def calc(request, ration=0):
    template = 'calc/calc.html'

    mass_dict, chosen_food, chosen_pet = initialize(ration, request)
    #if ration != 0:
    #    return redirect(reverse('calc:calc', args=(1,)))

    # print('chosen_food:', chosen_food)
    # print('mass_dict:', mass_dict)
    # print('chosen_pet:', chosen_pet)

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
                if id in chosen_food:
                    index = chosen_food.index(id)
                    chosen_food.pop(index)
                    del mass_dict[id]
        elif 'chose_pet' in request.GET:
            form = PetForm(request.GET or None)
            if form.is_valid():
                pet_name = form.cleaned_data['chose_pet']
                chosen_pet = get_object_or_404(Animal,
                                               name=pet_name,
                                               owner=request.user)
        elif 'pet_reset' in request.GET:
            chosen_pet = None

    if request.POST:
        for food_id in chosen_food:
            if 'mass_' + str(food_id) in request.POST.keys():
                if request.POST['mass_' + str(food_id)]:
                    mass = float(request.POST['mass_' + str(food_id)])
                    if mass >= 0:
                        mass_dict[food_id] = mass

    foodlist = Food.objects.exclude(id__in=chosen_food)
    pet_list = Animal.objects.filter(owner=request.user)
    form = FoodForm()
    delete_list = []
    nutrients = []
    items_name = []
    totals = {}



    # Food
    if chosen_food:
        mass_dict[0] = 0
        mass_dict[0] = round_rules(sum(mass_dict.values())+0.01)

        # Totals
        for food_id in chosen_food:
            all_nutr = NutrientsQuantity.objects.select_related(
                'nutrient').filter(
                    food__id=food_id, nutrient__is_published=True)
            for nutr in all_nutr.iterator():
                totals[nutr.nutrient.name] = round_rules(totals.get(nutr.nutrient.name, 0) + mass_dict.get(food_id, 0) * nutr.amount/100)
                                                
        
    # Pet
    if chosen_pet:
        tmp = pet_stage_calculate(chosen_pet)
        if not tmp:
            return csrf_failure(request, reason='Такой PetStage не существует')
        else:
            pet_stage, weight = tmp
            pet_stage_info = get_object_or_404(PetStage, id=pet_stage.id)
            rec_nutr = RecommendedNutrientLevelsDM.objects.filter(
                pet_stage__id=pet_stage.id).select_related('nutrient_name')
    #recomended per DryMatter
            recommended = {}
            for nutr in rec_nutr.iterator():
                recommended[nutr.nutrient_name] = nutr.nutrient_amount
                if nutr.nutrient_name.name == 'Energy':
                    nutr_amount = get_object_or_404(
                        rec_nutr, nutrient_name__name='Energy').nutrient_amount

                    recommended[nutr.nutrient_name] = round_rules(
                        nutr_amount * (weight)**(pet_stage_info.MER_power))
                if nutr.nutrient_name.name == 'Water':
                    recommended[nutr.nutrient_name] = ' '
    #recommended per 1000kcal
            rec_nutr_1000kcal = RecommendedNutrientLevels1000kcal.objects.filter(
                pet_stage__id=pet_stage.id).select_related('nutrient_name')
            recommended_1000kcal = {}
            total_energy = totals.get('Energy',0)
            
            for nutr in rec_nutr_1000kcal.iterator():
                if nutr.nutrient_name.name not in ['Energy', 'Water']:

                    recommended_1000kcal[nutr.nutrient_name] = round_rules(nutr.nutrient_amount*total_energy/1000)
                elif nutr.nutrient_name.name=='Energy':
                    recommended_1000kcal[nutr.nutrient_name] = total_energy
                else:
                    recommended_1000kcal[nutr.nutrient_name] = ' '


        # Food nutrients
        delete_list = Food.objects.filter(id__in=chosen_food)
        for elem in chosen_food:
            item = [NutrientsQuantity.objects.select_related(
                'food', 'nutrient').filter(
                    food__id=elem,
                    nutrient__is_published=True)]
            nutrients += item
            try:
                item_name = Food.objects.get(id=elem)
                items_name += [item_name]
            except Food.DoesNotExist:
                item_name = None
        columns = NutrientsName.objects.filter(
            is_published=True).order_by('order')

        # Dry_matter
        total_mass = mass_dict[0]
        total_water = totals.get('Water', 0.1)
        on_dry_matter = {}
        for nutr in totals:
            if nutr != 'Water' and nutr != 'Energy':
                measure = round_rules(
                    100*totals[nutr]/(total_mass-total_water))
                on_dry_matter[nutr] = measure
        if chosen_pet:
            on_dry_matter['Energy'] = totals.get('Energy', 1)

    # RationSave
    ration_form = RationCreateForm(request.POST or None, request=request)
    if ration_form.is_valid():
        ration_instance = Rations.objects.create(
            pet_name=chosen_pet.name,
            pet_info=pet_stage,
            pet_weight=chosen_pet.weight,
            ration_name=ration_form.cleaned_data['ration_name'],
            ration_comment=ration_form.cleaned_data['ration_comment'],
            owner=request.user)
        food_instance = Food.objects.filter(id__in=chosen_food)
        foods = (FoodData(ration=ration_instance,
                          food_name=food,
                          weight=mass_dict[food.id]) for food in food_instance)
        FoodData.objects.bulk_create(foods)
        return redirect('calc:profile', username=request.user)

    # context
    context = {"form": form,
               "showfood": foodlist,
               "mass_dict": mass_dict,
               'pet_list': pet_list}
    if chosen_food:
        context |= {
            'delete_list': delete_list,
            'columns': columns,
            'items': nutrients,
            'items_name': items_name,
            'totals': totals,
            'on_dry_matter': on_dry_matter,
                   }

    if chosen_pet:
        context |= {
            'pet_stage': pet_stage_info,
            'chosen_pet': chosen_pet,
            'recommended_nutr': recommended,
            'recommended_nutr_1000kcal': recommended_1000kcal,
            'ration_form': ration_form
        }

    response = render(request, template, context)
    response.set_cookie(key='chosen_food', value=chosen_food)
    response.set_cookie(key='mass_dict', value=mass_dict)
    if chosen_pet:
        response.set_cookie(key='chosen_pet', value=chosen_pet.id)

    return response


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
    nutrients = RecommendedNutrientLevels1000kcal.objects.all().select_related(
        'nutrient_name')
    nutrients_name = NutrientsName.objects.exclude(
        name='Water').filter(is_published=True).order_by('order')
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


def data_export(request):
    template = 'calc/export.html'
    if request.GET:
        user = request.user
        export_to_file(user)
    return render(request, template, {})


def data_import(request):
    template = 'calc/export.html'
    form = FileForm(request.POST or None)
    if form.is_valid():  # and request.user.is_staff:
        file = str(Path(__file__).resolve().parent.parent) +\
            '/files/'+form.cleaned_data['file_name']
        user = request.user
        import_from_file(file, user)
    return render(request, template, {})
