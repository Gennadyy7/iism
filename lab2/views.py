from django.shortcuts import render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab2.forms import Task1Form, Task2Form
from lab2.services.continuous_variable_simulator import ContinuousVariableSimulator
from lab2.services.discrete_variable_simulator import DiscreteVariableSimulator
from lab2.services.statistical_analysis import StatisticalAnalysisService


class Lab2View(TemplateView):
    template_name = 'lab2/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['continuous_form'] = Task1Form()
        context['discrete_form'] = Task2Form()
        return context

    @handle_lab_exceptions
    def post(self, request):
        context = self.get_context_data()

        if 'run_continuous' in request.POST:
            form = Task1Form(request.POST)
            if form.is_valid():
                try:
                    distribution = form.get_scipy_distribution()
                    sample_size = form.cleaned_data['sample_size']

                    sample = ContinuousVariableSimulator.generate_sample(distribution, sample_size)

                    descriptive_stats = StatisticalAnalysisService.calculate_descriptive_stats(sample)
                    ci_mean_result = StatisticalAnalysisService.calculate_confidence_interval(
                        sample,
                        0.95,
                        'mean'
                    )
                    histogram_base64 = StatisticalAnalysisService.plot_histogram(
                        sample,
                        is_continuous=True,
                        title=f"Histogram of {form.cleaned_data['distribution']} sample"
                    )

                    ks_test_result = StatisticalAnalysisService.test_distribution_fit(
                        sample,
                        distribution,
                        is_continuous=True
                    )

                    context['continuous_result'] = {
                        'sample': sample[:20],
                        'descriptive_stats': descriptive_stats,
                        'ci_mean': ci_mean_result,
                        'histogram': histogram_base64,
                        'ks_test': ks_test_result,
                        'distribution_name': form.cleaned_data['distribution'],
                        'params': f"param1={form.cleaned_data['param1']}, param2={form.cleaned_data['param2']}",
                        'sample_size': sample_size
                    }
                except Exception as e:
                    form.add_error(None, f"Error during simulation or analysis: {e}")
                    context['continuous_form'] = form
            else:
                context['continuous_form'] = form

        elif 'run_discrete' in request.POST:
            form = Task2Form(request.POST)
            if form.is_valid():
                try:
                    values_list, probabilities_list = form.get_simulation_params()
                    sample_size = form.cleaned_data['sample_size']

                    sample = DiscreteVariableSimulator.generate_sample_custom(
                        values_list, probabilities_list, sample_size
                    )

                    if all(isinstance(v, (int, float)) for v in values_list):
                        numeric_sample_for_analysis = sample
                        sample_for_plotting = sample
                    else:
                        value_to_num_map = {v: i for i, v in enumerate(sorted(set(values_list)))}
                        numeric_sample_for_analysis = [value_to_num_map[v] for v in sample]
                        sample_for_plotting = sample

                    descriptive_stats = StatisticalAnalysisService.calculate_descriptive_stats(
                        numeric_sample_for_analysis
                    )
                    ci_mean_result = StatisticalAnalysisService.calculate_confidence_interval(
                        numeric_sample_for_analysis, 0.95, 'mean'
                    )
                    chart_base64 = StatisticalAnalysisService.plot_histogram(
                        sample_for_plotting, is_continuous=False,
                        title=f"Frequency Chart for custom discrete distribution"
                    )

                    expected_dist_dict = dict(zip(values_list, probabilities_list))
                    chi2_test_result = StatisticalAnalysisService.test_distribution_fit(
                        sample, expected_dist_dict, is_continuous=False
                    )

                    context['discrete_result'] = {
                        'sample': sample[:20],
                        'descriptive_stats': descriptive_stats,
                        'ci_mean': ci_mean_result,
                        'chart': chart_base64,
                        'chi2_test': chi2_test_result,
                        'values': str(values_list),
                        'probabilities': str(probabilities_list),
                        'sample_size': sample_size
                    }
                except Exception as e:
                    form.add_error(None, f"Error during simulation or analysis: {e}")
                    context['discrete_form'] = form
            else:
                context['discrete_form'] = form

        return render(request, self.template_name, context)
