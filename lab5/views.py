from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions


class Lab5View(TemplateView):
    template_name = 'lab4/index.html'

    @handle_lab_exceptions
    def get(self, request):
        raise NotImplementedError
