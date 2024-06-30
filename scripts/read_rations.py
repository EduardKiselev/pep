import json
import pprint

files = ['dog.txt', 'cat.txt']
pk = 1
dog_seq_of_data = ['adult_sterilized', 'adult', 'early_growth', 'late_growth']
cat_seq_of_data = ['adult_sterilized', 'adult', 'growth/reproduction']
result = []

for file in files:
    if file == 'dog.txt':
        pet_type = 'dog'
        seq = dog_seq_of_data
    elif file == 'cat.txt':
        pet_type = 'cat'
        seq = cat_seq_of_data

    with open(file, 'r') as input:
        print('START', file)
        for line in input.readlines():
            nutrient, data = line.split(',')
            data = data.split()
   #         print(nutrient, len(data))
            for index, d in enumerate(data):
                nutr = {}
                nutr['model'] = 'calc.recommendednutrientlevelsdm'
                nutr['pk'] = pk
                pk += 1
                nutr['fields'] = {}
                nutr['fields']['pet_type'] = pet_type
                nutr['fields']['pet_stage'] = seq[index]
                nutr['fields']['amount'] = float(d)
                nutr['fields']['nutrient'] = nutrient
                result.append(nutr)

# pprint.pp(result)
with open('recommendednutrientlevels_data.json', 'w') as file:
    json.dump(result, file)
