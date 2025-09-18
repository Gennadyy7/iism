import math

from lab3.services.base_bivariate_simulator import BaseBivariateSimulator


class ContinuousBivariateSimulator(BaseBivariateSimulator):
    def __init__(self):
        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -10.0, 10.0
        self.area = (self.x_max - self.x_min) * (self.y_max - self.y_min)

        self.f_max = 1 / (2 * (math.pi ** 3))

    @staticmethod
    def density_function(x: float, y: float) -> float:
        denominator = (math.pi ** 2 + x ** 2 + y ** 2) ** 1.5
        return 1 / (2 * denominator)

    def _generate_candidate(self) -> tuple[float, float]:
        u1 = self.generate_uniform()
        u2 = self.generate_uniform()
        x = self.x_min + u1 * (self.x_max - self.x_min)
        y = self.y_min + u2 * (self.y_max - self.y_min)
        return x, y

    def simulate_single(self) -> tuple[float, float]:
        while True:
            x, y = self._generate_candidate()
            f_xy = self.density_function(x, y)
            u = self.generate_uniform()
            if u <= f_xy / self.f_max:
                return x, y

    @staticmethod
    def marginal_density_x(x: float) -> float:
        return 1 / (math.pi * (math.pi ** 2 + x ** 2))

    @staticmethod
    def marginal_density_y(y: float) -> float:
        return 1 / (math.pi * (math.pi ** 2 + y ** 2))

    def conditional_density_y_given_x(self, y: float, x: float) -> float:
        f_xy = self.density_function(x, y)
        f_x = self.marginal_density_x(x)
        return f_xy / f_x if f_x > 0 else 0.0

    def conditional_density_x_given_y(self, x: float, y: float) -> float:
        f_xy = self.density_function(x, y)
        f_y = self.marginal_density_y(y)
        return f_xy / f_y if f_y > 0 else 0.0
