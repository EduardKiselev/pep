import datetime
from calc.models import PetStage


def pet_stage_calculate(animal):
    birthday = animal.birthday
    weight = animal.weight
    pet_type = animal.type
    nursing = animal.nursing
    sterilized = animal.sterilized

    today = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).days
    birthday1 = (birthday - datetime.date(1970, 1, 1)).days
    age = round((today-birthday1)/30.5, 1)

    pet_stage = PetStage.objects.filter(
        sterilized=sterilized,
        nursing=nursing,
        age_finish__gt=age,
        age_start__lt=age,
        pet_type=pet_type)
    if len(pet_stage) == 1:
        return pet_stage[0], weight
    else:
        return None
