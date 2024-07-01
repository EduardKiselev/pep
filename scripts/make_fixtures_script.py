import json
import pprint

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
    'Vitamin A, IU',
    'Vitamin D3 (cholecalciferol)',
    'Vitamin E (alpha-tocopherol)',
    'Thiamine',  # B1
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

files = [
    ('FoodData_Central_survey_food_json_2022-10-28.json', 'SurveyFoods'),
    ('FoodData_Central_sr_legacy_food_json_2021-10-28.json', 'SRLegacyFoods'),
    ('FoodData_Central_foundation_food_json_2022-10-28.json', 'FoundationFoods'),
    ('foundationDownload.json', 'FoundationFoods'),
         ]

for file_info in files:

    with open(file_info[0]) as file:
        data = json.load(file)
        data = data[file_info[1]]

    for i in range(1, 30):  # all data - len(data)

        # calc nutr for previous food
        if calc_nutr:
            for calc_name, value in calc_nutr.items():
                if value > 0:
     #               print(data[i]['description'],calc_nutr)
                    current_nutr = {}
                    current_nutr['model'] = 'calc.nutrientsquantity'
                    current_nutr['pk'] = curr_nurt_quantity_pk
                    curr_nurt_quantity_pk += 1
                    current_nutr['fields'] = {}
                    current_nutr['fields']['food'] = food_pk
                    current_nutr['fields']['nutrient'] = nutrients_dict[calc_name]
                    current_nutr['fields']['amount'] = value
                    nutrients.append(current_nutr)


        if data[i]['description'] in food_added:
   #         print('food was added before', num_povtor, data[i]['description'])
            num_povtor += 1
        else:
            food_added.add(data[i]['description'])
            current = {}
            current['model'] = 'calc.food'
            food_pk += 1
            current['pk'] = food_pk
            current['fields'] = {
                "description": data[i]['description'],
                "ndbNumber": data[i].get('ndbNumber',0),
                "fdcId": data[i]['fdcId'],
          #     "foodCategory": data[i]['foodCategory']["description"],
            }
            max_food_len = max(max_food_len, len(data[i]['description']))
         #   max_foodcat_len = max(max_foodcat_len, len(data[i]['foodCategory']["description"]))
            food.append(current)

            

            calc_nutr = {}
            for j in range(len(data[i]['foodNutrients'])):  # это список нутриентов i-ой еды

                if data[i]['foodNutrients'][j].get('amount') is not None or data[i]['foodNutrients'][j].get('median') is not None:

                    name = data[i]['foodNutrients'][j]['nutrient']['name']
                    # CHANGING NAMES
                    if name == 'PUFA 18:2 n-6 c,c': name = 'Linoleic acid (omega-6)'
                    if name == 'PUFA 20:4 n-6': name = 'Arachidonic acid (omega-6)'
                    if name == 'PUFA 18:3 n-3 c,c,c (ALA)': name = 'Alpha-linolenic acid (omega-3)'

                    if name not in nutrients_added:
                        nutrients_added.add(name)
                        # for nutrinents Name and measure
                        nutr_name = {}
                        nutr_name['model'] = 'calc.nutrientsname'
                        nutr_name['pk'] = nutr_name_pk
                        nutrients_dict[name] = nutr_name_pk
                        nutr_name_pk += 1
                        nutr_name['fields'] = {}
                        nutr_name['fields']['name'] = name  # создание БД имен
                        nutr_name['fields']['unit_name'] = data[i]['foodNutrients'][j]['nutrient']['unitName']
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
                                nutr_name['model'] = 'calc.nutrientsname'
                                nutr_name['pk'] = nutr_name_pk
                                nutrients_dict[calc_name] = nutr_name_pk
                                nutr_name_pk += 1
                                nutr_name['fields'] = {}
                                nutr_name['fields']['name'] = calc_name  # создание БД имен
                                nutr_name['fields']['unit_name'] = data[i]['foodNutrients'][j]['nutrient']['unitName']  
                                nutr_name['fields']['is_published'] = 1
                                nutr_name['fields']['order'] = nutrients_order[calc_name]
                                nutr_name_list.append(nutr_name)

                    # for nutrinents_quantity
                    current_nutr = {}
                    current_nutr['model'] = 'calc.nutrientsquantity'
                    current_nutr['pk'] = curr_nurt_quantity_pk
                    curr_nurt_quantity_pk += 1
                    current_nutr['fields'] = {}
                    current_nutr['fields']['food'] = food_pk
                    current_nutr['fields']['nutrient'] = nutrients_dict[name]
                    if data[i]['foodNutrients'][j].get('amount') is not None:
                        current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['amount']
                    else:
                        current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['median']
                    nutrients.append(current_nutr)


                    # CALCULATING NUTRIENTS
                    if name in calculated:
                        calc_name = calculated[name]
                        calc_nutr[calc_name] = calc_nutr.get(calc_name,0) + data[i]['foodNutrients'][j]['amount']
                        

    # словарь нутриентов
    # nutrients_count = {}
    # for nutrient in nutrients_added:
    #     nutrients_count[nutrient] = 0
        if len(food_added) % 500 == 0:
            print(file_info)
            print(len(food_added))
            print('nutrients_added:', len(nutrients_added))
            print('max_food_len:', max_food_len)
    #     print('max_foodcat_len:', max_foodcat_len)
            print('\n\n\n')

#pprint.pp(nutrients_dict)

#read recommendednutrientlevels

files = ['dog.txt', 'cat.txt']
pk = 1
seq_of_data = {
    'dog': ['adult_sterilized', 'adult', 'early_growth', 'late_growth', 'reproduction'],
    'cat': ['adult_sterilized', 'adult', 'growth', 'reproduction'],
}
recommendednutrientlevels = []

# animal_type_fixtures
animal_pk = 1
animal_type_dict = {}
animal_types = []
for type in seq_of_data:
    animal_type = {}
    animal_type['model'] = 'calc.animaltype'
    animal_type['pk'] = animal_pk
    animal_type_dict[type] = animal_pk
    animal_pk += 1
    animal_type['fields'] = {}
    animal_type['fields']['title'] = type
    animal_type['fields']['description'] = ''
    animal_types.append(animal_type)

# print(animal_type_dict)

# pet_stages
pet_stage_pk = 1
pet_stage_dict = {}
pet_stages = []
for type_animal in seq_of_data:
    for stage in seq_of_data[type_animal]:
        pet_stage = {}
        pet_stage['model'] = 'calc.petstage'
        pet_stage['pk'] = pet_stage_pk
        pet_stage_dict[type_animal+'_'+stage] = pet_stage_pk
        pet_stage_pk += 1
        pet_stage['fields'] = {}
        pet_stage['fields']['pet_type'] = animal_type_dict[type_animal]
        
        print(stage)
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

        pet_stage['fields']['pet_stage'] = stage
        pet_stages.append(pet_stage)

# pprint.pp(pet_stage_dict)
# pprint.pp(pet_stages)

for file in files:
    if file == 'dog.txt':
        pet_type = 'dog'
        seq = seq_of_data['dog']
    elif file == 'cat.txt':
        pet_type = 'cat'
        seq = seq_of_data['cat']

    with open(file, 'r') as input:
        print('START', file)
        for line in input.readlines():
            nutrient, data = line.split('/')
            data = data.split()

            for index, d in enumerate(data):
                nutr = {}
                nutr['model'] = 'calc.recommendednutrientlevelsdm'
                nutr['pk'] = pk
                pk += 1
                nutr['fields'] = {}
                nutr['fields']['pet_type'] = animal_type_dict[pet_type]
                nutr['fields']['pet_stage'] = pet_stage_dict[pet_type+'_'+seq[index]]
                nutr['fields']['nutrient_amount'] = float(d)
                if nutrients_dict.get(nutrient) is None:
                    nutr_name = {}
                    nutr_name['model'] = 'calc.nutrientsname'
                    nutr_name['pk'] = nutr_name_pk
                    nutrients_dict[nutrient] = nutr_name_pk
                    nutr_name_pk += 1
                    nutr_name['fields'] = {}
                    nutr_name['fields']['name'] = nutrient 
                    nutr_name['fields']['unit_name'] = 'unknown'
                #    print('MAKE UNKNOWN,', nutrient, nutr_name_pk)
                    if nutrient in good_nutrients:
                        nutr_name['fields']['is_published'] = 1
                        nutr_name['fields']['order'] = nutrients_order[nutrient]
                    else:
                        nutr_name['fields']['is_published'] = 0
                    nutr_name_list.append(nutr_name)

                nutr['fields']['nutrient_name'] = nutrients_dict[nutrient]
                recommendednutrientlevels.append(nutr)


output = nutr_name_list + food + nutrients +\
     animal_types + pet_stages + recommendednutrientlevels

with open('small_data.json', 'w') as file:
    json.dump(output, file)

