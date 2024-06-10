import json
good_key = set(['description', 'foodNutrients', 'nutrientConversionFactors', 'ndbNumber', 'fdcId', 'foodCategory'])
nutrients_set=set()
with open('foundationDownload.json') as file:
    data = json.load(file)
    data = data['FoundationFoods']
    # for elem in data:
     #   print(elem['description'])
    
    # for i in range(1):
    #     for key, value in data[i].items():
    #         if key in good_key and key != 'foodNutrients':
    #             print(key, ':', value)
    #         if key == 'foodNutrients':
    #             print('Nutrients Len:', len(data[i]['foodNutrients']))
            
    #     print('=================================')

    for i in range(1): 
        for j in range(len(data[i]['foodNutrients'])):
            nutrients_set.add(data[i]['foodNutrients'][j]['nutrient']['name'])
    
 #   print(nutrients_set)
 #   print(len(nutrients_set))
food=[]
nutrients = []
for i in range(1, 3):
    current = {}
    current['model'] = 'Food'
    current['pk'] = i
    current['fields'] = {
        "description": data[i]['description'],
        "nutrientConversionFactors": data[i]['nutrientConversionFactors'],
        "ndbNumber": data[i]['ndbNumber'],
        "fdcId": data[i]['fdcId'],
        "foodCategory": data[i]['foodCategory'],
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
    nutrients.append(current_nutr)

for elem in food:
    for key, value in elem.items():
        print(key, ':', value)

output = food + nutrients

with open('output.json', 'w') as file:
    json.dump(output, file)
