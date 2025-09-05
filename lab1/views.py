from django.shortcuts import render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab1.forms import Task1Form, Task2Form, Task3Form, Task4Form
from lab1.services.task_view_processor import TaskViewProcessor


class Lab1View(TemplateView):
    template_name = 'lab1/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task1_form'] = Task1Form()
        context['task2_form'] = Task2Form()
        context['task3_form'] = Task3Form()
        context['task4_form'] = Task4Form()
        return context

    @handle_lab_exceptions
    def post(self, request):
        context = self.get_context_data()

        if 'task1' in request.POST:
            form = Task1Form(request.POST)
            if form.is_valid():
                p = form.cleaned_data['probability']
                context['task1_result'] = TaskViewProcessor.process_task1(p)
            else:
                context['task1_form'] = form
                return render(request, self.template_name, context)

        elif 'task2' in request.POST:
            form = Task2Form(request.POST)
            if form.is_valid():
                probs_str = form.cleaned_data['probabilities']
                probs = [float(x.strip()) for x in probs_str.split(',')]
                context['task2_result'] = TaskViewProcessor.process_task2(probs)
            else:
                context['task2_form'] = form
                return render(request, self.template_name, context)

        elif 'task3' in request.POST:
            form = Task3Form(request.POST)
            if form.is_valid():
                p_a = form.cleaned_data['p_a']
                p_b_given_a = form.cleaned_data['p_b_given_a']
                context['task3_result'] = TaskViewProcessor.process_task3(p_a, p_b_given_a)
            else:
                context['task3_form'] = form
                return render(request, self.template_name, context)

        elif 'task4' in request.POST:
            form = Task4Form(request.POST)
            if form.is_valid():
                probs_str = form.cleaned_data['probabilities']
                probs = [float(x.strip()) for x in probs_str.split(',')]
                context['task4_result'] = TaskViewProcessor.process_task4(probs)
            else:
                context['task4_form'] = form
                return render(request, self.template_name, context)

        return render(request, self.template_name, context)
