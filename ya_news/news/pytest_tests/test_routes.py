from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_id'))
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    '''Проверка доступа для не авторезированного пользователя'''
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('comment_id')),
     ('news:delete', pytest.lazy_fixture('comment_id')),),
)
def test_availability_for_comment_edit_and_delete(
    author_client,
    name,
    args
):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, name, comment_id):
    '''Перенаправление для незарегистрированного пользователя'''
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
