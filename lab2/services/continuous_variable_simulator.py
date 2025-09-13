from types import SimpleNamespace

from scipy import stats
from scipy.stats._distn_infrastructure import rv_frozen

from lab2.services.base_simulator import BaseSimulator


class ContinuousVariableSimulator(BaseSimulator):
    DISTRIBUTIONS = SimpleNamespace(
        norm=stats.norm,
        expon=stats.expon,
        gamma=stats.gamma,
        lognorm=stats.lognorm,
        uniform=stats.uniform,
        beta=stats.beta
    )

    @classmethod
    def simulate_inverse_transform(cls, distribution: rv_frozen) -> float:
        uniform_value = cls.generate_uniform()
        inverse_cdf = distribution.ppf
        return inverse_cdf(uniform_value)

    @classmethod
    def generate_sample(cls, distribution: rv_frozen, size: int) -> list[float]:
        if size <= 0:
            raise ValueError("The sample size should be positive.")
        return [cls.simulate_inverse_transform(distribution) for _ in range(size)]
