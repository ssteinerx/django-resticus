from django.utils.translation import ugettext as _

from .exceptions import ParseError
from .settings import api_settings


def parse_content_type(content_type):
    if ';' in content_type:
        content_type, params = content_type.split(';', 1)
        try:
            params = dict(param.split('=') for param in params.split())
        except Exception:
            params = {}
    else:
        params = {}
    return content_type, params


def parse_json(request, **extra):
    charset = extra.get('charset', 'utf-8')
    try:
        data = request.body.decode(charset)
        return api_settings.JSON_DECODER().decode(data)
    except Exception:
        raise ParseError()


def parse_post(request, **extra):
    return dict(request.POST.items())


def parse_plain_text(request, **extra):
    return request.body
