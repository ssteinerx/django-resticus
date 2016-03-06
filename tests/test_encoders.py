import sys

import pytest
from django.test import TestCase

from resticus import encoders
from resticus.settings import api_settings

try:
    import rapidjson
    RAPIDJSON_INSTALLED = True
except ImportError:
    RAPIDJSON_INSTALLED = False


class JSONEncoderTests(TestCase):
    @pytest.mark.skipif(RAPIDJSON_INSTALLED, reason='not used if rapidjson is present')
    def test_using_json(self):
        assert api_settings.JSON_DECODER == encoders.JSONDecoder
        assert api_settings.JSON_ENCODER == encoders.JSONEncoder

    @pytest.mark.skipif(not RAPIDJSON_INSTALLED, reason='Requires rapidjson')
    def test_using_rapidjson(self):
        assert api_settings.JSON_DECODER == encoders.RapidJSONDecoder
        assert api_settings.JSON_ENCODER == encoders.RapidJSONEncoder
