from django.core.exceptions import ImproperlyConfigured
from django.forms.models import modelform_factory
from django.utils.translation import ugettext as _

from . import http, mixins
from .exceptions import HttpError, NotFound, FormValidationError
from .utils import serialize
from .views import Endpoint

__all__ = ['GenericEndpoint', 'CreateEndpoint', 'ListEndpoint',
    'DetailEndpoint', 'UpdateEndpoint', 'DeleteEndpoint', 'ListCreateEndpoint',
    'DetailUpdateEndpoint', 'DetailDeleteEndpoint', 'DetailUpdateDeleteEndpoint']


class GenericEndpoint(Endpoint):
    model = None
    fields = None

    lookup_field = 'pk'
    lookup_url_kwarg = None

    form_class = None
    queryset = None

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset._clone()

        if self.model is not None:
            return self.model._default_manager.all()

        msg = _('{0} must either define "model" or "queryset", or '
            'override "get_queryset()"')
        raise ImproperlyConfigured(msg.format(self.__class__.__name__))

    def get_object(self):
        queryset = self.get_queryset()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            lookup = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        except KeyError:
            msg = _('Lookup field "{0}" was not provided in view '
                'kwargs to "{1}"')
            raise ImproperlyConfigured(msg.format(lookup_url_kwarg,
                self.__class__.__name__))

        try:
            return queryset.get(**lookup)
        except self.model.DoesNotExist:
            raise NotFound(_('Resource not found'))

    def get_form_class(self):
        if self.form_class is not None:
            return self.form_class

        return modelform_factory(self.model, fields=self.fields or '__all__')

        msg = _('{0} must either define "form_class" or both "model" and '
            '"fields", or override "get_form_class()"')
        raise ImproperlyConfigured(msg.format(self.__class__.__name__))

    def get_form(self, data=None, files=None, **kwargs):
        FormClass = self.get_form_class()
        return FormClass(data=data, files=files, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return {'data': self.serialize(self.object)}

    def form_invalid(self, form):
        raise FormValidationError(form=form)

    def serialize(self, objs):
        return serialize(objs, fields=self.fields)


class CreateEndpoint(
    mixins.CreateModelMixin,
    GenericEndpoint
):
    pass


class ListEndpoint(
    mixins.ListModelMixin,
    GenericEndpoint
):
    pass


class DetailEndpoint(
    mixins.DetailModelMixin,
    GenericEndpoint
):
    pass


class UpdateEndpoint(
    mixins.UpdateModelMixin,
    GenericEndpoint
):
    pass


class DeleteEndpoint(
    mixins.DeleteModelMixin,
    GenericEndpoint
):
    pass


class ListCreateEndpoint(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericEndpoint
):
    pass


class DetailUpdateEndpoint(
    mixins.DetailModelMixin,
    mixins.UpdateModelMixin,
    GenericEndpoint
):
    pass


class DetailDeleteEndpoint(
    mixins.DetailModelMixin,
    mixins.DeleteModelMixin,
    GenericEndpoint
):
    pass


class DetailUpdateDeleteEndpoint(
    mixins.DetailModelMixin,
    mixins.UpdateModelMixin,
    mixins.DeleteModelMixin,
    GenericEndpoint
):
    pass
