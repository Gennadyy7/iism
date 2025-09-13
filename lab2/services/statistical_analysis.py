import base64
import io

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.stats._unuran.unuran_wrapper import rv_frozen


class StatisticalAnalysisService:
    @staticmethod
    def calculate_descriptive_stats(sample: list[float | int]) -> dict:
        sample_array = np.array(sample)
        return {
            'mean': float(np.mean(sample_array)),
            'median': float(np.median(sample_array)),
            'std': float(np.std(sample_array, ddof=1)),
            'var': float(np.var(sample_array, ddof=1)),
            'min': float(np.min(sample_array)),
            'max': float(np.max(sample_array)),
            'size': len(sample)
        }

    @staticmethod
    def calculate_confidence_interval(
            sample: list[float | int],
            confidence_level: float = 0.95,
            parameter: str = 'mean'
    ) -> tuple[float, float, float]:
        sample_array = np.array(sample)
        alpha = 1 - confidence_level

        if parameter == 'mean':
            point_estimate = np.mean(sample_array)
            ci = stats.t.interval(
                confidence_level,
                df=len(sample_array) - 1,
                loc=point_estimate,
                scale=stats.sem(sample_array)
            )
        elif parameter == 'std':
            point_estimate = np.std(sample_array, ddof=1)
            chi2_lower = stats.chi2.ppf(1 - alpha / 2, df=len(sample_array) - 1)
            chi2_upper = stats.chi2.ppf(alpha / 2, df=len(sample_array) - 1)
            ci_lower = np.sqrt((len(sample_array) - 1) * (point_estimate ** 2) / chi2_lower)
            ci_upper = np.sqrt((len(sample_array) - 1) * (point_estimate ** 2) / chi2_upper)
            ci = (ci_lower, ci_upper)
        else:
            raise ValueError("The parameter must be 'mean' or 'std'.")

        return float(ci[0]), float(point_estimate), float(ci[1])

    @staticmethod
    def plot_histogram(
            sample: list[float | int],
            is_continuous: bool = True,
            bins: int | None = None,
            title: str = "Histogram"
    ) -> str:
        plt.figure(figsize=(8, 6))
        sample_array = np.array(sample)

        if is_continuous:
            if bins is None:
                bins = int(np.ceil(np.log2(len(sample_array)) + 1))
            plt.hist(sample_array, bins=bins, density=True, alpha=0.7, color='skyblue', edgecolor='black')
            plt.ylabel('Density')
        else:
            unique_vals, counts = np.unique(sample_array, return_counts=True)
            freqs = counts / len(sample_array)
            plt.bar(unique_vals, freqs, alpha=0.7, color='lightcoral', edgecolor='black')
            plt.ylabel('Relative Frequency')
            plt.xticks(unique_vals)

        plt.xlabel('Values')
        plt.title(title)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return image_base64

    @staticmethod
    def test_distribution_fit(
            sample: list[float | int],
            expected_dist: rv_frozen | dict,
            is_continuous: bool = True,
            alpha: float = 0.05
    ) -> dict:
        sample_array = np.array(sample)

        if is_continuous:
            if not isinstance(expected_dist, rv_frozen):
                raise ValueError("For a continuous test, expected_dist should be a "
                                 "continuous distribution object of scipy.stats.")

            ks_statistic, p_value = stats.kstest(sample_array, expected_dist.cdf)
            return {
                'test_name': 'Kolmogorov-Smirnov',
                'statistic': float(ks_statistic),
                'p_value': float(p_value),
                'alpha': alpha,
                'reject_null': p_value < alpha,
                'interpretation': f"{'Reject' if p_value < alpha else 'Do not reject'} "
                                  f"the null hypothesis at significance level {alpha}."
            }
        else:
            if not isinstance(expected_dist, dict):
                raise ValueError("For a discrete test, expected_dist should be a dictionary {value: probability}.")

            unique_vals, counts = np.unique(sample_array, return_counts=True)
            observed_freq = dict(zip(unique_vals, counts))

            expected_freq_list = []
            observed_freq_list = []

            for val in unique_vals:
                exp_prob = expected_dist.get(val, 0)
                expected_freq_list.append(exp_prob * len(sample_array))
                observed_freq_list.append(observed_freq.get(val, 0))

            filtered_pairs = [(obs, exp) for obs, exp in zip(observed_freq_list, expected_freq_list) if exp > 0]

            if not filtered_pairs or len(filtered_pairs) < 2:
                return {
                    'test_name': 'Chi-squared',
                    'statistic': None,
                    'p_value': None,
                    'alpha': alpha,
                    'reject_null': None,
                    'interpretation': "The test cannot be performed: "
                                      "there are not enough bins with a non-zero expected frequency."
                }

            filtered_obs, filtered_exp = zip(*filtered_pairs)

            chi2_stat, p_value = stats.chisquare(f_obs=filtered_obs, f_exp=filtered_exp)

            return {
                'test_name': 'Chi-squared',
                'statistic': float(chi2_stat),
                'p_value': float(p_value),
                'alpha': alpha,
                'reject_null': p_value < alpha,
                'interpretation': f"{'Reject' if p_value < alpha else 'Do not reject'} "
                                  f"the null hypothesis at significance level {alpha}."
            }
