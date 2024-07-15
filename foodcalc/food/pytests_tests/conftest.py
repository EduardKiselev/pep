import pytest
from animal.pytest_tests.conftest import auth_client,
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
def food_nutr(food, nutr_name):
    
    nutr_q = NutrientsQuantity.objects.create(
        food=food,
        nutrient=nutr_name
        amount=1.0
    )
    return nutr_q

@pytest.fixture
def food_form_data(food_author_user):
    return {
        'description': 'NewFood',
        'ndbNumber': 2,
        'fdcId': 2,
        'author': food_author_user,
    }