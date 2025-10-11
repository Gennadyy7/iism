from typing import Any

from lab4.services.balance_equations_solver import BalanceEquationsSolver
from lab4.services.performance_metrics import PerformanceMetrics
from lab4.services.priority_queue_model import PriorityQueueModel


class SMOService:
    def __init__(self, r: int, lambda1: float, lambda2: float, mu1: float, mu2: float):
        self.model = PriorityQueueModel(r, lambda1, lambda2, mu1, mu2)

    def analyze(self) -> dict[str, Any]:
        transitions = self.model.get_transitions()
        solver = BalanceEquationsSolver(transitions)
        probs = solver.solve()
        metrics = PerformanceMetrics(probs, self.model.l1, self.model.l2, self.model.m1, self.model.m2)

        transition_desc = self.model.get_transition_descriptions()
        balance_eqs = solver.get_balance_equations()

        report: dict[str, Any] = {
            'states': probs,
            'blocking': metrics.blocking_probabilities(),
            'entrance_intensities': metrics.entrance_intensities(),
            'served': metrics.served_probabilities(),
            'average_counts': metrics.average_counts(),
            'queue_lengths': metrics.average_queue_lengths(),
            'times': metrics.average_times(),
            'transitions': transition_desc,
            'balance_equations': balance_eqs,
        }
        return report
