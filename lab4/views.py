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

    @staticmethod
    def _safe_abs_error(a, b):
        if a is not None and b is not None:
            return abs(a - b)
        return None

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

                simulation_time = form.cleaned_data.get('simulation_time')
                seed = form.cleaned_data.get('random_seed')

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

                sim_report = service.simulate(simulation_time=simulation_time, seed=seed)

                context['result'] = {
                    'steady_state': [
                        {'state': str(k), 'probability': round(v, 6)}
                        for k, v in steady_state_probs.items()
                    ],
                    'metrics': {
                        k: round(v, 6) if v is not None else None
                        for k, v in metrics.items()
                    },
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
                        'mu2': mu2,
                        'simulation_time': simulation_time,
                        'random_seed': seed,
                    },
                    'transitions': report['transitions'],
                    'balance_equations': report['balance_equations'],
                    'simulation': {
                        'metrics': {
                            k: round(v, 6) if v is not None else None
                            for k, v in sim_report['times'].items()
                        },
                        'blocking': sim_report['blocking'],
                        'entrance_intensities': sim_report['entrance_intensities'],
                        'served': sim_report['served'],
                        'average_counts': sim_report['average_counts'],
                        'queue_lengths': sim_report['queue_lengths'],
                        'simulation_time': simulation_time,
                        'arrivals': sim_report['arrivals'],
                    },
                    'comparison': {
                        'metrics': {
                            k: self._safe_abs_error(
                                round(metrics.get(k), 6) if metrics.get(k) is not None else None,
                                round(sim_report['times'].get(k), 6) if sim_report['times'].get(k) is not None else None
                            )
                            for k in set(metrics.keys()) | set(sim_report['times'].keys())
                        },
                        'blocking': {
                            k: self._safe_abs_error(report['blocking'].get(k), sim_report['blocking'].get(k))
                            for k in set(report['blocking'].keys()) | set(sim_report['blocking'].keys())
                        },
                        'average_counts': {
                            k: self._safe_abs_error(report['average_counts'].get(k),
                                                    sim_report['average_counts'].get(k))
                            for k in set(report['average_counts'].keys()) | set(sim_report['average_counts'].keys())
                        },
                        'queue_lengths': {
                            k: self._safe_abs_error(report['queue_lengths'].get(k), sim_report['queue_lengths'].get(k))
                            for k in set(report['queue_lengths'].keys()) | set(sim_report['queue_lengths'].keys())
                        },
                    },
                }

            except Exception as e:
                form.add_error(None, f"Error during model calculation: {e}")
                context['form'] = form
        else:
            context['form'] = form

        return render(request, self.template_name, context)
