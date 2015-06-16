from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .auth import SessionAuth, login_required
from .compat import get_user_model, json
from .exceptions import APIException, AuthenticationFailed, ParseError
from .http import Http200, Http500
from .models import serialize
from .settings import api_settings

__all__ = ['Endpoint']


class Endpoint(View):
    """
    Class-based Django view that should be extended to provide an API
    endpoint (resource). To provide GET, POST, PUT, HEAD or DELETE methods,
    implement the corresponding get(), post(), put(), head() or delete()
    method, respectively.

    If you also implement authenticate(request) method, it will be called
    before the main method to provide authentication, if needed. Auth mixins
    use this to provide authentication.

    The usual Django "request" object passed to methods is extended with a
    few more attributes:

      * request.content_type - the content type of the request
      * request.params - a dictionary with GET parameters
      * request.data - a dictionary with POST/PUT parameters, as parsed from
          either form submission or submitted application/json data payload
      * request.raw_data - string containing raw request body

    The view method should return either a HTTPResponse (for example, a
    redirect), or something else (usually a dictionary or a list). If something
    other than HTTPResponse is returned, it is first serialized into
    :py:class:`resticus.http.JSONResponse` with a status code 200 (OK),
    then returned.

    The authenticate method should return either a HttpResponse, which will
    shortcut the rest of the request handling (the view method will not be
    called), or None (the request will be processed normally).

    Both methods can raise a :py:class:`resticus.http.HttpError` exception
    instead of returning a HttpResponse, to shortcut the request handling and
    immediately return the error to the client.
    """

    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    login_required = api_settings.LOGIN_REQUIRED

    @staticmethod
    def parse_content_type(content_type):
        if ';' in content_type:
            ct, params = content_type.split(';', 1)
            try:
                params = dict(param.split('=') for param in params.split())
            except:
                params = {}
        else:
            ct = content_type
            params = {}
        return ct, params

    def parse_body(self, request):
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return

        ct, ct_params = self.parse_content_type(request.content_type)
        if ct == 'application/json':
            charset = ct_params.get('charset', 'utf-8')
            try:
                data = request.body.decode(charset)
                return json.loads(data)
            except Exception as err:
                raise ParseError(_('Malformed JSON payload: {0}').format(err))
        elif ((ct == 'application/x-www-form-urlencoded') or
                (ct.startswith('multipart/form-data'))):
            return dict((k, v) for (k, v) in request.POST.items())
        return request.body

    def authenticate(self, request):
        for auth in self.get_authenticators():
            user = auth.authenticate(request)
            if user is not None:
                return user
        return AnonymousUser()

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        return [auth() for auth in self.authentication_classes]

    def get_authenticate_header(self, request):
        """
        If a request is unauthenticated, determine the WWW-Authenticate
        header to use for 401 responses, if any.
        """
        authenticators = self.get_authenticators()
        if authenticators:
            return authenticators[0].authenticate_header(request)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        request.content_type = request.META.get('CONTENT_TYPE', 'text/plain')
        request.params = dict((k, v) for (k, v) in request.GET.items())
        request.data = None
        request.raw_data = request.body

        try:
            request.user = self.authenticate(request)
            request.data = self.parse_body(request)
            response = super(Endpoint, self).dispatch(request, *args, **kwargs)

        except AuthenticationFailed as err:
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)
            if auth_header:
                err.response['WWW-Authenticate'] = auth_header
            else:
                err.response.status_code = 403
            response = err.response

        except APIException as err:
            response = err.response

        except Exception as err:
            if settings.DEBUG:
                response = Http500(str(err))
            else:
                response = Http500(_('Internal server error.'))

        if not isinstance(response, HttpResponse):
            response = Http200(response)
        return response


class SessionAuthEndpoint(Endpoint):
    """
    Session-based authentication API endpoint. Provides a GET method for
    authenticating the user based on passed-in "username" and "password"
    request params. On successful authentication, the method returns
    authenticated user details.

    Uses :py:class:`UsernamePasswordAuthMixin` to actually implement the
    Authentication API endpoint.

    On success, the user will get a response with their serialized User
    object, containing id, username, first_name, last_name and email fields.
    """

    authentication_classes = (SessionAuth,)

    user_fields = ('id', 'username', 'first_name', 'last_name', 'email')

    @login_required
    def get(self, request):
        return Http200({
            'data': serialize(request.user, fields=self.user_fields)
        })

    def post(self, request):
        username_field = getattr(get_user_model(), 'USERNAME_FIELD', 'username')

        username = request.data.get(username_field)
        password = request.data.get('password')

        credentials = {
            username_field: username,
            'password': password
        }
        user = auth.authenticate(**credentials)

        if user is None:
            raise AuthenticationFailed(_('Invalid username/password.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        auth.login(request, user)
        return self.get(request)
