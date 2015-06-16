import base64
from django.test import TestCase
from restless.compat import json
from .client import TestClient
from .testapp.models import Publisher, Author, Book


class TestAuth(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(username='foo', password='bar')

