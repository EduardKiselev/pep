from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name', ('food:food_create',
             'food:func',
             'food:food_search_by_name')
)
def test_login_redirect(
        name,
        client
):

    """При попытке перейти на страницу создания и поиска еды,
    анонимный пользователь перейдет на страницу логина. 
    """
    url = reverse(name)
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name', ('food:food_create',
             'food:func',
             'food:food_search_by_name')
)
def test_food_pages_for_auth_user(
        name,
        author_client
):
    """Залогиненному пользователю доступны страницы"""
    url = reverse(name)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'name', ('food:food_update',
             'food:food_delete'
             )
)
def test_update_delete_for_anonimus_user(
        name,
        client,
        food_id
):
    """Неавторизованный при попытке удалить или редактировать
    попадает на страницу логирования."""
    url = reverse(name, args=food_id)
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'user,resp',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
    )
)
def test_food_detail(
        user,
        resp,
        food_id,
        client
):
    """При попытке перейти на страницу продукта,
    анонимный пользователь перейдет на страницу логина.
    авторизованный просмотрит страницу
    """
    url = reverse('food:food_detail', args=food_id)
    response = user.get(url)
    if user == client:
        assert response.status_code == resp
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_url)
    else:
        assert response.status_code == resp
