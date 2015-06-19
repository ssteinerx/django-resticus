from . import http

__all__ = ['ListModelMixin', 'DetailModelMixin', 'CreateModelMixin',
    'UpdateModelMixin', 'DeleteModelMixin']


class ListModelMixin(object):
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return {'data': self.serialize(queryset)}


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

    # TODO: patch


class DeleteModelMixin(object):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return http.Http204()
