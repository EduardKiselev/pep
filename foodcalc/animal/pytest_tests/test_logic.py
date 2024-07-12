import pytest
from django.urls import reverse
from animal.models import Animal
#from pytest_lazyfixture import lazy_fixture
from http import HTTPStatus

@pytest.mark.django_db
@pytest.mark.parametrize('user, http_resp, animal_exist',
    (
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND, True),
        (pytest.lazy_fixture('animal_owner_client'), HTTPStatus.OK, True),
    )
)
def test_4(user, animal_exist, http_resp, pet_form_data):
    """Авторизованный пользователь может создать питомца,
    неавторизованный не может
    """
    url = reverse('animal:animal_create')
    form_data = pet_form_data
    response = user.post(url, data=form_data)
    print(response)
    assert response.status_code == http_resp
   # assert Animal.objects.exists() == animal_exist
