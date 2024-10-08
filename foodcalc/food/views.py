from django.shortcuts import render, get_object_or_404, redirect
from food.models import Food, NutrientsName, NutrientsQuantity
from calc.forms import FoodForm, NutrinentForm, FoodCreateForm, \
    RemoveNutrinentForm, FormNutrAdd, FormNutrRemove
from django.views.generic import DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import ast
from pages.urls import csrf_failure
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class FoodDetailView(LoginRequiredMixin, DetailView):
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


@login_required
def food_search(request, chosen_nutrients=[], mass_dict={}):
    nutrients = request.COOKIES.get('chosen_nutrients')
    mass = request.COOKIES.get('mass_dict')
    if nutrients is None:
        chosen_nutrients = []
    else:
        chosen_nutrients = ast.literal_eval(nutrients)
    if mass is None:
        mass_dict = {}
    else:
        mass_dict = ast.literal_eval(mass)

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
                mass_dict.pop(id, None)
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
                    mass_dict.get(nutrient, 0) * object.amount, 2)
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

    response = render(request, template, context)
    response.set_cookie(key='chosen_nutrients', value=chosen_nutrients)
    response.set_cookie(key='mass_dict', value=mass_dict)
    return response


@login_required
def food_create(request):
    template = 'calc/food_create.html'
    foodlist = Food.objects.all()
    form = FoodCreateForm(request.POST or None)
    if form.is_valid():
        if Food.objects.filter(
                description=form.cleaned_data.get('description')).exists():
            return csrf_failure(request,
                                reason='Продукт с таким именем уже существует')
        else:
            new_food = Food.objects.create(
                description=request.POST.get('description'),
                text=request.POST.get('text'),
                ndbNumber=0,
                fdcId=0,
                author=request.user,
                )
            if request.POST.get('based_on'):
                base_food = get_object_or_404(
                    Food, description=form.cleaned_data.get('based_on'))
                new_food.foodCategory = base_food.foodCategory
                nutrients = NutrientsQuantity.objects.filter(food=base_food)
                new_nutr = []
                for nutr in nutrients:
                    new_nutr.append(
                        NutrientsQuantity(food=new_food,
                                          nutrient=nutr.nutrient,
                                          amount=nutr.amount))
                NutrientsQuantity.objects.bulk_create(new_nutr)
            else:
                return redirect('food:food_detail', new_food.id)

    context = {
        'form': form,
        'foods': foodlist
    }
    return render(request, template, context)


@login_required
def food_update(request, food_id):
    template = 'calc/food_update.html'

    food_instance = get_object_or_404(Food, id=food_id)

    if food_instance.author != request.user:
        return csrf_failure(
            request, reason='У вас нет прав для\
                редактирования этого продукта!')

    food_nutrients = NutrientsQuantity.objects.filter(
        food=food_id, nutrient__is_published=True).select_related(
            'nutrient', 'food').order_by('nutrient__order')
    nutr_names_already_added = food_nutrients.values('nutrient__name')
    all_nutrients = NutrientsName.objects.filter(is_published=True)

    form_add = FormNutrAdd()
    form_add.fields['nutrient'].queryset = all_nutrients.exclude(
        name__in=nutr_names_already_added)
    form_remove = FormNutrRemove()
    form_remove.fields['nutrient'].queryset = all_nutrients.filter(
        name__in=nutr_names_already_added)
    print('2222222')
    if request.POST:
        print('333333')
        form_to_add = FormNutrAdd(request.POST)
        if form_to_add.is_valid():
            print('1111111')
            if not food_nutrients.filter(
                    nutrient=form_to_add.cleaned_data['nutrient']).exists():
                NutrientsQuantity.objects.create(
                    nutrient=form_to_add.cleaned_data['nutrient'],
                    amount=form_to_add.cleaned_data['amount'],
                    food=food_instance)
        else:
            form_remove = FormNutrRemove(request.POST)
            if form_remove.is_valid():
                get_object_or_404(food_nutrients,
                                  nutrient=form_remove.cleaned_data[
                                      'nutrient'].id).delete()

    context = {}
    context['food_instance'] = food_instance
    context['food_nutrients'] = food_nutrients
    context['form_add'] = form_add
    context['form_remove'] = form_remove
    return render(request, template, context)


@login_required
def food_search_by_name(request):
    template = 'calc/food_search_by_name.html'
    foodlist = Food.objects.all()
    form = FoodForm(request.GET or None)
    if form.is_valid():
        return redirect(reverse('food:food_detail', args=(
            get_object_or_404(foodlist,
                              description=form.cleaned_data['food']).id,)))
    return render(request, template, {'foodlist': foodlist, 'form': form})


class FoodDeleteView(OnlyAuthorMixin, DeleteView):
    model = Food
    template_name = 'calc/food_delete.html'

    def get_success_url(self):
        return reverse_lazy('calc:index')
