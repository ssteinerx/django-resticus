from . import http
from .utils import patch_form

__all__ = ['ListModelMixin', 'DetailModelMixin', 'CreateModelMixin',
    'UpdateModelMixin', 'DeleteModelMixin']


class ListModelMixin(object):
    def get(self, request, *args, **kwargs):
        filter = self.get_filter()
        return {'data': [self.serialize(obj) for obj in filter]}


class DetailModelMixin(object):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return {'data': self.serialize(self.object)}


class CreateModelMixin(object):
    def put(self, request, *args, **kwargs):
        form = self.get_form(
            data=request.data,
            files=request.FILES
        )
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    def form_valid(self, form):
        data = super(CreateModelMixin, self).form_valid(form)
        return http.Http201(data)


class UpdateModelMixin(object):
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(
            data=request.data,
            files=request.FILES,
            instance=self.object
        )
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class PatchModelMixin(object):
    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(
            data=request.data,
            files=request.FILES,
            instance=self.object
        )
        form = patch_form(form)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class DeleteModelMixin(object):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return http.Http204()
