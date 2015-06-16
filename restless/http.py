import sys
import traceback

from django import http
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from .compat import json

__all__ = ['JSONResponse', 'JSONErrorResponse', 'Http200', 'Http201',
    'Http400', 'Http403']

HTTP_HEADER_ENCODING = 'iso-8859-1'


class JSONResponse(http.HttpResponse):
    """HTTP response with JSON body ("application/json" content type)"""

    def __init__(self, data, **kwargs):
        """
        Create a new JSONResponse with the provided data (will be serialized
        to JSON using django.core.serializers.json.DjangoJSONEncoder).
        """

        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(json.dumps(data,
            cls=DjangoJSONEncoder), **kwargs)


class JSONErrorResponse(JSONResponse):
    """HTTP Error response with JSON body ("application/json" content type)"""

    status_code = 500

    def __init__(self, reason, **kwargs):
        """
        Create a new JSONErrorResponse with the provided error reason (string)
        and the optional additional data (will be added to the resulting
        JSON object).
        """
        data = {'errors': [{'detail': reason}]}
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
    """HTTP 201 CREATED"""
    status_code = 201


class Http400(JSONErrorResponse, http.HttpResponseBadRequest):
    """HTTP 400 Bad Request"""
    pass


class Http403(JSONErrorResponse, http.HttpResponseForbidden):
    """HTTP 403 Forbidden"""
    pass


class Http404(JSONErrorResponse):
    """HTTP 404 Not Found"""
    status_code = 404


class Http409(JSONErrorResponse):
    """HTTP 409 Conflict"""
    status_code = 409


class Http500(JSONErrorResponse):
    """HTTP 500 Internal Server Error"""
    status_code = 500
