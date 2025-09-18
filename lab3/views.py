import numpy as np
from django.shortcuts import render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab3.forms import Task1Form, Task2Form
from lab3.services.bivariate_statistical_analysis import (
    BivariateStatisticalAnalysisService,
)
from lab3.services.continuous_bivariate_simulator import ContinuousBivariateSimulator
from lab3.services.discrete_bivariate_simulator import DiscreteBivariateSimulator


class Lab3View(TemplateView):
    template_name = 'lab3/index.html'

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
                    sample_size = form.cleaned_data['sample_size']
                    confidence_level = form.cleaned_data['confidence_level']

                    simulator = ContinuousBivariateSimulator()
                    sample = simulator.generate_sample(sample_size)

                    x_vals, y_vals = BivariateStatisticalAnalysisService.separate_components(sample)

                    stats_x = BivariateStatisticalAnalysisService.calculate_descriptive_stats(x_vals)
                    stats_y = BivariateStatisticalAnalysisService.calculate_descriptive_stats(y_vals)

                    ci_mean_x = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                        x_vals, confidence_level, 'mean'
                    )
                    ci_mean_y = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                        y_vals, confidence_level, 'mean'
                    )

                    ci_std_x = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                        x_vals, confidence_level, 'std'
                    )
                    ci_std_y = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                        y_vals, confidence_level, 'std'
                    )

                    cov = BivariateStatisticalAnalysisService.calculate_covariance(x_vals, y_vals)
                    corr = BivariateStatisticalAnalysisService.calculate_correlation(x_vals, y_vals)

                    independence_test = BivariateStatisticalAnalysisService.test_independence_pearson(
                        x_vals, y_vals, alpha=1-confidence_level
                    )

                    hist_x_base64, hist_y_base64 = (
                        BivariateStatisticalAnalysisService.plot_marginal_histograms_with_density(
                            sample,
                            density_func_x=simulator.marginal_density_x,
                            density_func_y=simulator.marginal_density_y,
                            title_x="Marginal Distribution of X",
                            title_y="Marginal Distribution of Y"
                        )
                    )

                    hist_3d_base64 = None
                    if form.cleaned_data.get('include_3d', False):
                        try:
                            hist_3d_base64 = BivariateStatisticalAnalysisService.plot_3d_histogram_and_density(
                                sample,
                                density_func=simulator.density_function,
                                title="3D Histogram and Density Surface"
                            )
                        except Exception as e:
                            print(f"3D plot failed: {e}")

                    demo_x_values = [-2.0, 0.0, 2.0]
                    conditional_densities_demo = {}
                    y_range = np.linspace(-5, 5, 100)
                    for x_val in demo_x_values:
                        densities = [simulator.conditional_density_y_given_x(y, x_val) for y in y_range]
                        conditional_densities_demo[x_val] = {
                            'y_values': y_range.tolist(),
                            'densities': densities
                        }

                    context['continuous_result'] = {
                        'sample': sample[:10],
                        'sample_size': sample_size,
                        'stats_x': stats_x,
                        'stats_y': stats_y,
                        'ci_mean_x': ci_mean_x,
                        'ci_mean_y': ci_mean_y,
                        'ci_std_x': ci_std_x,
                        'ci_std_y': ci_std_y,
                        'covariance': cov,
                        'correlation': corr,
                        'independence_test': independence_test,
                        'histogram_x': hist_x_base64,
                        'histogram_y': hist_y_base64,
                        'histogram_3d': hist_3d_base64,
                        'conditional_densities_demo': conditional_densities_demo,
                        'confidence_level': confidence_level,
                    }
                except Exception as e:
                    form.add_error(None, f"Error in continuous simulation: {e}")
                    context['continuous_form'] = form
            else:
                context['continuous_form'] = form

        elif 'run_discrete' in request.POST:
            form = Task2Form(request.POST)
            if form.is_valid():
                try:
                    prob_matrix = form.cleaned_data['distribution_matrix']
                    sample_size = form.cleaned_data['sample_size']
                    confidence_level = form.cleaned_data['confidence_level']

                    simulator = DiscreteBivariateSimulator(prob_matrix)
                    sample = simulator.generate_sample(sample_size)

                    x_vals, y_vals = BivariateStatisticalAnalysisService.separate_components(sample)

                    try:
                        numeric_x = [float(x) for x in x_vals]
                        numeric_y = [float(y) for y in y_vals]
                        stats_x = BivariateStatisticalAnalysisService.calculate_descriptive_stats(numeric_x)
                        stats_y = BivariateStatisticalAnalysisService.calculate_descriptive_stats(numeric_y)

                        ci_mean_x = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                            numeric_x, confidence_level, 'mean'
                        )
                        ci_mean_y = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                            numeric_y, confidence_level, 'mean'
                        )

                        ci_std_x = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                            numeric_x, confidence_level, 'std'
                        )
                        ci_std_y = BivariateStatisticalAnalysisService.calculate_confidence_interval(
                            numeric_y, confidence_level, 'std'
                        )

                        cov = BivariateStatisticalAnalysisService.calculate_covariance(numeric_x, numeric_y)
                        corr = BivariateStatisticalAnalysisService.calculate_correlation(numeric_x, numeric_y)

                        independence_test = BivariateStatisticalAnalysisService.test_independence_pearson(
                            numeric_x, numeric_y, alpha=1 - confidence_level
                        )
                    except (ValueError, TypeError):
                        stats_x = stats_y = ci_mean_x = ci_mean_y = ci_std_x = ci_std_y = None
                        cov = corr = None
                        independence_test = {
                            'test_name': 'Pearson Correlation t-test',
                            'interpretation': 'Cannot perform test: X or Y contains non-numeric values.'
                        }

                    chart_x_base64 = BivariateStatisticalAnalysisService.plot_histogram(
                        x_vals, is_continuous=False, title="Marginal Distribution of X"
                    )
                    chart_y_base64 = BivariateStatisticalAnalysisService.plot_histogram(
                        y_vals, is_continuous=False, title="Marginal Distribution of Y"
                    )

                    chart_3d_base64 = None
                    if form.cleaned_data.get('include_3d', False):
                        try:
                            chart_3d_base64 = BivariateStatisticalAnalysisService.plot_discrete_3d_histogram(
                                sample,
                                prob_matrix,
                                title="3D Histogram: Observed vs Theoretical"
                            )
                        except Exception as e:
                            form.add_error(None, f"3D discrete plot generation failed: {e}")

                    marginal_x = simulator.get_marginal_x()
                    conditional_distributions = {}
                    for x_val in marginal_x.keys():
                        cond_dist = simulator.get_conditional_y_given_x(x_val)
                        conditional_distributions[x_val] = cond_dist

                    context['discrete_result'] = {
                        'sample': sample[:10],
                        'sample_size': sample_size,
                        'distribution_matrix': prob_matrix,
                        'stats_x': stats_x,
                        'stats_y': stats_y,
                        'ci_mean_x': ci_mean_x,
                        'ci_mean_y': ci_mean_y,
                        'ci_std_x': ci_std_x,
                        'ci_std_y': ci_std_y,
                        'covariance': cov,
                        'correlation': corr,
                        'independence_test': independence_test,
                        'chart_x': chart_x_base64,
                        'chart_y': chart_y_base64,
                        'chart_3d': chart_3d_base64,
                        'marginal_x': marginal_x,
                        'conditional_distributions': conditional_distributions,
                        'confidence_level': confidence_level,
                    }
                except Exception as e:
                    form.add_error(None, f"Error in discrete simulation: {e}")
                    context['discrete_form'] = form
            else:
                context['discrete_form'] = form

        return render(request, self.template_name, context)
