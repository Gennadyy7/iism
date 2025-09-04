import random


class EventSimulator:
    @staticmethod
    def _probability_validation(probability: float | list[float] | tuple[float, ...]) -> None:
        if isinstance(probability, (int, float)):
            probabilities = [float(probability)]
        elif isinstance(probability, (list, tuple)):
            probabilities = [float(p) for p in probability]

        for i, p in enumerate(probabilities):
            if not 0 <= p <= 1:
                raise ValueError(f"Element {i}: the probability should be between 0 and 1, obtained {p}.")

    @classmethod
    def simulate_simple_event(cls, probability: float) -> bool:
        cls._probability_validation(probability)
        return random.random() < probability

    @classmethod
    def simulate_independent_events(cls, probabilities: list[float]) -> list[bool]:
        return [cls.simulate_simple_event(p) for p in probabilities]

    @classmethod
    def simulate_dependent_event(cls, p_a: float, p_b_given_a: float) -> int:
        cls._probability_validation([p_a, p_b_given_a])

        p_b_given_not_a = 1 - p_b_given_a
        a = random.random() < p_a
        b = random.random() < (p_b_given_a if a else p_b_given_not_a)

        match a, b:
            case True, True:
                return 0
            case True, False:
                return 1
            case False, True:
                return 2
            case _:
                return 3

    @classmethod
    def simulate_complete_group_event(cls, probabilities: list[float]) -> int:
        if len(probabilities) == 0:
            raise ValueError("The list of probabilities cannot be empty")

        cls._probability_validation(probabilities)

        total = sum(probabilities)
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"The sum of the probabilities should be 1, resulting in {total}.")

        r = random.random()
        cumulative = 0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r < cumulative:
                return i
        return len(probabilities) - 1  # protection against rounding errors
