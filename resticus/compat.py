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
    # Optional support for rapidjson
    import rapidjson as json
except ImportError:
    # json module from python > 2.6
    import json


# Support custom user models in Django 1.5+
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def get_model(model_lookup):
    app_label, model_name = model_lookup.split('.')
    try:
        from django.apps import apps
        return apps.get_model(app_label, model_name)
    except ImportError:
        from django.db import models
        return models.get_model(app_label, model_name)
