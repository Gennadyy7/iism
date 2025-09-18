import random
from abc import ABC, abstractmethod


class BaseBivariateSimulator(ABC):
    @staticmethod
    def generate_uniform() -> float:
        return random.random()

    @abstractmethod
    def simulate_single(self) -> tuple[float, float]:
        pass

    def generate_sample(self, size: int) -> list[tuple[float, float]]:
        if size <= 0:
            raise ValueError("The sample size should be positive.")
        return [self.simulate_single() for _ in range(size)]
