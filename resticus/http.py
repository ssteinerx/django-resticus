import sys
import traceback

from django import http
from django.conf import settings
from django.utils.translation import ugettext as _

from .settings import api_settings

__all__ = ['JSONResponse', 'JSONErrorResponse', 'Http200', 'Http201',
    'Http204', 'Http400', 'Http401', 'Http403', 'Http404', 'Http405',
    'Http409', 'Http500']

HTTP_HEADER_ENCODING = 'iso-8859-1'


class JSONResponse(http.StreamingHttpResponse):
    """An HTTP response class that consumes data to be serialized to JSON."""

    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        data = api_settings.JSON_ENCODER().iterencode(data)
        super(JSONResponse, self).__init__(streaming_content=data, **kwargs)


class JSONErrorResponse(JSONResponse):
    """A JSON response class for simple API errors."""

    default_reason = None
    status_code = 500

    def __init__(self, reason=None, **kwargs):
        data = {'errors': [{'detail': reason or self.default_reason}]}

        if settings.DEBUG:
            exc = sys.exc_info()
            if exc[0] is not None:
                data['errors'][0]['meta'] = {
                    'traceback': ''.join(traceback.format_exception(*exc))
                }
        super(JSONErrorResponse, self).__init__(data, **kwargs)


class Http200(JSONResponse):
    """HTTP 200 OK"""
    pass


class Http201(JSONResponse):
    """HTTP 201 Created"""
    status_code = 201


class Http204(http.HttpResponse):
    """HTTP 204 No Content"""
    status_code = 204


class Http400(JSONErrorResponse):
    """HTTP 400 Bad Request"""
    status_code = 400

    def __init__(self, reason, details=None, **kwargs):
        data = {'errors': [{'detail': reason}]}
        if details is not None:
            data['errors'][0]['meta'] = {'details': details}
        super(Http400, self).__init__(data, **kwargs)


class Http401(JSONErrorResponse):
    """HTTP 401 Unauthorized"""
    status_code = 401


class Http403(JSONErrorResponse):
    """HTTP 403 Forbidden"""
    status_code = 403


class Http404(JSONErrorResponse):
    """HTTP 404 Not Found"""
    status_code = 404


class Http405(JSONResponse):
    """HTTP 405 Method Not Allowed"""
    status_code = 405

    def __init__(self, method, permitted_methods, *args, **kwargs):
        data = {'errors': [{
            'detail': _('Method "{0}" not allowed').format(method),
        }]}
        super(Http405, self).__init__(data=data, *args, **kwargs)
        self['Allow'] = ', '.join(permitted_methods)


class Http409(JSONErrorResponse):
    """HTTP 409 Conflict"""
    status_code = 409


class Http500(JSONErrorResponse):
    """HTTP 500 Internal Server Error"""
    pass
