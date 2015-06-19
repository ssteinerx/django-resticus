from django.utils.translation import ugettext as _

from . import http


class APIException(Exception):
    """Exception that results in returning a JSONErrorResponse to the user."""

    response_class = http.JSONErrorResponse

    def __init__(self, reason, **additional_data):
        super(APIException, self).__init__(reason)
        self.response = self.response_class(reason, **additional_data)


class HttpError(APIException):
    def __init__(self, code=None, reason=None, **additional_data):
        code = code or self.status_code
        reason = reason or _('Internal server error')
        super(HttpError, self).__init__(reason, **additional_data)
        self.response.status_code = code


class AuthenticationFailed(APIException):
    response_class = http.Http401


class NotFound(APIException):
    response_class = http.Http404


class Forbidden(APIException):
    response_class = http.Http403


class ParseError(APIException):
    response_class = http.Http400


class FormValidationError(APIException):
    response_class = http.Http400

    def __init__(self, form, **kwargs):
        kwargs.setdefault('details', form.errors)
        msg = _('Invalid data')
        super(ValidationError, self).__init__(self, msg, **kwargs)
