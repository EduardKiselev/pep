import json, os, sys, pprint


good_nutrients = [
    'Water',
    'Energy',
    'Protein',
    'Arginine',
    'Histidine',
    'Isoleucine',
    'Leucine',
    'Lysine',
    'Methionine',
    'Methionine + cystine',
    'Phenylalanine',
    'Phenylalanine + tyrosine',
    'Threonine',
    'Tryptophan',
    'Valine',
    'Taurine',  #
    'Total lipid (fat)',
    'Linoleic acid (omega-6)',  #
    'Arachidonic acid (omega-6)',  #
    'Alpha-linolenic acid (omega-3)',  #
    'EPA + DHA (omega-3)',  #
    'Calcium, Ca',
    'Phosphorus, P',
    'Potassium, K',
    'Sodium, Na',
    'Chloride',  #
    'Magnesium, Mg',
    'Copper, Cu',
    'Iodine, I',
    'Iron, Fe',
    'Manganese, Mn',
    'Selenium, Se',
    'Zinc, Zn',
    'Vitamin A',
    'Vitamin D3 (cholecalciferol)',
    'Vitamin E (alpha-tocopherol)',
    'Thiamin',  # B1
    'Riboflavin',  # B2
    'Pantothenic acid',  # B5
    'Vitamin B-6',
    'Vitamin B-12',
    'Niacin',  # B3
    'Folate, total',  # B9
    'Biotin',  # B7 Biotin
    'Choline, total',
    'Vitamin K (phylloquinone)',
]

calculated = {
    'Methionine': 'Methionine + cystine',
    'Cystine': 'Methionine + cystine',
    'Phenylalanine': 'Phenylalanine + tyrosine',
    'Tyrosine': 'Phenylalanine + tyrosine',
    'PUFA 20:5 n-3 (EPA)': 'EPA + DHA (omega-3)',
    'PUFA 22:6 n-3 (DHA)': 'EPA + DHA (omega-3)',
}

nutrients_order = {}
for i, nutr in enumerate(good_nutrients, 1):
   nutrients_order[nutr] = i
good_nutrients = set(good_nutrients)


food = []
nutrients = []
nutrients_measure = []
nutrients_added = set()
food_added = set()
pk_measure = 1
nutr_name_pk = 1
nutrient_id = 1
nutrients_dict = {}
nutr_name_list = []
curr_nurt_quantity_pk = 1
max_food_len = 0
max_foodcat_len = 0
food_pk = 0
num_povtor = 1
calc_nutr_list = []
calc_nutr = {}
unit_calc_nutr = {}
povtor_list = []
energy_added = set()
unit_name_in_DB_dict = {}


files = [
    ('FoodData_Central_sr_legacy_food_json_2021-10-28.json', 'SRLegacyFoods', 'legasy'),
    ('foundationDownload.json', 'FoundationFoods', 'foundation1'),   
    ('FoodData_Central_survey_food_json_2022-10-28.json', 'SurveyFoods', 'survey'),
    ('FoodData_Central_foundation_food_json_2022-10-28.json', 'FoundationFoods', 'foundation2'),
         ]

args = sys.argv
if len(args) > 2:
    raise TypeError('Too many ARGS')
elif len(args) == 2:
    if args[1] == '-a':
        flag = 'all'
    elif args[1] == '-s':
        flag = 'small'
        files = [files[1]]
    else:
        raise ValueError('No such ARG')
else:
    _len=30
    flag = 'small'


for file_info in files:
    print('Start file:',file_info[0])
    with open(file_info[0]) as file:
        data = json.load(file)
        data = data[file_info[1]]
    if flag == 'all':
        _len = len(data)
    elif flag == 'small':
        _len = 30

    for i in range(1, _len):  # all data - len(data)

        # calc nutr for previous food
        if calc_nutr:
            for calc_name, value in calc_nutr.items():
                if value > 0:
     #               print(data[i]['description'],calc_nutr)
                    current_nutr = {}
                    current_nutr['model'] = 'food.nutrientsquantity'
                    current_nutr['pk'] = curr_nurt_quantity_pk
                    curr_nurt_quantity_pk += 1
                    current_nutr['fields'] = {}
                    current_nutr['fields']['food'] = food_pk
                    current_nutr['fields']['nutrient'] = nutrients_dict[calc_name]
                    current_nutr['fields']['amount'] = value
                    nutrients.append(current_nutr)


        if data[i]['description'] in food_added:

     #       print('food was added before', num_povtor, data[i]['description'])
            povtor_list.append(data[i]['description'])
            num_povtor += 1
            descr = data[i]['description'] + '_' + file_info[2]
        else:
            descr = data[i]['description']
            food_added.add(data[i]['description'])

        current = {}
        current['model'] = 'food.food'
        food_pk += 1
        current['pk'] = food_pk
        if data[i].get('foodCategory') is not None:
            category = data[i]['foodCategory']["description"]
        else:
            category = 'None'
        current['fields'] = {
            "description": descr,
            "ndbNumber": data[i].get('ndbNumber', 0),
            "fdcId": data[i]['fdcId'],
            "foodCategory": category,
            "author": 1
        }

        food.append(current)

        

        calc_nutr = {}
        for j in range(len(data[i]['foodNutrients'])):  # это список нутриентов i-ой еды

            if data[i]['foodNutrients'][j].get('amount') is not None or data[i]['foodNutrients'][j].get('median') is not None:

                name = data[i]['foodNutrients'][j]['nutrient']['name']
                # CHANGING NAMES
                if name == 'Vitamin A, IU': name = 'Vitamin A'
                if name == 'PUFA 18:2 n-6 c,c': name = 'Linoleic acid (omega-6)'
                if name == 'PUFA 20:4': name = 'Arachidonic acid (omega-6)'
                if name == 'PUFA 18:3 n-3 c,c,c (ALA)': name = 'Alpha-linolenic acid (omega-3)'

                if name not in nutrients_added:
                    nutrients_added.add(name)
                    # for nutrinents Name and measure
                    nutr_name = {}
                    nutr_name['model'] = 'food.nutrientsname'
                    nutr_name['pk'] = nutr_name_pk
                    nutrients_dict[name] = nutr_name_pk
                    nutr_name_pk += 1
                    nutr_name['fields'] = {}
                    nutr_name['fields']['name'] = name  # создание БД имен
                    if name != 'Energy':
                        nutr_name['fields']['unit_name'] = data[i]['foodNutrients'][j]['nutrient']['unitName']
                    else:
                        nutr_name['fields']['unit_name'] = 'kcal'
                    unit_name_in_DB_dict[name] = nutr_name['fields']['unit_name']

                    if name in good_nutrients:
                        nutr_name['fields']['is_published'] = 1
                        nutr_name['fields']['order'] = nutrients_order[name]
                    else:
                        nutr_name['fields']['is_published'] = 0
                    nutr_name_list.append(nutr_name)

                    if name in calculated:
                        calc_name = calculated[name]
                        if nutrients_dict.get(calc_name) is None:
                            nutr_name = {}
                            nutr_name['model'] = 'food.nutrientsname'
                            nutr_name['pk'] = nutr_name_pk
                            nutrients_dict[calc_name] = nutr_name_pk
                            nutr_name_pk += 1
                            nutr_name['fields'] = {}
                            nutr_name['fields']['name'] = calc_name  # создание БД имен
                            nutr_name['fields']['unit_name'] = data[i]['foodNutrients'][j]['nutrient']['unitName'] 
                            unit_name_in_DB_dict[calc_name] = nutr_name['fields']['unit_name']
                            nutr_name['fields']['is_published'] = 1
                            nutr_name['fields']['order'] = nutrients_order[calc_name]
                            nutr_name_list.append(nutr_name)

                # for nutrinents_quantity
                current_nutr = {}
                current_nutr['model'] = 'food.nutrientsquantity'
                current_nutr['pk'] = curr_nurt_quantity_pk
                curr_nurt_quantity_pk += 1
                current_nutr['fields'] = {}
                current_nutr['fields']['food'] = food_pk
                current_nutr['fields']['nutrient'] = nutrients_dict[name]

                if name != 'Energy':
                    # if (data[i]['description'] == 'Pillsbury, Cinnamon Rolls with Icing, refrigerated dough'):
                    #     print('!!!!!!!!!!!!!!!!!!!!',name,data[i]['foodNutrients'][j]['nutrient']['unitName'],data[i]['foodNutrients'][j].get('amount'))
                    if data[i]['foodNutrients'][j].get('amount') is not None:
                        current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['amount']
                    else:
                        current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['median']
                    nutrients.append(current_nutr)   

                else:
                    if data[i]['foodNutrients'][j]['nutrient']['unitName'] == 'kcal' and data[i]['description'] not in energy_added:
                        if data[i]['foodNutrients'][j].get('amount') is not None:
                            current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['amount']
                        else:
                            current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['median']
                        nutrients.append(current_nutr)
                        energy_added.add(data[i]['description'])

                    elif data[i]['foodNutrients'][j]['nutrient']['unitName'] == 'kJ' and data[i]['description'] not in energy_added:
                        if data[i]['foodNutrients'][j].get('amount') is not None:                        
                            current_nutr['fields']['amount'] = round(data[i]['foodNutrients'][j]['amount']/1000*239,2)
                        else:
                            current_nutr['fields']['amount'] = round(data[i]['foodNutrients'][j]['median']/1000*239,2)
                        energy_added.add(data[i]['description'])
                        nutrients.append(current_nutr)




                # CALCULATING NUTRIENTS
                if name in calculated:
                    calc_name = calculated[name]
                    calc_nutr[calc_name] = calc_nutr.get(calc_name,0) + data[i]['foodNutrients'][j]['amount']
                        
        # printing in console process
        if len(food_added) % 500 == 0:
            print(file_info)
            print(len(food_added))
            print('nutrients_added:', len(nutrients_added))
            print('max_food_len:', max_food_len)
            print('\n\n\n')
    print('End file:', file_info[0])

#pprint.pp(nutrients_dict)

#read recommendednutrientlevels

files = [
    'cat_reformated.txt',
    'dog_reformated.txt',
    ]
pk = 1
seq_of_data = {
    'dog': [['adult_sterilized', 'Собака, взрослая стрерилизованная'],
            ['adult', 'Собака, взрослая'],
            ['early_growth', 'Щенок, ранняя стадия роста'],
            ['reproduction', 'Собака, кормящяя или беременная'],
            ['late_growth', 'Щенок, поздняя стадия роста']],
    'cat': [['adult_sterilized', 'Кошка, взростая стерилизованная'],
            ['adult', 'Кошка, взрослая'],
            ['growth', 'Котенок'],
            ['reproduction', 'Кошка, кормящяя или беременная']],
}
description = {
    'dog': 'собака',
    'cat': 'кошка'
}
recommendednutrientlevels = []

# animal_type_fixtures
animal_pk = 1
animal_type_dict = {}
animal_types = []
for type in seq_of_data:
    animal_type = {}
    animal_type['model'] = 'animal.animaltype'
    animal_type['pk'] = animal_pk
    animal_type_dict[type] = animal_pk
    animal_pk += 1
    animal_type['fields'] = {}
    animal_type['fields']['title'] = description[type]
    animal_type['fields']['description'] = description[type]
    animal_types.append(animal_type)

# pet_stages
pet_stage_pk = 1
pet_stage_dict = {}
pet_stages = []
for type_animal in seq_of_data:
    for stage, description in seq_of_data[type_animal]:
        pet_stage = {}
        pet_stage['model'] = 'animal.petstage'
        pet_stage['pk'] = pet_stage_pk
        pet_stage_dict[type_animal+'_'+stage] = pet_stage_pk
        pet_stage_pk += 1
        pet_stage['fields'] = {}
        pet_stage['fields']['pet_type'] = animal_type_dict[type_animal]
        
        if 'sterilized' in stage:
            pet_stage['fields']['sterilized'] = True

        else:
            pet_stage['fields']['sterilized'] = False
        if 'reproduction' in stage:
            pet_stage['fields']['nursing'] = True
        else:
            pet_stage['fields']['nursing'] = False
        if 'early_growth' in stage:
            age_start = 0
            age_finish = 3
        elif 'late_growth' in stage:
            age_start = 3
            age_finish = 12
        elif 'growth' in stage:
            age_start = 0
            age_finish = 12
        else:
            age_start = 12
            age_finish = 9999
        pet_stage['fields']['age_start'] = age_start
        pet_stage['fields']['age_finish'] = age_finish

        pet_stage['fields']['pet_stage'] = type_animal + '_' + stage
        pet_stage['fields']['description'] = description
        pet_stages.append(pet_stage)

# pprint.pp(pet_stage_dict)
# pprint.pp(pet_stages)

for file in files:
    if 'dog' in file:
        pet_type = 'dog'
        seq = seq_of_data['dog']
    elif 'cat' in file:
        pet_type = 'cat'
        seq = seq_of_data['cat']

    with open(file, 'r') as input:
        print('START', file)
        for line in input.readlines():
            nutrient, data = line.split('/')
            data = data.split()
            unit_name = data.pop()

            for index, d in enumerate(data):
                nutr = {}
                nutr['model'] = 'calc.recommendednutrientlevelsdm'
                nutr['pk'] = pk
                pk += 1
                nutr['fields'] = {}
                nutr['fields']['pet_type'] = animal_type_dict[pet_type]
                nutr['fields']['pet_stage'] = pet_stage_dict[pet_type+'_'+seq[index][0]]

                if nutrients_dict.get(nutrient) is None:
                    nutr_name = {}
                    nutr_name['model'] = 'food.nutrientsname'
                    nutr_name['pk'] = nutr_name_pk
                    nutrients_dict[nutrient] = nutr_name_pk
                    nutr_name_pk += 1
                    nutr_name['fields'] = {}
                    nutr_name['fields']['name'] = nutrient
                    if nutrient in ['Taurine', 'Chloride']:
                        nutr_name['fields']['unit_name'] = 'g'
                    elif nutrient in ['Biotin',]:
                        nutr_name['fields']['unit_name'] = 'µg'
                    else:
                        nutr_name['fields']['unit_name'] = 'unknown'
                        print('MAKE UNKNOWN,', nutrient, nutr_name_pk)
                    unit_name_in_DB_dict[nutrient] = nutr_name['fields']['unit_name']
                    if nutrient in good_nutrients:
                        nutr_name['fields']['is_published'] = 1
                        nutr_name['fields']['order'] = nutrients_order[nutrient]
                    else:
                        nutr_name['fields']['is_published'] = 0

                    nutr_name_list.append(nutr_name)

                nutr['fields']['nutrient_name'] = nutrients_dict[nutrient]

                if unit_name == 'IU':
                    if nutrient == 'Vitamin A': coef_nutr_to_gramm = 1 # here IU measure
                    if nutrient == 'Vitamin D3 (cholecalciferol)': coef_nutr_to_gramm = 0.000000025
                    if nutrient == 'Vitamin E (alpha-tocopherol)': coef_nutr_to_gramm = 0.00067
                elif unit_name == 'g': coef_nutr_to_gramm = 1
                elif unit_name == 'mg': coef_nutr_to_gramm = 1/1000
                elif unit_name == 'mug': coef_nutr_to_gramm = 1/1000000
                elif unit_name == 'kcal': coef_nutr_to_gramm = 1  # here kcal measure    

                unit_name_in_DB = unit_name_in_DB_dict.get(nutrient, 'unknown')

                coef_to_unit_in_DB=0
                if unit_name_in_DB == 'IU':
                    if nutrient == 'Vitamin A':
                        coef_to_unit_in_DB = 1 # here IU measure
                elif unit_name_in_DB == 'g': coef_to_unit_in_DB = 1
                elif unit_name_in_DB == 'mg': coef_to_unit_in_DB = 1/1000
                elif unit_name_in_DB == 'µg': coef_to_unit_in_DB = 1/1000000
                elif unit_name_in_DB == 'kcal': coef_to_unit_in_DB = 1 # here kcal measure
                elif unit_name_in_DB == 'unknown': coef_to_unit_in_DB = 1 # here unknown measure

                measure = float(d)*coef_nutr_to_gramm/coef_to_unit_in_DB
                counter = 0
                while measure >= 1:
                    counter -= 1
                    measure = measure/10
                while measure<1 and measure>0:
                    measure = measure*10
                    counter += 1
                measure = measure/10**counter
                measure = round(measure,counter+2)
                if measure >= 100:
                    measure = int(measure)

                nutr['fields']['nutrient_amount'] = measure

                recommendednutrientlevels.append(nutr)
              #  print(pet_type+'_'+seq[index][0],nutrient,measure,unit_name_in_DB_dict[nutrient])

output = nutr_name_list + food + nutrients +\
     animal_types + pet_stages + recommendednutrientlevels
print('Writing Data')
write_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/foodcalc/'
if flag == 'small':
    filename = 'small_data.json'
elif flag == 'all':
    filename = 'all_data.json'

with open(write_dir+filename, 'w') as file:
    json.dump(output, file)

