from typing import Any

from lab3.services.base_bivariate_simulator import BaseBivariateSimulator


class DiscreteBivariateSimulator(BaseBivariateSimulator):
    def __init__(self, probability_matrix: dict[tuple[Any, Any], float]):
        if abs(sum(probability_matrix.values()) - 1.0) > 1e-10:
            raise ValueError("The sum of probabilities must be equal to 1.")

        self.probability_matrix = probability_matrix
        self.pairs = list(probability_matrix.keys())
        self.probabilities = list(probability_matrix.values())

        self.cumsums = []
        cumsum = 0.0
        for p in self.probabilities:
            self.cumsums.append(cumsum)
            cumsum += p
        self.cumsums.append(cumsum)

    def simulate_single(self) -> tuple[Any, Any]:
        u = self.generate_uniform()
        for i in range(len(self.cumsums) - 1):
            if self.cumsums[i] <= u < self.cumsums[i + 1] or (i == len(self.cumsums) - 2 and u == 1.0):
                return self.pairs[i]
        raise RuntimeError("Failed to determine the interval for the value.")

    def get_marginal_x(self) -> dict[Any, float]:
        marginal = {}
        for (x, y), p in self.probability_matrix.items():
            marginal[x] = marginal.get(x, 0.0) + p
        return marginal

    def get_marginal_y(self) -> dict[Any, float]:
        marginal = {}
        for (x, y), p in self.probability_matrix.items():
            marginal[y] = marginal.get(y, 0.0) + p
        return marginal

    def get_conditional_y_given_x(self, x_value) -> dict[Any, float]:
        conditional = {}
        total_prob_x = self.get_marginal_x().get(x_value, 0.0)
        if total_prob_x == 0.0:
            return conditional

        for (x, y), p in self.probability_matrix.items():
            if x == x_value:
                conditional[y] = p / total_prob_x

        return conditional
