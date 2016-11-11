import base64

from resticus import generics
from resticus.auth import login_required, BasicHttpAuth
from resticus.exceptions import HttpError
from resticus.http import Http201, Http403, Http404, Http400
from resticus.utils import serialize
from resticus.views import Endpoint

from .models import *
from .forms import *

__all__ =  [
            'AuthorList',
            'AuthorDetail',
            'BookDetail',
            'PublisherList',
            'PublisherDetail',
            'ReadOnlyPublisherList',
           ]

__all__ += [
            'BasicAuthEndpoint'
            'EchoView',
            'ErrorRaisingView',
            'FailsIntentionally',
            'WildcardHandler',
          ]


class AuthorList(generics.ListCreateEndpoint):
    model = Author
    form_class = AuthorForm


class AuthorDetail(generics.DetailUpdateDeleteEndpoint):
    model = Author
    form_class = AuthorForm
    lookup_url_kwarg = 'author_id'


class PublisherList(generics.ListCreateEndpoint):
    model = Publisher


class PublisherDetail(generics.DetailUpdateDeleteEndpoint):
    model = Publisher


class ReadOnlyPublisherList(generics.DetailEndpoint):
    model = Publisher


class BookDetail(generics.DetailEndpoint):
    model = Book
    lookup_field = 'isbn'


class FailsIntentionally(Endpoint):
    def get(self, request):
        raise Exception("I'm being a bad view")


class WildcardHandler(Endpoint):
    def dispatch(self, request, *args, **kwargs):
        return Http404('no such resource: %s %s' % (
            request.method, request.path))


class EchoView(Endpoint):
    def post(self, request):
        return {
            'headers': dict((k, str(v)) for k, v in request.META.items()),
            'raw_data': base64.b64encode(request.raw_data).decode('ascii')
        }

    def get(self, request):
        return self.post(request)

    def put(self, request):
        return self.post(request)


class ErrorRaisingView(Endpoint):
    def get(self, request):
        raise HttpError(400, 'raised error')


class BasicAuthEndpoint(Endpoint):
    authentication_classes = (BasicHttpAuth,)

    @login_required
    def get(self, request):
        return serialize(request.user)
