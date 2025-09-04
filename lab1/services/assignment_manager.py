from collections import Counter

from lab1.services.event_simulator import EventSimulator


class AssignmentManager:
    def __init__(self, generation_rate: int = 10**6):
        if not generation_rate > 0:
            raise ValueError("The generation rate must be greater than 0.")
        self.generation_rate = generation_rate

    def run_task1(self, p: float) -> tuple[float, float]:
        freq = sum(EventSimulator.simulate_simple_event(p) for _ in range(self.generation_rate)) / self.generation_rate
        return freq, p

    def run_task2(self, probs: list[float] | tuple[float, ...]) -> tuple[list[float], list[float]]:
        results = [EventSimulator.simulate_independent_events(probs) for _ in range(self.generation_rate)]
        freqs = [sum(r[i] for r in results) / self.generation_rate for i in range(len(probs))]
        return freqs, list(probs)

    def run_task3(self, p_a: float, p_b_given_a: float) -> tuple[dict[int, float], dict[int, float]]:
        counts = Counter(EventSimulator.simulate_dependent_event(p_a, p_b_given_a) for _ in range(self.generation_rate))
        freqs = {k: v / self.generation_rate for k, v in counts.items()}

        p_b_given_not_a = 1 - p_b_given_a
        theory = {
            0: p_a * p_b_given_a,
            1: p_a * (1 - p_b_given_a),
            2: (1 - p_a) * p_b_given_not_a,
            3: (1 - p_a) * (1 - p_b_given_not_a)
        }
        return freqs, theory

    def run_task4(self, probs: list[float] | tuple[float, ...]) -> tuple[dict[int, float], dict[int, float]]:
        counts = Counter(EventSimulator.simulate_complete_group_event(probs) for _ in range(self.generation_rate))
        freqs = {k: v / self.generation_rate for k, v in counts.items()}
        theory = {i: p for i, p in enumerate(probs)}
        return freqs, theory
