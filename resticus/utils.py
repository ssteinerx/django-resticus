import six

from django.db import models
from django.utils.encoding import force_text

__all__ = ['serialize', 'flatten']


def serialize_model(obj, fields=None, include=None, exclude=None,
        fixup=None):

    fieldmap = {}
    for f in obj._meta.concrete_model._meta.local_fields:
        fieldmap[f.name] = f.attname

    def getfield(f):
        return getattr(obj, fieldmap.get(f, f))

    if fields is None:
        fields = list(fieldmap.keys())
    else:
        fields = list(fields)

    if exclude is not None:
        fields = [f for f in fields if f not in exclude]

    if include is not None:
        for i in include:
            if isinstance(i, tuple) or (isinstance(i, six.string_types)):
                fields.append(i)

    data = {}
    for f in fields:
        if isinstance(f, six.string_types):
            data[f] = force_text(getfield(f), strings_only=True)
        elif isinstance(f, tuple):
            k, v = f
            if callable(v):
                data[k] = v(obj)
            elif isinstance(v, dict):
                data[k] = serialize(getattr(obj, k), **v)

    if fixup:
        data = fixup(obj, data)

    return data


def serialize(src, fields=None, related=None, include=None, exclude=None,
        fixup=None):
    """Serialize Model or a QuerySet instance to Python primitives.

    By default, all the model fields (and only the model fields) are
    serialized. If the field is a Python primitive, it is serialized as such,
    otherwise it is converted to string in utf-8 encoding.

    If `fields` is specified, it is a list of attribute descriptions to be
    serialized, replacing the default (all model fields). If `include` is
    specified, it is a list of attribute descriptions to add to the default
    list. If `exclude` is specified, it is a list of attribute descriptions
    to remove from the default list.

    Each attribute description can be either:

      * a string - includes a correspondingly named attribute of the object
        being serialized (eg. `name`, or `created_at`); this can be a
        model field, a property, class variable or anything else that's
        an attribute on the instance

      * a tuple, where the first element is a string key and the second
        is a function taking one argument - function will be run with the
        object being serialized as the argument, and the function result will
        be included in the result, with the key being the first tuple element

      * a tuple, where the first element is a related model attribute name
        and the second is a dictionary - related model instance(s) will
        be serialized recursively and added as sub-object(s) to the object
        being serialized; the dictionary may specify `fields`, `include`,
        `exclude` and `fixup` options for the related models following the
        same semantics as for the object being serialized.

    The `fixup` argument, if defined, is a function taking two arguments, the
    object being serialized, and the serialization result dict, and returning
    the modified serialization result. It's useful in cases where it's
    neccessary to modify the result of the automatic serialization, but its
    use is discouraged if the same result can be obtained through the
    attribute descriptions.

    The `related` argument (a different way of specifying related
    objects to be serialized) is deprecated and included only for backwards
    compatibility.

    Example::

        serialize(obj, fields=[
            'name',   # obj.name
            'dob',    # obj.dob
            ('age', lambda obj: date.today() - obj.dob),
            ('jobs', dict(   # for job in obj.jobs.all()
                fields=[
                    'title',  # job.title
                    'from',   # job.from
                    'to',     # job.to,
                    ('duration', lambda job: job.to - job.from),
                ]
            ))
        ])

    Returns: a dict (if a single model instance was serialized) or a list
    od dicts (if a QuerySet was serialized) with the serialized data. The
    data returned is suitable for JSON serialization using Django's JSON
    serializator.
    """

    def subs(subsrc):
        return serialize(subsrc, fields=fields, include=include,
            exclude=exclude, fixup=fixup)

    if isinstance(src, models.Manager):
        return [subs(i) for i in src.all()]

    elif (isinstance(src, list) or
            isinstance(src, models.query.QuerySet) or
            isinstance(src, set)):
        return [subs(i) for i in src]

    elif isinstance(src, dict):
        return dict((k, subs(v)) for k, v in src.items())

    elif isinstance(src, models.Model):
        return serialize_model(src, fields=fields, include=include,
            exclude=exclude, fixup=fixup)

    else:
        return src


def flatten(attname):
    """Fixup helper for serialize.

    Given an attribute name, returns a fixup function suitable for serialize()
    that will pull all items from the sub-dict and into the main dict. If
    any of the keys from the sub-dict already exist in the main dict, they'll
    be overwritten.
    """

    def fixup(obj, data):
        for k, v in data[attname].items():
            data[k] = v
        del data[attname]
        return data
    return fixup


def patch_form(form):
    if form.is_bound:
        for field in list(form.fields.keys()):
            if field not in form.data:
                form.fields.pop(field)
    return form
