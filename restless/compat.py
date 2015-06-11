
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
