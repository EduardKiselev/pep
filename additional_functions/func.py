import json
from decimal import Decimal
# good_key = set(['description', 'foodNutrients', 'nutrientConversionFactors', 'ndbNumber', 'fdcId', 'foodCategory'])
with open('foundationDownload.json') as file:
    data = json.load(file)
    data = data['FoundationFoods']

food = []
nutrients = []
nutrients_measure = []
nutrients_added = set()
pk_measure = 1
nutr_name_pk=1
nutrient_id = 1
nutrients_dict = {}
nutr_name_list = []
curr_nurt_quantity_pk = 1
for i in range(1, len(data)):
    current = {}
    current['model'] = 'calc.food'
    current['pk'] = i
    current['fields'] = {
        "description": data[i]['description'],
        "ndbNumber": data[i]['ndbNumber'],
        "fdcId": data[i]['fdcId'],
        "foodCategory": data[i]['foodCategory']["description"],
    }
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
                nutr_name_list.append(nutr_name)

            # for nutrinents_quantity
            current_nutr = {}
            current_nutr['model'] = 'calc.nutrientsquantity'
            current_nutr['pk'] = curr_nurt_quantity_pk
            curr_nurt_quantity_pk += 1
            current_nutr['fields'] = {}
            current_nutr['fields']['food_id'] = i
            current_nutr['fields']['nutrient_id'] = nutrients_dict[name]
            if data[i]['foodNutrients'][j].get('amount') is not None:
                current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['amount']
            else:
                current_nutr['fields']['amount'] = data[i]['foodNutrients'][j]['median']
            nutrients.append(current_nutr)

# словарь нутриентов
# nutrients_count = {}
# for nutrient in nutrients_added:
#     nutrients_count[nutrient] = 0
print(len(nutrients_added))
output = nutr_name_list + food + nutrients

with open('converted_load_data.json', 'w') as file:
    json.dump(output, file)
#    json.dump(nutrients_added, file)
