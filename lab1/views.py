from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab1.forms import (
    Task1Form,
    Task2Form,
    Task3Form,
    Task4Form,
    TeamForm,
    TournamentRunForm,
)
from lab1.models import Team
from lab1.services.task_view_processor import TaskViewProcessor
from lab1.services.tournament_simulator import TournamentSimulator


class Lab1View(TemplateView):
    template_name = 'lab1/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task1_form'] = Task1Form()
        context['task2_form'] = Task2Form()
        context['task3_form'] = Task3Form()
        context['task4_form'] = Task4Form()

        context['teams'] = Team.objects.all()
        context['team_form'] = TeamForm()
        context['tournament_run_form'] = TournamentRunForm()
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

        elif 'task2' in request.POST:
            form = Task2Form(request.POST)
            if form.is_valid():
                probs_str = form.cleaned_data['probabilities']
                probs = [float(x.strip()) for x in probs_str.split(',')]
                context['task2_result'] = TaskViewProcessor.process_task2(probs)
            else:
                context['task2_form'] = form

        elif 'task3' in request.POST:
            form = Task3Form(request.POST)
            if form.is_valid():
                p_a = form.cleaned_data['p_a']
                p_b_given_a = form.cleaned_data['p_b_given_a']
                context['task3_result'] = TaskViewProcessor.process_task3(p_a, p_b_given_a)
            else:
                context['task3_form'] = form

        elif 'task4' in request.POST:
            form = Task4Form(request.POST)
            if form.is_valid():
                probs_str = form.cleaned_data['probabilities']
                probs = [float(x.strip()) for x in probs_str.split(',')]
                context['task4_result'] = TaskViewProcessor.process_task4(probs)
            else:
                context['task4_form'] = form

        elif 'add_team' in request.POST:
            form = TeamForm(request.POST)
            if form.is_valid():
                form.save()
            else:
                context['team_form'] = form

        elif 'delete_team' in request.POST:
            team_id = request.POST.get('team_id')
            if team_id:
                team = get_object_or_404(Team, id=team_id)
                team.delete()

        elif 'run_tournament' in request.POST:
            form = TournamentRunForm(request.POST)
            if form.is_valid():
                teams_qs = Team.objects.all()
                simulator = TournamentSimulator(teams_qs)
                simulator.run_tournament()
                result = simulator.get_tournament_result()
                context['tournament_result'] = result
            else:
                context['tournament_run_form'] = form

        return render(request, self.template_name, context)
