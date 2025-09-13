from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions


class Lab2View(TemplateView):
    template_name = 'lab1/index.html'

    @handle_lab_exceptions
    def get(self, request):
        raise NotImplementedError

    @handle_lab_exceptions
    def post(self, request):
        raise NotImplementedError
