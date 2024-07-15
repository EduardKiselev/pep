import pytest
from django.urls import reverse
from food.models import Food
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from animal.pytest_tests.conftest import auth_client,auth_user


@pytest.mark.parametrize(
    'user, resp',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('auth_client'), HTTPStatus.FORBIDDEN),
    )
)
@pytest.mark.parametrize(
    'name', ('food:food_update', 'food:food_delete',)
)
def test_animal_delete_and_edit(user, resp, name, food_id):
    """Авторизованный пользователь не может редактировать и удалять
    не свои посты. Автору доступны страницы редактирования
    """
    url = reverse(name, args=food_id)
    response = user.get(url)
    assert response.status_code == resp


@pytest.mark.django_db
def test_auth_food_create(food_form_data, author_client):
    """Авторизованный пользователь может создать продукт,
    редирект на страницу продукта
    """
    url = reverse('food:food_create')
    response = author_client.post(url, data=food_form_data)
    assert Food.objects.exists() == True
    id = Food.objects.get().id
    expected_url = reverse('food:food_detail', args=(id,))
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_auth_food_create(food_form_data, auth_client, food):
    """Авторизованный пользователь не может создать продукт,
    с существующим именем
    """

    url = reverse('food:food_create')
    food_form_data['description'] = food.description
    print(food.description)
    response = auth_client.post(url, data=food_form_data)
    assert Food.objects.count() == 1
    assert response.status_code == HTTPStatus.FORBIDDEN
