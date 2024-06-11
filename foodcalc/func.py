import json
# good_key = set(['description', 'foodNutrients', 'nutrientConversionFactors', 'ndbNumber', 'fdcId', 'foodCategory'])
with open('foundationDownload.json') as file:
    data = json.load(file)
    data = data['FoundationFoods']

food = []
nutrients = []
nutrients_measure = []
nutrients_added = set()
pk_measure = 1
for i in range(1, len(data)):
    current = {}
    current['model'] = 'Food'
    current['pk'] = i
    current['fields'] = {
        "description": data[i]['description'],
        "ndbNumber": data[i]['ndbNumber'],
        "fdcId": data[i]['fdcId'],
        "foodCategory": data[i]['foodCategory']["description"],
    }
    food.append(current)
    current_nutr = {}
    current_nutr['model'] = 'Nutrients'
    current_nutr['pk'] = i
    current_nutr['fields'] = {}
    for j in range(len(data[i]['foodNutrients'])):  # это список
        if data[i]['foodNutrients'][j].get('amount') is not None:
            name = data[i]['foodNutrients'][j]['nutrient']['name']
            value = data[i]['foodNutrients'][j]['amount']
            current_nutr['fields'][name] = value
            if name not in nutrients_added:
                nutrients_added.add(name)
                nutr_measure = {}
                nutr_measure['model'] = 'NutrientsMeasure'
                nutr_measure['pk'] = pk_measure
                pk_measure += 1
                nutr_measure['fields'] = {}
                nutr_measure['fields']['nutr_name'] = name
                nutr_measure['fields']['unit_name'] = data[i]['foodNutrients'][j]['nutrient']['unitName']
                nutrients_measure.append(nutr_measure)
    nutrients.append(current_nutr)

output = food + nutrients + nutrients_measure

with open('output.json', 'w') as file:
    json.dump(output, file)
