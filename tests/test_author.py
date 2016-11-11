# -*- coding: utf-8 -*-
from django.test import TestCase
from resticus.compat import json
from django.contrib.auth import get_user_model

from testapp.models import Author


class AuthorFormTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user('zoidberg')
        self.entry = Author.objects.create(name="Joe T. Schmoe")

    def test_change_create_author_author_list_json(self):
        self.client.post(
            'author_list',
            data=json.dumps({"name": "Not Joe T. Schmoe", "comment": "Some other Schmoe"}),
            content_type='application/json; charset=utf-8'
        )