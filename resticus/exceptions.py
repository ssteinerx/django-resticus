from django.utils.translation import ugettext as _

from . import http


class APIException(Exception):
    """Exception that results in returning a JSONErrorResponse to the user."""

    response_class = http.JSONErrorResponse
    default_reason = None

    def __init__(self, reason=None, **additional_data):
        super(APIException, self).__init__()
        reason = reason or self.default_reason
        self.response = self.response_class(reason, **additional_data)


class HttpError(APIException):
    def __init__(self, code=None, reason=None, **additional_data):
        code = code or self.status_code
        reason = reason or _('Internal server error')
        super(HttpError, self).__init__(reason, **additional_data)
        self.response.status_code = code


class AuthenticationFailed(APIException):
    response_class = http.Http401
    default_reason = _('Incorrect authentication credentials.')


class NotAuthenticated(APIException):
    response_class = http.Http401
    default_reason = _('Authentication credentials were not provided.')


class NotFound(APIException):
    response_class = http.Http404


class Forbidden(APIException):
    response_class = http.Http403


class ParseError(APIException):
    response_class = http.Http400
    default_reason = _('Malformed request.')


class PermissionDenied(APIException):
    response_class = http.Http403
    default_reason = _('You do not have permission to perform this action.')


class ValidationError(APIException):
    response_class = http.Http400
    default_reason = _('Malformed request.')

    def __init__(self, form, **kwargs):
        # rapidjson doesn't properly serialize collection.User[List|Dict], which
        # is used for Django's Error[List|Dict], so we have to manually convert.
        kwargs.setdefault('details', {k: list(v) for k, v in form.errors.items()})
        super(ValidationError, self).__init__(self, **kwargs)
