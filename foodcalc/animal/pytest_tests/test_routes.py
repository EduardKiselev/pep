import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('animal:animal_create',
             'animal:animal_update',
             'animal:animal_delete'),
)
def test_login_redirect(
        name,
        pet_id,
        client
):

    """При попытке перейти на страницу редактирования или удаления питомца
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    if name != 'animal:animal_create':
        url = reverse(name, args=pet_id)
    else:
        url = reverse(name)
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
