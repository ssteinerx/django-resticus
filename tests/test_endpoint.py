import base64
from django.test import TestCase
from restless.compat import json
from .client import TestClient
from .testapp.models import Publisher, Author, Book

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class TestEndpoint(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.author = Author.objects.create(name='User Foo')

    def test_author_list(self):
        """Exercise a simple GET request"""

        r = self.client.get('author_list')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json), 1)
        self.assertEqual(r.json[0]['id'], self.author.id)

    def test_author_details(self):
        """Exercise passing parameters to GET request"""

        r = self.client.get('author_detail', author_id=self.author.id)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['id'], self.author.id)
        self.assertEqual(r.json['name'], 'User Foo')

    def test_author_details_not_found(self):
        """Exercise returning arbitrary HTTP status codes from view"""

        r = self.client.get('author_detail', author_id=self.author.id + 9999)
        self.assertEqual(r.status_code, 404)

    def test_author_details_invalid_method(self):
        """Exercise 405 if POST request doesn't pass form validation"""
        r = self.client.post('author_detail', author_id=self.author.id)
        self.assertEqual(r.status_code, 405)

    def test_create_author_form_encoded(self):
        """Exercise application/x-www-form-urlencoded POST"""

        r = self.client.post('author_list', data=urlencode({
            'name': 'New User',
        }), content_type='application/x-www-form-urlencoded')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json['name'], 'New User')
        self.assertEqual(r.json['name'],
            Author.objects.get(id=r.json['id']).name)

    def test_create_author_multipart(self):
        """Exercise multipart/form-data POST"""

        r = self.client.post('author_list', data={
            'name': 'New User',
        })  # multipart/form-data is default in test client
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json['name'], 'New User')
        self.assertEqual(r.json['name'],
            Author.objects.get(id=r.json['id']).name)

    def test_create_author_json(self):
        """Exercise application/json POST"""

        r = self.client.post('author_list', data=json.dumps({
            'name': 'New User',
        }), content_type='application/json; charset=utf-8')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json['name'], 'New User')
        self.assertEqual(r.json['name'],
            Author.objects.get(id=r.json['id']).name)

    def test_invalid_json_payload(self):
        """Exercise invalid JSON handling"""

        r = self.client.post('author_list', data='xyz',
            content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_delete_author(self):
        """Exercise DELETE request"""

        r = self.client.delete('author_detail', author_id=self.author.id)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Author.objects.count(), 0)

    def test_change_author(self):
        """Exercise PUT request"""

        r = self.client.put('author_detail', data=json.dumps({
            'name': 'User Bar'
        }), author_id=self.author.id, content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['name'], 'User Bar')
        self.assertEqual(r.json['name'],
            Author.objects.get(id=r.json['id']).name)

    def test_view_failure(self):
        """Exercise exception handling"""

        with self.settings(DEBUG=True):
            r = self.client.get('fail_view')

        self.assertEqual(r.status_code, 500)
        self.assertEqual(r.json['errors'][0]['detail'], "I'm being a bad view")
        self.assertTrue('traceback' in r.json)

    def test_raw_request_body(self):
        raw = b'\x01\x02\x03'
        r = self.client.post('echo_view', data=raw,
            content_type='text/plain')

        self.assertEqual(base64.b64decode(r.json['raw_data'].encode('ascii')),
            raw)

    def test_get_payload_is_ignored(self):
        """Test that body of the GET request is always ignored."""
        r = self.client.get('echo_view', extra={
            'CONTENT_TYPE': 'application/json'})
        # If the GET request body is not ignored, it (empty string) will be an
        # invalid JSON and will return 400 instead of 200.
        self.assertEqual(r.status_code, 200)

    def test_raising_http_error_returns_it(self):
        r = self.client.get('error_raising_view')
        self.assertEqual(r.status_code, 400)
