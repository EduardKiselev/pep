import pytest
from django.test.client import Client
from food.models import Food, NutrientsName, NutrientsQuantity


@pytest.fixture
def food_author_user(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def author_client(food_author_user):
    client = Client()
    client.force_login(food_author_user)
    return client


@pytest.fixture
def auth_user(django_user_model):
    return django_user_model.objects.create(username='user')


@pytest.fixture
def auth_client(auth_user):
    client = Client()
    client.force_login(auth_user)
    return client


@pytest.fixture
def nutr_name():
    nutr_name = NutrientsName.objects.create(
        name='Efir',
        unit_name='g',
    )
    return nutr_name


@pytest.fixture
def food(food_author_user):
    food = Food.objects.create(
        description='BestFood',
        ndbNumber=1,
        fdcId=1,
        author=food_author_user,
    )
    return food


@pytest.fixture
def food_id(food):
    return (food.id,)


@pytest.fixture
def food_nutr(food, nutr_name):

    nutr_q = NutrientsQuantity.objects.create(
        food=food,
        nutrient=nutr_name,
        amount=1.0,
    )
    return nutr_q


@pytest.fixture
def food_form_data():
    return {
        'description': 'NewFood',
    }
