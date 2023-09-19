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
        adress = reverse('notes:list')
        user_note = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for key, value in user_note:
            with self.subTest(key=key, value=value):
                response = key.get(adress)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, value)

    def test_authorized_client_has_form(self):
        adress = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for key, value in adress:
            with self.subTest(key):
                url = reverse(key, args=value)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
