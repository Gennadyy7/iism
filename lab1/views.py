from django.shortcuts import render
from django.views.generic import TemplateView

from lab1.forms import Task1Form, Task2Form, Task3Form, Task4Form
from lab1.services.assignment_manager import AssignmentManager


class Lab1View(TemplateView):
    template_name = 'lab1/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task1_form'] = Task1Form()
        context['task2_form'] = Task2Form()
        context['task3_form'] = Task3Form()
        context['task4_form'] = Task4Form()
        return context

    def post(self, request):
        context = self.get_context_data()

        if 'task1' in request.POST:
            form = Task1Form(request.POST)
            if form.is_valid():
                p = form.cleaned_data['probability']
                manager = AssignmentManager()
                freq, theory = manager.run_task1(p)
                context['task1_result'] = {
                    'frequency': round(freq, 4),
                    'theory': round(theory, 4)
                }
            else:
                context['task1_form'] = form
                return render(request, self.template_name, context)

        return render(request, self.template_name, context)
