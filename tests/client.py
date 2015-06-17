from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client, MULTIPART_CONTENT
from django.test.utils import override_settings
from resticus.compat import json


def debug(fn):
    return override_settings(DEBUG=True)(fn)


class TestClient(Client):
    @staticmethod
    def process(response):
        try:
            response.json = json.loads(response.content.decode('utf-8'))
        except Exception:
            response.json = None
        return response

    def get(self, url_name, data={}, follow=False, extra={}, *args, **kwargs):
        return self.process(
            super(TestClient, self).get(
                reverse(url_name, args=args, kwargs=kwargs),
                data=data,
                follow=follow,
                **extra))

    def post(self, url_name, data={}, content_type=MULTIPART_CONTENT,
            follow=False, extra={}, *args, **kwargs):
        return self.process(
            super(TestClient, self).post(
                reverse(url_name, args=args, kwargs=kwargs),
                content_type=content_type,
                data=data,
                follow=follow,
                **extra))

    def put(self, url_name, data={}, content_type=MULTIPART_CONTENT,
            follow=False, *args, **kwargs):
        return self.process(
            super(TestClient, self).put(
                reverse(url_name, args=args, kwargs=kwargs),
                content_type=content_type, data=data, follow=follow))

    def delete(self, url_name, data={}, content_type=MULTIPART_CONTENT,
            follow=False, *args, **kwargs):
        return self.process(
            super(TestClient, self).delete(
                reverse(url_name, args=args, kwargs=kwargs),
                content_type=content_type, data=data, follow=follow))
