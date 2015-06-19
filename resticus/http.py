import sys
import traceback

from django import http
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _

from .compat import json

__all__ = ['JSONResponse', 'JSONErrorResponse', 'Http200', 'Http201',
    'Http400', 'Http403']

HTTP_HEADER_ENCODING = 'iso-8859-1'


class JSONResponse(http.HttpResponse):
    """An HTTP response class that consumes data to be serialized to JSON."""

    def __init__(self, data, encoder=DjangoJSONEncoder, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder)
        super(JSONResponse, self).__init__(content=data, **kwargs)


class JSONErrorResponse(JSONResponse, http.HttpResponseServerError):
    """A JSON response class for simple API errors."""

    def __init__(self, reason, **kwargs):
        data = {'errors': [{
            'detail': reason,
            'meta': {}
        }]}

        if settings.DEBUG:
            exc = sys.exc_info()
            if exc[0] is not None:
                data['errors'][0]['meta'].update(
                    traceback=''.join(traceback.format_exception(*exc))
                )
        super(JSONErrorResponse, self).__init__(data, **kwargs)


class Http200(JSONResponse):
    """HTTP 200 OK"""
    pass


class Http201(JSONResponse):
    """HTTP 201 CREATED"""
    status_code = 201


class Http400(JSONErrorResponse, http.HttpResponseBadRequest):
    """HTTP 400 Bad Request"""
    pass


class Http403(JSONErrorResponse, http.HttpResponseForbidden):
    """HTTP 403 Forbidden"""
    pass


class Http404(JSONErrorResponse, http.HttpResponseNotFound):
    """HTTP 404 Not Found"""
    pass


class Http405(JSONResponse, http.HttpResponseNotAllowed):
    """HTTP 405 Method Not Allowed"""

    def __init__(self, method, permitted_methods):
        data = {'errors': [{
            'detail': _('Method "{0}" not allowed').format(method),
        }]}
        super(Http405, self).__init__(data,
            permitted_methods=permitted_methods)


class Http409(JSONErrorResponse):
    """HTTP 409 Conflict"""
    status_code = 409


class Http500(JSONErrorResponse):
    """HTTP 500 Internal Server Error"""
    pass
