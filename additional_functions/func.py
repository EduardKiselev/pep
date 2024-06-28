import json

good_nutrients = ([
    'Water',
    'Energy',
    'Protein',
    'Arginine',
    'Histidine',
    'Isoleucine',
    'Leucine',
    'Lysine',
    'Methionine',
    'Phenylalanine',
    'Threonine',
    'Tryptophan',
    'Valine',
    'Taurine', #
    'Total fat (NLEA)',
    'Linoleic acid (ω-6)', #
    'Arachidonic acid (ω-6)', #
    'Alpha-linolenic acid (ω-3)', #
    'EPA+DHA(ω-3)', #
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
    'Vitamin D (D2 + D3)',
    'Vitamin E (alpha-tocopherol)',
    'Vitamin B-1', #
    'Vitamin B-2',#
    'Vitamin B-5',#
    'Vitamin B-6',
    'Vitamin B-12',
    'Vitamin B-3',#
    'Vitamin B-9',#
    'Vitamin B-7',#
    'Choline, total',
    'Vitamin K',    #
])
nutrients_order = {}
for i,nutr in enumerate(good_nutrients, 1):
   nutrients_order[nutr] = i
good_nutrients = set(good_nutrients)

food = []
nutrients = []
nutrients_measure = []
nutrients_added = set()
food_added=set()
pk_measure = 1
nutr_name_pk=1
nutrient_id = 1
nutrients_dict = {}
nutr_name_list = []
curr_nurt_quantity_pk = 1
max_food_len=0
max_foodcat_len=0
food_pk=0
num_povtor=1

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

    for i in range(1, 30): #all data - len(data)
        if data[i]['description'] in food_added:
            print('food was added before', num_povtor)
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

            for j in range(len(data[i]['foodNutrients'])):  # это список нутриентов i-ой еды

                if data[i]['foodNutrients'][j].get('amount') is not None or data[i]['foodNutrients'][j].get('median') is not None:

                    name = data[i]['foodNutrients'][j]['nutrient']['name']
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


output = nutr_name_list + food + nutrients

with open('small_data.json', 'w') as file:
    json.dump(output, file)
    #    json.dump(nutrients_added, file)
