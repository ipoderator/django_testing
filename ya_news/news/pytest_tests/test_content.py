import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_page(client):
    '''Проверка вывода кол-во новостей на странице'''
    url = reverse('news:home')
    response = client.get(url)
    news_count = len(response.context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news(client):
    '''Проверка сортировки новостей'''
    url = reverse('news:home')
    response = client.get(url)
    news_date = [news.date for news in response.context['object_list']]
    ordered_dates = sorted(news_date, reverse=True)
    assert news_date == ordered_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('comment_list')
def test_comments(client, news_id):
    '''Проверка сортировки комментариев по времени'''
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'key, value',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_form_show_correct_user(key, value, news_id):
    '''Проверка формы для отправки комментариев'''
    url = reverse('news:detail', args=news_id)
    response = key.get(url)
    assert ('form' in response.context) == value
