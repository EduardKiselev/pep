from django.forms.models import BaseModelForm
from django.shortcuts import render, get_object_or_404, redirect
from food.models import Food, NutrientsName, NutrientsQuantity
from calc.forms import FoodForm, NutrinentForm, \
    RemoveNutrinentForm, FormNutrAdd, FormNutrRemove
from django.views.generic import DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import ast
from calc.forms import FoodCreateForm
from django import forms
# from django.forms import formset_factory


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


class FoodCreateView(CreateView, LoginRequiredMixin):
    model = Food
    form_class = FoodCreateForm
    #fields = ['description', ]
    template_name = 'calc/food_create.html'
    
    # def get_form_kwargs(self, *args, **kwargs):
    #     kwargs = super(FoodCreateView, self).get_form_kwargs(*args, **kwargs)
    #     #kwargs['pk'] = self.kwargs['pk']
    #     print(kwargs)
    #     return kwargs

    def form_valid(self, form):
        form.instance.ndbNumber = 0
        form.instance.fdcId = 0
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        id = get_object_or_404(Food,
                               description=self.request.POST['description']).id
        return reverse_lazy('food:food_detail',
                            args=(id,))

def food_create(request):
    template = 'calc/food_create.html'
    #foodlist = Food.objects.all()
    form = FoodCreateForm(request.POST or None)
    if form.is_valid():
        if len(Food.objects.filter(description=request.POST.get('description'))) == 1:
            print('DSDFGSDFDDFSDFSDF')
            form.add_error('description', forms.ValidationError(
                '''Такой продукт уже существует'''))
        else:    
            new_food = Food.objects.create(
                description=request.POST.get('description'),
                ndbNumber=0,
                fdcId=0,
                author=request.user,
                )
            if request.POST.get('based_on'):
                print('based_on')
                base_food = get_object_or_404(Food, id=request.POST.get('based_on'))
                new_food.foodCategory = base_food.foodCategory
                nutrients = NutrientsQuantity.objects.filter(food=base_food)
                new_nutr = []
                for nutr in nutrients:
                    new_nutr.append(
                        NutrientsQuantity(food=new_food,
                                        nutrient=nutr.nutrient,
                                        amount=nutr.amount))
                print(new_nutr)
                NutrientsQuantity.objects.bulk_create(new_nutr)
            else:
                print('NONONONONON')
            return redirect('food:food_detail',new_food.id)       
        
    context = {
        'form': form
    }
    return render(request, template, context)


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
    form_add.fields['nutrient'].queryset = form_queryset.exclude(
        name__in=nutr_names_already_added)
    form_remove = FormNutrRemove()
    form_remove.fields['nutrient'].queryset = form_queryset.filter(
        name__in=nutr_names_already_added)

    if request.POST:
        if 'amount' in request.POST and float(request.POST['amount']) > 0:
            nutr_to_add = get_object_or_404(
                all_nutrients,
                name=ast.literal_eval(request.POST['nutrient'])[0])
            amount = float(request.POST['amount'])
            NutrientsQuantity.objects.create(
                nutrient=nutr_to_add, amount=amount, food=food_instance)
        else:
            nutr_quan_id = get_object_or_404(
                all_nutrients, name=ast.literal_eval(
                    request.POST['nutrient'])[0])
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
        return redirect(reverse('food:food_detail', args=(
            get_object_or_404(foodlist,
                              description=form.cleaned_data['food']).id,)))
    return render(request, template, {'foodlist': foodlist, 'form': form})


class FoodDeleteView(DeleteView, LoginRequiredMixin):
    model = Food
    template_name = 'calc/food_delete.html'

    def get_success_url(self):
        return reverse_lazy('calc:index')
