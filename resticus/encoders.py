from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise

from .compat import json


class JSONDecoder(json.JSONDecoder):
    pass


class JSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(JSONEncoder, self).default(obj)


class RapidJSONDecoder(object):
    def decode(self, data):
        import rapidjson
        return rapidjson.loads(data, use_decimal=True)


class RapidJSONEncoder(object):
    def encode(self, data):
        import rapidjson
        return rapidjson.dumps(data, use_decimal=True, datetime_mode=True)
