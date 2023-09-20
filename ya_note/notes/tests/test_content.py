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

    def test_page_list(self):
        url = reverse('notes:list')
        user_note = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for client, result in user_note:
            with self.subTest(key=client, value=result):
                response = client.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, result)

    def test_authorized_client_has_form(self):
        adress = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for client, result in adress:
            with self.subTest(client):
                url = reverse(client, args=result)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
