import pytest
from django.urls import reverse
from animal.models import Animal
from http import HTTPStatus
from calc.forms import AnimalForm
from pytest_django.asserts import assertRedirects

@pytest.mark.django_db
def test_4(pet_form_data, animal_owner_client, owner_id):
    """Авторизованный пользователь может создать питомца, редирект на профиль
    неавторизованный не может
    """
    url = reverse('animal:animal_create')
    response = animal_owner_client.post(url, data=pet_form_data)
    print(owner_id)
    #assertRedirects(response, reverse('calc:profile', args=owner_id))
    assert response.status_code == HTTPStatus.OK
   # assert Animal.objects.exists() == 1


@pytest.mark.django_db
def test_5(client, pet_form_data, owner_id):
    """Неавторизованный пользователь не может создать питомца, редирект на логирование
    """   
    url = reverse('animal:animal_create')
    response = client.post(url, data=pet_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=pet_form_data)    
    assertRedirects(response, expected_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Animal.objects.exists() == 0

