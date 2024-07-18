import pytest
from django.urls import reverse
from food.models import Food, NutrientsQuantity
from http import HTTPStatus
from pytest_django.asserts import assertRedirects


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
def test_food_delete_and_edit(user, resp, name, food_id):
    """Авторизованный пользователь не может изменять не свои продукты."""
    url = reverse(name, args=food_id)
    response = user.get(url)
    assert response.status_code == resp


@pytest.mark.django_db
def test_auth_food_create(food_form_data, author_client):
    """Авторизованный пользователь может создать продукт. редирект на index."""
    url = reverse('food:food_create')
    response = author_client.post(url, data=food_form_data)
    assert Food.objects.exists() is True
    id = Food.objects.get().id
    expected_url = reverse('food:food_detail', args=(id,))
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_auth_food_create_same_name(food_form_data, auth_client, food):
    """Авториз пользователь не может создать продукт c cуществующим именем."""
    url = reverse('food:food_create')
    food_form_data['description'] = food.description
    response = auth_client.post(url, data=food_form_data)
    assert Food.objects.count() == 1
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_food_create_based_on(food_form_data, auth_client, food):
    """Авториз пользователь может создать продукт на основе существующего."""
    url = reverse('food:food_create')
    food_form_data['based_on'] = food.description
    auth_client.post(url, data=food_form_data)
    assert Food.objects.count() == 2
    instance = Food.objects.filter(
        description=food_form_data['description']).get()
    nutr_food = NutrientsQuantity.objects.filter(food=food)
    nutr_new_food = NutrientsQuantity.objects.filter(food=instance)
    assert len(nutr_new_food) == len(nutr_food)
    assert set(nutr_food) == set(nutr_food)


@pytest.mark.django_db
def test_food_search(auth_client, food, food_id):
    """Авторизованный пользователь может искать продукт."""
    url = reverse('food:food_search_by_name')
    form_data = {'food': food.description}
    print(form_data)
    response = auth_client.get(url, data=form_data)
    expected_url = reverse('food:food_detail', args=food_id)
    assertRedirects(response, expected_url)


# @pytest.mark.django_db
# def test_food_update(author_client, food, food_id, nutr_name, food_nutr):
#     """Автор продукта может изменять свой продукт
#     """
#     url = reverse('food:food_update',args=food_id)
#     print(url)
#     form_data = {'nutrient': [nutr_name.name]}

#     print(form_data)
#     response = author_client.post(url, data=form_data)
#    # print(response)
#     print(NutrientsQuantity.objects.count())
#     assert NutrientsQuantity.objects.count() == 2
