from lab4.services.base_queue_model import BaseQueueModel


class PriorityQueueModel(BaseQueueModel):
    def __init__(self, r: int, lambda1: float, lambda2: float, mu1: float, mu2: float):
        super().__init__(r)
        for name, val in (('lambda1', lambda1), ('lambda2', lambda2), ('mu1', mu1), ('mu2', mu2)):
            if val <= 0:
                raise ValueError(f"{name} must be > 0")

        self.l1 = float(lambda1)
        self.l2 = float(lambda2)
        self.m1 = float(mu1)
        self.m2 = float(mu2)

        self.states = self.get_states()
        self.transitions = self._build_transitions()

    def _build_transitions(self) -> dict[tuple[int, int], dict[tuple[int, int], float]]:
        trans: dict[tuple[int, int], dict[tuple[int, int], float]] = {}

        for s in self.states:
            i, j = s.i, s.j
            current = (i, j)
            trans[current] = {}

            total = i + j

            if total < self.K:
                next_state = (i + 1, j)
                trans[current][next_state] = self.l1
            elif total == self.K and i == 0:
                next_state = (1, self.K - 1)
                trans[current][next_state] = self.l1

            if total < self.K:
                next_state = (i, j + 1)
                trans[current][next_state] = self.l2

            if i > 0:
                next_state = (i - 1, j)
                trans[current][next_state] = self.m1
            elif j > 0:
                next_state = (i, j - 1)
                trans[current][next_state] = self.m2
        return trans

    def get_transitions(self) -> dict[tuple[int, int], dict[tuple[int, int], float]]:
        return self.transitions

    def debug_print(self) -> None:
        for state, outs in sorted(self.transitions.items()):
            outs_str = ", ".join(f"{t}:{r}" for t, r in outs.items())
            print(f"{state} -> {outs_str}")
