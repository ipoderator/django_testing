from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='note-slug',
        )

    def test_pages_availability(self):
        '''Какие страницы доступны всем пользователям'''
        adress = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for adress_url in adress:
            with self.subTest(adress_url):
                url = reverse(adress_url)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        '''Какие страницы доступны авторизированным пользователям'''
        adress = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for adress_url in adress:
            with self.subTest(adress_url):
                url = reverse(adress_url)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        user_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        adress = (
            'notes:edit',
            'notes:delete',
            'notes:detail',
        )
        for user, status in user_statuses:
            for adress_url in adress:
                with self.subTest(user=user, adress_url=adress_url):
                    url = reverse(adress_url, args=(self.note.slug, ))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        adress = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for key, value in adress:
            with self.subTest(key=key):
                url = reverse(key, args=value)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
