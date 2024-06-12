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
        if data[i]['foodNutrients'][j].get('amount') is not None:

            name = data[i]['foodNutrients'][j]['nutrient']['name']
            if name not in nutrients_added:
                nutrients_added.add(name)
                #for nutrients measure
                nutr_measure = {}
                nutr_measure['model'] = 'calc.nutrientsmeasure'
                nutr_measure['pk'] = pk_measure
                pk_measure += 1
                nutr_measure['fields'] = {}
                nutr_measure['fields']['nutrient_id'] = nutrient_id
                nutr_measure['fields']['unit_name'] = data[i]['foodNutrients'][j]['nutrient']['unitName']
                nutrients_measure.append(nutr_measure) #создание попугаев измерения
                
                # for nutrinents Name
                nutr_name = {}
                nutr_name['model'] = 'calc.nutrientsname'
                nutr_name['pk'] = nutr_name_pk               
                nutr_name['fields'] = {}
                nutr_name_pk += 1
                nutr_name['fields']['nutrient_id'] = nutrient_id
                nutrients_dict[name] = nutrient_id
                nutrient_id += 1  # increment for next nutrinent
                nutr_name['fields']['name'] = name  # создание БД имен
                nutr_name_list.append(nutr_name)
            
            current_nutr = {}
            current_nutr['model'] = 'calc.nutrientsquantity'
            current_nutr['pk'] = curr_nurt_quantity_pk
            curr_nurt_quantity_pk += 1
            current_nutr['fields'] = {}
            current_nutr['fields']['food_id'] = i
            current_nutr['fields']['nutrient_id'] = nutrients_dict[name]
            amount = data[i]['foodNutrients'][j]['amount']
            current_nutr['fields']['amount'] = amount
            nutrients.append(current_nutr)

# словарь нутриентов
# nutrients_count = {}
# for nutrient in nutrients_added:
#     nutrients_count[nutrient] = 0

output = nutr_name_list + food + nutrients + nutrients_measure

with open('converted_load_data.json', 'w') as file:
    json.dump(output, file)
#    json.dump(nutrients_added, file)
