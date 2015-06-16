from django.conf import settings

try:
    import importlib
except ImportError:
    from django.utils import importlib


try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text


try:
    # json module from python > 2.6
    import json
except ImportError:
    # use packaged django version of simplejson
    from django.utils import simplejson as json


# Support custom user models in Django 1.5+
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
