from django.shortcuts import render, get_object_or_404, redirect
from calc.models import Food, NutrientsName, NutrientsQuantity, User, Animal, \
    RecommendedNutrientLevelsDM, PetStage, Rations, FoodData
from calc.forms import FoodForm, RemoveFoodForm, NutrinentForm, \
    RemoveNutrinentForm, ProfileForm, PetForm, RationNameForm, \
        FormNutrAdd, FormNutrRemove
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django import forms
from calc.utils import pet_stage_calculate
import ast
# from django.forms import formset_factory
import pprint


class FoodDetailView(DetailView):
    model = Food
    template_name = 'calc/detail.html'
    pk_url_kwarg = 'food_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nutrients = NutrientsQuantity.objects.select_related(
            'nutrient', 'food').filter(
            food_id=self.kwargs.get(self.pk_url_kwarg),
            nutrient__is_published=True).order_by('nutrient__order')
        context['nutrients'] = nutrients
        return context

    def get(self, *args, **kwargs):
        if 'update_food' in self.request.GET:
            print('redirect_update')
            return redirect(reverse('calc:food_update',
                                    args=(self.kwargs.get(
                                        self.pk_url_kwarg),)))
        return super().get(*args, **kwargs)


class RationDetailView(DetailView):
    model = Rations
    template_name = 'calc/detail.html'
    pk_url_kwarg = 'ration_id'

    def get(self, *args, **kwargs):
        if 'open_in_calc' in self.request.GET:
            print('redirect')
            return redirect(reverse('calc:calc',
                                    args=(self.kwargs.get(
                                        self.pk_url_kwarg),)))
        if 'delete' in self.request.GET:
            print('redirect delete')
            return redirect(reverse('calc:ration_delete',
                                    args=(self.kwargs.get(
                                        self.pk_url_kwarg),)))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        food_data = FoodData.objects.select_related(
            'food_name', 'ration').filter(
            ration__id=self.kwargs.get(self.pk_url_kwarg))
        context['food_data'] = food_data
        context['ration'] = get_object_or_404(Rations,
                                              id=self.kwargs.get(
                                                  self.pk_url_kwarg))
        return context


class RationDeleteView(DeleteView):
    model = Rations
    template_name = 'calc/delete.html'
    pk_url_kwarg = 'ration_id'
    success_url = reverse_lazy('calc:index')
    # def get(self, *args, **kwargs):
    #    return redirect(reverse('calc:profile', args=(self.request.user,)))


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    fields = ['name', 'type', 'nursing', 'sterilized', 'weight', 'birthday']
    template_name = 'animal/create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        sterilized = form.cleaned_data.get('sterilized')
        nursing = form.cleaned_data.get('nursing')
        if sterilized*nursing:
            form.add_error('nursing', forms.ValidationError(
                '''не возможно быть одновременно стерилизованным
                и кормящим/беременным'''))
            return super().form_invalid(form)

        name = form.cleaned_data.get('name')
        if len(Animal.objects.filter(name=name, owner=self.request.user)) == 1:
            form.add_error('name',
                           forms.ValidationError('''У вас уже есть питомец
                                                 с этим именем'''))
            return super().form_invalid(form)

        form.instance.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('calc:profile', args=(self.request.user,))


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    model = Animal
    template_name = 'animal/create.html'
    fields = ['name', 'type', 'nursing', 'sterilized', 'weight', 'birthday']

    def form_valid(self, form):
        self.object = form.save(commit=False)

        sterilized = form.cleaned_data.get('sterilized')
        nursing = form.cleaned_data.get('nursing')
        if sterilized*nursing:
            form.add_error('nursing',
                           forms.ValidationError(
                               '''не возможно быть одновременно стерилизованным
                                                 и кормящим/беременным'''))
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
        ration_id = list(request.GET.keys())[0]
        return redirect(reverse('calc:ration_detail', args=(ration_id,)))

    profile = get_object_or_404(User, username=username)
    animals = Animal.objects.filter(owner=profile)
    foods = FoodData.objects.select_related(
        'ration', 'food_name').filter(ration__owner=profile)
    rations_list = set()
    rations = Rations.objects.filter(id__in=rations_list)
    for elem in foods.values('ration'):
        rations_list.add(elem['ration'])
    rations = Rations.objects.filter(id__in=rations_list)
    print(rations)
    context = {'profile': profile,
               'animals': animals,
               'foods': foods,
               'rations': rations}
    return render(request, template, context)


@login_required
def calc(request, ration=0):
    template = 'calc/calc.html'
    if ration == 0:
        foods = request.COOKIES.get('chosen_food')
        mass = request.COOKIES.get('mass_dict')
        pet = request.COOKIES.get('chosen_pet')
        if foods is None:
            chosen_food = []
        else:
            foods = ast.literal_eval(foods)
            chosen_food = foods
        if mass is None:
            mass_dict = {}
        else:
            mass = ast.literal_eval(mass)
            mass_dict = mass
        if pet is None:
            chosen_pet = None
        else:
            foods = ast.literal_eval(pet)
            try:
                chosen_pet = Animal.objects.get(id=pet)
                if chosen_pet.owner != request.user:
                    chosen_pet = None
            except Animal.DoesNotExist:
                chosen_pet = None
            # chosen_pet = get_object_or_404(Animal, id=pet)
            # if chosen_pet.owner != request.user:
            #    chosen_pet = None
    else:
        chosen_food = []
        mass_dict = {}
        chosen_pet = None
        instance = FoodData.objects.filter(
            ration=ration).select_related('food_name')
        for elem in instance:
            chosen_food.append(elem.food_name.id)
            mass_dict[elem.food_name.id] = elem.weight

    print('chosen_food:', chosen_food)
    print('mass_dict:', mass_dict)
    print('chosen_pet:', chosen_pet)

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
                    if mass > 0:
                        mass_dict[food_id] = mass

    foodlist = Food.objects.exclude(id__in=chosen_food)
    pet_list = Animal.objects.filter(owner=request.user)
    form = FoodForm()
    delete_list = []
    nutrients = []
    items_name = []
    totals = {}

    # Pet
    if chosen_pet:
        tmp = pet_stage_calculate(chosen_pet)
        if not tmp:
            return redirect('calc:index')
        else:
            pet_stage, weight = tmp
            pet_stage_info = get_object_or_404(PetStage, id=pet_stage.id)
            rec_nutr = RecommendedNutrientLevelsDM.objects.filter(
                pet_stage__id=pet_stage.id).select_related('nutrient_name')
            recommended = {}
            for nutr in rec_nutr.iterator():
                recommended[nutr.nutrient_name] = nutr.nutrient_amount
                if nutr.nutrient_name.name == 'Energy':
                    nutr_amount = get_object_or_404(
                        rec_nutr, nutrient_name__name='Energy').nutrient_amount
                    recommended[nutr.nutrient_name] = round(
                        nutr_amount * (weight)**(0.75), 2)
                if nutr.nutrient_name.name == 'Water':
                    recommended[nutr.nutrient_name] = ' '

    # Food
    if chosen_food:
        mass_dict[0] = 0
        mass_dict[0] = sum(mass_dict.values())

        # Totals
        for food_id in chosen_food:
            all_nutr = NutrientsQuantity.objects.select_related(
                'nutrient').filter(
                    food__id=food_id, nutrient__is_published=True)
            for nutr in all_nutr.iterator():
                totals[nutr.nutrient.name] = round(
                    totals.get(nutr.nutrient.name, 0)
                    + mass_dict.get(food_id, 0) * nutr.amount/100, 2
                                                )

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
        total_water = totals.get('Water', 1)
        on_dry_matter = {}
        for nutr in totals:
            if nutr != 'Water' and nutr != 'Energy':
                measure = round(100*totals[nutr]/(total_mass-total_water), 2)
                if measure >= 10:
                    measure = round(measure, 1)
                if measure >= 100:
                    measure = int(measure)
                on_dry_matter[nutr] = measure
        if chosen_pet:
            on_dry_matter['Energy'] = totals.get('Energy',1)

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
        }

    if 'ration_name' in request.POST.keys():
        form = RationNameForm(request.POST or None)
        if form.is_valid():
            ration_instance = Rations.objects.create(
                pet_name=chosen_pet.name, pet_info=pet_stage,
                ration_name=request.POST['ration_name'], owner=request.user)
            food_instance = Food.objects.filter(id__in=chosen_food)
            foods = (FoodData(
                ration=ration_instance, food_name=food,
                weight=mass_dict[food.id]) for food in food_instance)
        FoodData.objects.bulk_create(foods)

        return redirect('calc:profile', username=request.user)

    response = render(request, template, context)
    response.set_cookie(key='chosen_food', value=chosen_food)
    response.set_cookie(key='mass_dict', value=mass_dict)
    if chosen_pet:
        response.set_cookie(key='chosen_pet', value=chosen_pet.id)
    return response


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
    nutrient_list = NutrientsName.objects.filter(is_published=True).exclude(
        id__in=chosen_nutrients)
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
        all_food = sorted(totals.items(), key=lambda x: x[1],
                          reverse=True)[:75]
        paginator = Paginator(all_food, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        add_context = {'delete_list': delete_list,
                       'page_obj': page_obj,
                       'nutrients': nutrients}

    context = {'nutrient_list': nutrient_list,
               'chosen_nutrients': chosen_nutrients,
               'mass_dict': mass_dict}
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
    nutrients = RecommendedNutrientLevelsDM.objects.all().select_related(
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


class FoodCreateView(CreateView, LoginRequiredMixin):
    model = Food
    fields = ['description',]
    template_name = 'calc/food_create.html'

    def form_valid(self, form):
        form.instance.ndbNumber = 0
        form.instance.fdcId = 0
        return super().form_valid(form)

    def get_success_url(self):
        id = get_object_or_404(Food, description=self.request.POST['description']).id
        return reverse_lazy('calc:food_detail',
                            args=(id,))


@login_required
def food_update(request, food_id):
    template = 'calc/food_update.html'

    food_instance = get_object_or_404(Food, id=food_id)

    food_nutrients = NutrientsQuantity.objects.filter(
        food=food_id, nutrient__is_published=True).select_related(
            'nutrient', 'food').order_by('nutrient__order')
    nutr_names_already_added = food_nutrients.values('nutrient__name')
    all_nutrients = NutrientsName.objects.all()
    base_queryset = all_nutrients.values('id', 'name', 'unit_name').filter(
            is_published=True)
    form_queryset = base_queryset.values_list('name', 'unit_name')
    form_add = FormNutrAdd()
    form_add.fields['nutrient'].queryset = form_queryset.exclude(name__in=nutr_names_already_added)
    form_remove = FormNutrRemove()
    form_remove.fields['nutrient'].queryset = form_queryset.filter(name__in=nutr_names_already_added)

    if request.POST:
        if 'amount' in request.POST and float(request.POST['amount']) > 0:
            nutr_to_add = get_object_or_404(all_nutrients, name=ast.literal_eval(request.POST['nutrient'])[0])
            amount = float(request.POST['amount'])
            NutrientsQuantity.objects.create(nutrient=nutr_to_add, amount=amount, food=food_instance)
        else:
            nutr_quan_id = get_object_or_404(all_nutrients, name=ast.literal_eval(request.POST['nutrient'])[0])
            get_object_or_404(food_nutrients, nutrient=nutr_quan_id).delete()

    context = {}
    context['food_instance'] = food_instance
    context['food_nutrients'] = food_nutrients
    context['form_add'] = form_add
    context['form_remove'] = form_remove
    return render(request, template, context)


def food_search_by_name(request):
    template = 'calc/food_search_by_name.html'
    foodlist = Food.objects.all()
    form = FoodForm(request.GET or None)
    if form.is_valid():
        return redirect(reverse('calc:food_detail', args=(
            get_object_or_404(foodlist,
                              description=form.cleaned_data['food']).id,)))
    return render(request, template, {'foodlist': foodlist, 'form': form})
