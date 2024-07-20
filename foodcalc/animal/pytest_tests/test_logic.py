import pytest
from django.urls import reverse
from animal.models import Animal
from http import HTTPStatus
from calc.forms import AnimalForm
from pytest_django.asserts import assertRedirects
from django.test import RequestFactory

factory = RequestFactory()


@pytest.mark.django_db
def test_auth_animal_create(pet_form_data, auth_client):
    """Авторизованный пользователь может создать питомца."""
    url = reverse('animal:animal_create')
    response = auth_client.post(url, data=pet_form_data)
    assert Animal.objects.exists() == 1
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonim_pet_create(client, pet_form_data):
    """Клиент не может создать питомца. Редирект на логирование."""
    url = reverse('animal:animal_create')
    response = client.post(url, data=pet_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=pet_form_data)
    assertRedirects(response, expected_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Animal.objects.exists() == 0


def test_animal_delete_owner(animal_owner_client, animal_owner_user, pet_id):
    """Авторизованный пользователь может удалять своих питомцев."""
    url = reverse('animal:animal_delete', args=pet_id)
    response = animal_owner_client.post(url)
    assertRedirects(response, reverse('calc:profile',
                                      args=(animal_owner_user,)))
    assert response.status_code == HTTPStatus.FOUND
    assert Animal.objects.exists() is False


def test_animal_delete_user(auth_client, pet_id):
    """Авториз пользователь не может удалять не своих питомцев."""
    url = reverse('animal:animal_delete', args=pet_id)
    response = auth_client.post(url)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Animal.objects.exists() is True


@pytest.mark.django_db
def test_animal_create_sterilized_nursing(pet_form_data,
                                          auth_client, auth_user):
    """Нельзя создать питомца sterilized and nursing."""
    url = reverse('animal:animal_create')
    pet_form_data['sterilized'] = 1
    pet_form_data['nursing'] = 1
    request = RequestFactory().post(url)
    request.user = auth_user
    kwargs = {}
    kwargs['initial'] = {'request': request}
    form = AnimalForm(pet_form_data, **kwargs)
    assert form.is_valid() is False
    assert 'sterilized' in form.errors.keys()
    auth_client.post(url, data=pet_form_data)
    assert Animal.objects.exists() is False


@pytest.mark.django_db
def test_animal_create_same_name(pet, pet_form_data, animal_owner_client,
                                 animal_owner_user):
    """Авториз пользователь не может создать питомца с одинаковым именем."""
    url = reverse('animal:animal_create')
    pet_form_data['name'] = pet.name
    request = RequestFactory().post(url)
    request.user = animal_owner_user
    kwargs = {}
    kwargs['initial'] = {'request': request}
    form = AnimalForm(pet_form_data, **kwargs)
    assert form.is_valid() is False
    animal_owner_client.post(url, data=pet_form_data)
    assert Animal.objects.count() == 1
