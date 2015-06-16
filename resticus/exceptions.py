from .http import JSONErrorResponse
from django.utils.translation import ugettext as _


class APIException(Exception):
    """Exception that results in returning a JSONErrorResponse to the user."""

    status_code = 500

    def __init__(self, reason, **additional_data):
        super(APIException, self).__init__(reason)
        additional_data.setdefault('status', self.status_code)
        self.response = JSONErrorResponse(reason, **additional_data)


class HttpError(APIException):
    def __init__(self, code=None, reason=None, **additional_data):
        code = code or self.status_code
        reason = reason or _('Internal server error')
        super(HttpError, self).__init__(reason, **additional_data)
        self.response.status_code = code


class AuthenticationFailed(APIException):
    status_code = 401


class NotFound(APIException):
    status_code = 404


class ParseError(APIException):
    status_code = 400
