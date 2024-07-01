import datetime

def pet_stage_calculate(animal):

    birthday = animal.birthday
    weight = animal.weight
    pet_type = animal.type
    nursing = animal.nursing
    sterilized = animal.sterilized

    today = (datetime.datetime.now() - datetime.datetime(1970,1,1)).days
    birthday1 = (birthday - datetime.date(1970,1,1)).days
    age = round((today-birthday1)/30.5, 1)

    if pet_type == 'dog':
        if sterilized:
            
