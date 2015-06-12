import os
import sys
from django.conf import settings

sys.path.append(os.path.dirname(__file__))


def pytest_configure():
    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
