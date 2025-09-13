import random
from types import SimpleNamespace


class BaseSimulator:
    DISTRIBUTIONS: SimpleNamespace

    @staticmethod
    def generate_uniform() -> float:
        return random.random()
