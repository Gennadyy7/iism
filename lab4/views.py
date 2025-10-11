from django.shortcuts import render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab4.forms import PriorityQueueForm
from lab4.services.smo_service import SMOService


class Lab4View(TemplateView):
    template_name = 'lab4/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PriorityQueueForm()
        return context

    @handle_lab_exceptions
    def post(self, request):
        context = self.get_context_data()
        form = PriorityQueueForm(request.POST)

        if form.is_valid():
            try:
                r = form.cleaned_data['queue_length']
                lambda1 = form.cleaned_data['lambda1']
                lambda2 = form.cleaned_data['lambda2']
                mu1 = form.cleaned_data['mu1']
                mu2 = form.cleaned_data['mu2']

                service = SMOService(
                    r=r,
                    lambda1=lambda1,
                    lambda2=lambda2,
                    mu1=mu1,
                    mu2=mu2
                )

                report = service.analyze()
                steady_state_probs = report['states']
                metrics = report['times']

                context['result'] = {
                    'steady_state': [
                        {'state': str(k), 'probability': round(v, 6)}
                        for k, v in steady_state_probs.items()
                    ],
                    'metrics': {k: round(v, 6) for k, v in metrics.items()},
                    'blocking': report['blocking'],
                    'entrance_intensities': report['entrance_intensities'],
                    'served': report['served'],
                    'average_counts': report['average_counts'],
                    'queue_lengths': report['queue_lengths'],
                    'input_params': {
                        'queue_length': r,
                        'lambda1': lambda1,
                        'lambda2': lambda2,
                        'mu1': mu1,
                        'mu2': mu2
                    },
                    'transitions': report['transitions'],
                    'balance_equations': report['balance_equations'],
                }

            except Exception as e:
                form.add_error(None, f"Error during model calculation: {e}")
                context['form'] = form
        else:
            context['form'] = form

        return render(request, self.template_name, context)
