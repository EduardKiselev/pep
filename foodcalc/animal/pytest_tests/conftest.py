import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from animal.models import Animal, AnimalType
from django.shortcuts import get_object_or_404
import datetime

User = get_user_model()


@pytest.fixture
def auth_user(django_user_model):
    return django_user_model.objects.create(username='auth')


@pytest.fixture
def animal_owner_user(django_user_model):
    return django_user_model.objects.create(username='animal_owner')


@pytest.fixture
def owner_id(animal_owner_user):
    return (get_object_or_404(User, username=animal_owner_user).username,)


@pytest.fixture
def auth_client(auth_user):
    client = Client()
    client.force_login(auth_user)
    return client


@pytest.fixture
def not_auth_client():
    client = Client()
    return client


@pytest.fixture
def animal_owner_client(animal_owner_user):
    client = Client()
    client.force_login(animal_owner_user)
    return client


@pytest.fixture
def animal_type():
    animal_type = AnimalType.objects.create(
        title='Кошка',
        description='cat'
        )
    #  animal_type = get_object_or_404(AnimalType,title='Кошка')
    return animal_type


@pytest.fixture
def pet(animal_owner_user, animal_type):
    pet = Animal.objects.create(
        name='Мурка',
        owner=animal_owner_user,
        type=animal_type,
        nursing=0,
        sterilized=0,
        weight=5,
        birthday=datetime.date(2023, 1, 1),
    )
    return pet


@pytest.fixture
def pet_id(pet):
    return (pet.id,)


@pytest.fixture
def pet_form_data(animal_type):
    return {
        'name': 'Мурка2',
        'type': animal_type,
        'nursing': True,
        'sterilized': False,
        'weight': 5,
        'birthday': '01.01.2024',
    }
