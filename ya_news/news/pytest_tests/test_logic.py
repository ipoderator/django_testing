from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    '''Проверка доступа к коментарияем не зарег. пользователя'''
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


def test_user_can_create_comment(
        author_client,
        form_data,
        news_id,
        news,
        author
):
    '''Проверка создания коментария зарег. пользователем'''
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news_id, bad_word):
    '''Проверка запрещенных слов'''
    url = reverse('news:detail', args=news_id)
    comments_count = Comment.objects.count()
    bad_words = {'text': f'Какой-то текст, {bad_word}, еще текст.'}
    response = author_client.post(url, data=bad_words)
    assert comments_count == 0
    assertFormError(response, form='form', field='text', errors=WARNING)


def test_author_can_edit_comment(
        author_client,
        form_data,
        news_id,
        comment
):
    '''Проверка редактирования комментария зарег. пользователем'''
    author_client.post(news_id, data=form_data)
    updated_comment = Comment.objects.get(id=comment.id)
    assert comment == updated_comment
    assert comment.text == form_data['text']
    assert comment.news == updated_comment.news
    assert comment.author == updated_comment.author


def test_author_can_delete_comment(
        author_client,
        comment_id,
        news_id,
):
    '''Проверка, что автор может удалить комментарий'''
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    news_detail_url = reverse('news:detail', args=news_id)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_reader_cant_edit_comment_of_another_user(
        reader_client,
        form_data,
        comment_id,
        comment
):
    '''Проверка доступа только к своим коментариям'''
    comment_text = comment.text
    url = reverse('news:edit', args=comment_id)
    response = reader_client.post(url, data=form_data)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    expected_count = 1
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == expected_count
    assert comment.text == comment_text


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        comment_id
):
    '''Проверка, что пользователи могут удалять только свои комментарии'''
    url = reverse('news:delete', args=comment_id)
    response = reader_client.post(url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    assert response.status_code == HTTPStatus.NOT_FOUND
