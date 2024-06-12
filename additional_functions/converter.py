import json

with open('nutrients_data.txt','w') as output:
    # data = json.load(input)
    # for i in range(250):
    #     print(key+' = '+'models.IntegerField(blank=True)',file=output)
    for i in range(1, 250):
        print('n'+str(i)+' = '+'models.IntegerField(blank=True, null=True)',file=output)
