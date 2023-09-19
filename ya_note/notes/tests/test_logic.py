from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestRoutes(TestCase):
    TITLE_TEXT = 'Новый заголовок'
    COMMENT_TEXT = 'Текст комментария'
    SLUG_TEXT = 'slug_text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.TITLE_TEXT,
            'text': cls.COMMENT_TEXT,
            'slug': cls.SLUG_TEXT,
        }
        cls.add_url = reverse('notes:add')
        cls.add_success = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, redirect_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)

    def test_user_can_create_note(self):
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.add_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        notes = Note.objects.get()
        self.assertEqual(notes.title, self.form_data['title'])
        self.assertEqual(notes.text, self.form_data['text'])
        self.assertEqual(notes.slug, self.form_data['slug'])
        self.assertEqual(notes.author, self.author)

    def test_unique_slug(self):
        self.author_client.post(self.add_url, data=self.form_data)
        response = self.author_client.post(self.add_url, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(response, form='form',
                             field='slug', errors=warning)

    def test_auto_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.add_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        slugify_slug = slugify(self.form_data['title'])
        note_slug = Note.objects.get(slug=slugify_slug)
        self.assertEqual(slugify_slug, note_slug.slug)


class TestCommentCreation(TestCase):
    TITLE_TEXT = 'Новый заголовок'
    COMMENT_TEXT = 'Текст комментария'
    SLUG_TEXT = 'slug_text'
    TITLE = 'Title'
    TEXT = 'TEXT'
    SLUG = 'SLug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.add_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.TITLE_TEXT,
            'text': cls.COMMENT_TEXT,
            'slug': cls.SLUG_TEXT,
        }

    def test_anonymous_user_cant_delete_note(self):
        response = self.reader_client.post(
            self.add_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_from_db = Note.objects.count()
        self.assertEqual(notes_from_db, 0)

    def test_author_can_edit_note(self):
        self.author_client.post(self.add_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE_TEXT)
        self.assertEqual(self.note.text, self.COMMENT_TEXT)
        self.assertEqual(self.note.slug, self.SLUG_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note_slug_db = Note.objects.get(slug=self.note.slug)
        self.assertEqual(self.note.text, note_slug_db.text)
        self.assertEqual(self.note.title, note_slug_db.title)
        self.assertEqual(self.note.slug, note_slug_db.slug)
