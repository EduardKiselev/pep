from calc.models import Rations, FoodData
from food.models import Food, NutrientsName, NutrientsQuantity
from animal.models import AnimalType, PetStage, Animal
from django.shortcuts import get_object_or_404
import json
from django.core import serializers
from pathlib import Path
from datetime import datetime
import ast


def round_rules(number):
    if number >= 100:
        return int(number)
    if number >= 10:
        return round(number, 1)
    else:
        return round(number, 2)


def pet_stage_calculate(animal):
    birthday = animal.birthday
    weight = animal.weight
    pet_type = animal.type
    nursing = animal.nursing
    sterilized = animal.sterilized

    age = round((datetime.now().date()-birthday).days/30.41, 1)

    pet_stage = PetStage.objects.filter(
        sterilized=sterilized,
        nursing=nursing,
        age_finish__gt=age,
        age_start__lt=age,
        pet_type=pet_type)
    if len(pet_stage) == 1:
        return pet_stage[0], weight
    else:
        return None


def export_to_file(user):
    queries = []
    food_query = Food.objects.filter(author=user)
    queries.append(food_query)
    queries.append(NutrientsQuantity.objects.filter(food__in=food_query))
    queries.append(NutrientsName.objects.all())
    ration_query = Rations.objects.filter(owner=user)
    queries.append(ration_query)
    queries.append(FoodData.objects.filter(ration__in=ration_query))
    queries.append(Animal.objects.filter(owner=user))
    queries.append(PetStage.objects.all())
    queries.append(AnimalType.objects.all())
    res = []
    for q in queries:
        if q:
            data_json = serializers.serialize('json', q)
            res.extend(json.loads(data_json))
    res = json.dumps(res, ensure_ascii=False)

    directory = str(Path(__file__).resolve().parent.parent)
    filename = '/files/'+user.username+'_export' +\
        str(datetime.now().date())+'.json'
    file = directory + filename
    with open(file, 'w', encoding='utf-8') as output:
        print(res, file=output)
    print('export Finished')
    return


def import_from_file(file, user):
    nutrients_query = NutrientsName.objects.all()
    petstage_query = PetStage.objects.all()
    animaltype_query = AnimalType.objects.all()
    food_query = Food.objects.all()
    rations_query = Rations.objects.filter(owner=user)

    convert_nutrients_name = {}  # key:in export,
    convert_animaltype = {}      # value:in fixtures for all dicts
    convert_petstage = {}
    convert_food = {}
    convert_rations = {}

    user_food = []
    user_nutr_quan = []
    user_food_names = set()

    user_rations = []
    user_fooddata = []
    user_rations_names = set()

    with open(file, 'r') as input_file:
        all_data = json.load(input_file)
        for data in all_data:
            if data['model'] == 'food.nutrientsname':
                convert_nutrients_name[data['pk']] = nutrients_query.filter(
                    name=data['fields']['name']).get().id
            if data['model'] == 'animal.animaltype':
                convert_animaltype[data['pk']] = animaltype_query.filter(
                    title=data['fields']['title']).get().id
            if data['model'] == 'animal.petstage':
                convert_petstage[data['pk']] = petstage_query.filter(
                    pet_stage=data['fields']['pet_stage']).get().id
        for data in all_data:
            if data['model'] == 'food.food' and not food_query.filter(
                    description=data['fields']['description']).exists():
                user_food_names.add(data['fields']['description'])
                user_food.append(Food(
                    description=data['fields']['description'],
                    text=data['fields'].get('text'),
                    ndbNumber=data['fields'].get('ndbNumber'),
                    fdcId=data['fields'].get('fdcId'),
                    foodCategory=data['fields'].get('foodCategory'),
                    author=user
                    ))
        Food.objects.bulk_create(user_food)
        new_food_query = Food.objects.filter(description__in=user_food_names)

        for data in all_data:
            if data['model'] == 'food.food':
                convert_food[data['pk']] = food_query.filter(
                    description=data['fields']['description']).get().id

        if new_food_query:
            for data in all_data:
                if data['model'] == 'food.nutrientsquantity':
                    id_food_in_file = data['fields']['food']
                    id_nutr_in_file = data['fields']['nutrient']
                    user_nutr_quan.append(NutrientsQuantity(
                        food=get_object_or_404(
                            new_food_query,
                            id=convert_food[id_food_in_file]),
                        nutrient=get_object_or_404(
                            nutrients_query,
                            id=convert_nutrients_name[id_nutr_in_file]),
                        amount=data['fields']['amount']
                    ))
            print(user_nutr_quan)
            NutrientsQuantity.objects.bulk_create(user_nutr_quan)
        print('convert_nutrients_name', convert_nutrients_name)
        print('convert_animaltype', convert_animaltype)
        print('convert_petstage', convert_petstage)
        print('convert_food', convert_food)
        print('user_food', user_food)
        for data in all_data:
            if data['model'] == 'calc.rations':
                id_petstage_in_file = data['fields']['pet_info']
                user_rations_names.add(data['fields']['ration_name'])
                if not rations_query.filter(
                        ration_name=data['fields']['ration_name']).exists():
                    user_rations.append(Rations(
                        owner=user,
                        pet_name=data['fields']['pet_name'],
                        pet_info=get_object_or_404(
                            petstage_query, id=convert_petstage[
                                id_petstage_in_file]),
                        ration_name=data['fields']['ration_name'],
                        ration_comment=data['fields'].get('ration_comment')
                    ))
        Rations.objects.bulk_create(user_rations)

        new_rations_query = Rations.objects.filter(
            ration_name__in=user_rations_names)
        print('new_rations!!!!', new_rations_query)
        if new_rations_query:
            for data in all_data:
                if data['model'] == 'calc.rations':
                    convert_rations[data['pk']] =\
                        new_rations_query.filter(
                            ration_name=data['fields']['ration_name']).get().id
        print('convert_rations', convert_rations)
        for data in all_data:
            if data['model'] == 'calc.fooddata':
                id_ration_in_file = data['fields']['ration']
                id_food_in_file = data['fields']['food_name']
                user_fooddata.append(FoodData(
                    ration=get_object_or_404(
                        rations_query, id=convert_rations[id_ration_in_file]),
                    food_name=get_object_or_404(
                        food_query, id=convert_food[id_food_in_file]),
                    weight=data['fields'].get('weight')
                ))
        FoodData.objects.bulk_create(user_fooddata)

        if data['model'] == 'animal.animal':
            pass

    print('Import Finished')
    return


def initialize(ration, request):
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
    else:
        chosen_food = []
        mass_dict = {}
        chosen_pet = None
        instance = FoodData.objects.filter(
            ration=ration).select_related('food_name')
        for elem in instance:
            chosen_food.append(elem.food_name.id)
            mass_dict[elem.food_name.id] = elem.weight
    return mass_dict, chosen_food, chosen_pet
