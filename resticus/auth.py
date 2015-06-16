import base64

from django.conf import settings
from django.contrib import auth
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.translation import ugettext as _

from .compat import get_model, get_user_model, smart_text
from .exceptions import AuthenticationFailed
from .http import HTTP_HEADER_ENCODING, Http200, Http403
from .settings import api_settings


__all__ = ['SessionAuth', 'BasicHttpAuth', 'SessionAuthEndpoint',
    'login_required']


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    Hide some test client ickyness where the header can be unicode.
    """
    authorization = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(authorization, type('')):
        # Work around django test client oddness
        authorization = authorization.encode(HTTP_HEADER_ENCODING)
    return authorization


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class BaseAuth(object):
    def authenticate(self, request):
        pass

    def authenticate_header(self, request):
        pass


class SessionAuth(BaseAuth):
    def authenticate(self, request):
        user = getattr(request, 'user', None)

        if not user:
            return None

        if user.is_authenticated() and not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        self.enforce_csrf(request)
        return user

    def enforce_csrf(self, request):
        reason = CSRFCheck().process_view(request, None, (), {})
        if reason:
            raise HttpError(403, _('CSRF Failed: {0}').format(reason))


class BasicHttpAuth(BaseAuth):
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        authdata = get_authorization_header(request).split()

        if not authdata or authdata[0].lower() != b'basic':
            return

        if len(authdata) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(authdata) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise AuthenticationFailed(msg)

        try:
            auth_parts = base64.b64decode(authdata[1]).decode(HTTP_HEADER_ENCODING).partition(':')
        except Exception:
            msg = _('Invalid basic header. Credentials not correctly base64 encoded.')
            raise AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self.authenticate_credentials(request, userid, password)

    def authenticate_credentials(self, request, userid, password):
        username_field = getattr(get_user_model(), 'USERNAME_FIELD', 'username')
        credentials = {
            username_field: userid,
            'password': password
        }

        user = auth.authenticate(**credentials)

        if user is None:
            raise AuthenticationFailed(_('Invalid username/password.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return user

    def authenticate_header(self, request):
        return 'Basic realm="{0}"'.format(self.www_authenticate_realm)


class TokenAuth(BaseAuth):
    def authenticate(self, request):
        self.model = self.get_token_model()

        if self.model is None:
            msg = _('Token authentication is not enabled.')
            raise AuthenticationFailed(msg)

        authdata = get_authorization_header(request).split()

        if not authdata or authdata[0].lower() != b'token':
            return

        if len(authdata) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(authdata) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(request, authdata[1])

    @staticmethod
    def get_token_model():
        if api_settings.TOKEN_MODEL is None:
            return
        return get_model(api_settings.TOKEN_MODEL)

    def authenticate_credentials(self, request, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        user = token.get_user()

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return user

    def authenticate_header(self, request):
        return 'Token'


def login_required(fn):
    """
    Decorator for :py:class:`resticus.views.Endpoint` methods to require
    authenticated user. If the user isn't authenticated, HTTP 403 is
    returned immediately (HTTP 401 if Basic HTTP authentication is used).
    """
    def wrapper(self, request, *args, **kwargs):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated() or not user.is_active:
            msg = _('You must be logged in to access this endpoint.')
            raise AuthenticationFailed(msg)
        return fn(self, request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper
