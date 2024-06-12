import json

with open('input.json') as input, open('nutrients_data.txt','w') as output:
    data = json.load(input)
    for key in data:
        print(key+' = '+'models.IntegerField(blank=True)',file=output)


