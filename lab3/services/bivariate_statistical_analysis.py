import base64
import io
from collections import Counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from lab2.services.statistical_analysis import StatisticalAnalysisService as BaseSAS


class BivariateStatisticalAnalysisService(BaseSAS):
    @staticmethod
    def separate_components(sample: list[tuple[float, float]]) -> tuple[list[float], list[float]]:
        x_list = []
        y_list = []
        for x, y in sample:
            x_list += [x]
            y_list += [y]
        return x_list, y_list

    @staticmethod
    def calculate_covariance(x: list[float], y: list[float]) -> float:
        x_arr = np.array(x)
        y_arr = np.array(y)
        return float(np.cov(x_arr, y_arr, ddof=1)[0, 1])

    @staticmethod
    def calculate_correlation(x: list[float], y: list[float]) -> float:
        if len(x) < 2:
            return 0.0
        x_arr = np.array(x)
        y_arr = np.array(y)
        corr = np.corrcoef(x_arr, y_arr)[0, 1]
        return float(corr) if not np.isnan(corr) else 0.0

    @staticmethod
    def test_independence_pearson(x: list[float], y: list[float], alpha: float = 0.05) -> dict[str, Any]:
        n = len(x)
        if n < 3:
            return {
                'test_name': 'Pearson Correlation t-test',
                'statistic': None,
                'p_value': None,
                'alpha': alpha,
                'reject_null': None,
                'interpretation': "There is not enough data for the test."
            }

        r = BivariateStatisticalAnalysisService.calculate_correlation(x, y)
        t_stat = r * np.sqrt((n - 2) / (1 - r ** 2)) if abs(r) < 1 else float('inf')
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n - 2))

        return {
            'test_name': 'Pearson Correlation t-test',
            'correlation_estimate': r,
            'statistic': float(t_stat),
            'p_value': float(p_value),
            'alpha': alpha,
            'reject_null': p_value < alpha,
            'interpretation': f"{'Reject' if p_value < alpha else 'Fail to reject'} "
                              f"the hypothesis of independence (zero correlation) at the {alpha} significance level."
        }

    @staticmethod
    def plot_marginal_histograms_with_density(
            sample: list[tuple[float, float]],
            density_func_x=None,
            density_func_y=None,
            title_x: str = "Histogram X",
            title_y: str = "Histogram Y"
    ) -> tuple[str, str]:
        x_vals, y_vals = BivariateStatisticalAnalysisService.separate_components(sample)

        def plot_single(val_array, density_func, title):
            plt.figure(figsize=(8, 6))
            bins = int(np.ceil(np.log2(len(val_array)) + 1))
            plt.hist(
                val_array,
                bins=bins,
                density=True,
                alpha=0.7,
                color='skyblue',
                edgecolor='black',
                label='Histogram',
            )

            if density_func is not None:
                x_min, x_max = plt.xlim()
                x_range = np.linspace(x_min, x_max, 500)
                y_density = [density_func(x) for x in x_range]
                plt.plot(x_range, y_density, 'r-', linewidth=2, label='Theoretical Density')

            plt.xlabel('Values')
            plt.ylabel('Density')
            plt.title(title)
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')

        img_x = plot_single(x_vals, density_func_x, title_x)
        img_y = plot_single(y_vals, density_func_y, title_y)

        return img_x, img_y

    @staticmethod
    def plot_3d_histogram_and_density(
            sample: list[tuple[float, float]],
            density_func=None,
            title: str = "3D Histogram and Distribution Density"
    ) -> str:
        x_vals_list, y_vals_list = BivariateStatisticalAnalysisService.separate_components(sample)

        x_vals = np.array(x_vals_list)
        y_vals = np.array(y_vals_list)

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        n_bins = int(np.ceil(np.power(len(sample), 1/3)))
        hist, x_edges, y_edges = np.histogram2d(x_vals, y_vals, bins=n_bins, density=True)

        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2
        x_mesh, y_mesh = np.meshgrid(x_centers, y_centers)

        dx = (x_edges[1] - x_edges[0]) * 0.8
        dy = (y_edges[1] - y_edges[0]) * 0.8
        ax.bar3d(x_mesh.ravel(), y_mesh.ravel(), np.zeros_like(hist).ravel(),
                 dx, dy, hist.T.ravel(), shade=True, alpha=0.7, color='skyblue')

        if density_func is not None:
            x_surf = np.linspace(x_vals.min(), x_vals.max(), 50)
            y_surf = np.linspace(y_vals.min(), y_vals.max(), 50)
            x_data_value, y_data_value = np.meshgrid(x_surf, y_surf)
            z_data_value = np.array([[density_func(x, y) for x in x_surf] for y in y_surf])

            ax.plot_surface(X=x_data_value, Y=y_data_value, Z=z_data_value, color='red', alpha=0.3, linewidth=0)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Density')
        ax.set_title(title)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    @staticmethod
    def plot_discrete_3d_histogram(
        sample: list[tuple[Any, Any]],
        theoretical_prob_matrix: dict[tuple[Any, Any], float],
        title: str = "3D Histogram: Observed vs Theoretical"
    ) -> str:
        sample_counter = Counter(sample)
        n = len(sample)

        all_pairs = list(theoretical_prob_matrix.keys())
        observed_freq = [sample_counter.get(pair, 0) / n for pair in all_pairs]
        theoretical_prob = [theoretical_prob_matrix[pair] for pair in all_pairs]

        x_vals = [pair[0] for pair in all_pairs]
        y_vals = [pair[1] for pair in all_pairs]

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.bar3d(x_vals, y_vals, [0] * len(x_vals), 0.5, 0.5, observed_freq,
                 color='skyblue', alpha=0.8, label='Observed Frequency')

        ax.bar3d([x + 0.25 for x in x_vals], [y + 0.25 for y in y_vals], [0] * len(x_vals),
                 0.5, 0.5, theoretical_prob,
                 color='red', alpha=0.8, label='Theoretical Probability')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Probability / Frequency')
        ax.set_title(title)
        ax.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return image_base64
