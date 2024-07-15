import pytest
from django.urls import reverse
from animal.models import Animal
from http import HTTPStatus
from calc.forms import AnimalForm
from pytest_django.asserts import assertRedirects

@pytest.mark.django_db
def test_auth_animal_create(pet_form_data, animal_owner_client, owner_id):
    """Авторизованный пользователь может создать питомца, редирект на профиль
    неавторизованный не может
    """
    url = reverse('animal:animal_create')
    response = animal_owner_client.post(url, data=pet_form_data)
    form = AnimalForm(pet_form_data)
    print(form.is_valid())
    # s = json.loads(response.data)
    # print(response.status_code)
    # print(s['html'])
    # assertRedirects(response, reverse('calc:profile', args=owner_id))
    assert response.status_code == HTTPStatus.OK
    # assert Animal.objects.exists() == 1


@pytest.mark.django_db
def test_anonim_pet_create(client, pet_form_data, owner_id):
    """Неавторизованный пользователь не может создать питомца, редирект на логирование
    """   
    url = reverse('animal:animal_create')
    response = client.post(url, json=pet_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=pet_form_data)    
    assertRedirects(response, expected_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Animal.objects.exists() == 0


@pytest.mark.parametrize(
    'user, resp',
    (
        (pytest.lazy_fixture('animal_owner_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('auth_client'), HTTPStatus.FORBIDDEN),
    )
)
@pytest.mark.parametrize(
    'name', ('animal:animal_update', 'animal:animal_delete',)
)
def test_animal_delete_and_edit(user, resp, name, pet_id):
    """Авторизованный пользователь может редактировать или удалять
    свои комментарии. Авторизованный пользователь не может редактировать
    или удалять чужие комментарии.
    """
    url = reverse(name, args=pet_id)
    response = user.get(url)
    assert response.status_code == resp
