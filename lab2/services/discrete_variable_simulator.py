from types import SimpleNamespace

from scipy import stats

from lab2.services.base_simulator import BaseSimulator


class DiscreteVariableSimulator(BaseSimulator):
    DISTRIBUTIONS = SimpleNamespace(
        randint=stats.randint,
        binom=stats.binom,
        geom=stats.geom,
        poisson=stats.poisson,
    )

    @classmethod
    def simulate_discrete_custom(cls, values: list[int | str], probabilities: list[float]) -> int | str:
        if len(values) != len(probabilities):
            raise ValueError("The 'values' and 'probabilities' lists must have the same length.")

        if abs(sum(probabilities) - 1.0) > 1e-10:
            raise ValueError("The sum of the probabilities should be equal to 1.")

        uniform_value = cls.generate_uniform()

        cumsum = 0.0
        cumsums = [cumsum]
        for p in probabilities:
            cumsum += p
            cumsums.append(cumsum)

        for i in range(len(cumsums) - 1):
            if cumsums[i] <= uniform_value < cumsums[i + 1] or (i == len(cumsums) - 2 and uniform_value == 1.0):
                return values[i]

        raise RuntimeError(f"The interval for the {uniform_value} value could not be determined. "
                           f"Cumulative sums: {cumsums}.")

    @classmethod
    def generate_sample_custom(cls, values: list[int | str], probabilities: list[float], size: int) -> list[int | str]:
        if size <= 0:
            raise ValueError("The sample size should be positive.")
        return [cls.simulate_discrete_custom(values, probabilities) for _ in range(size)]
