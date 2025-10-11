import numpy as np


class BalanceEquationsSolver:
    def __init__(self, transitions: dict[tuple[int, int], dict[tuple[int, int], float]]):
        if not transitions:
            raise ValueError("transitions must be a non-empty dict")
        self.transitions = transitions
        self.states = list(transitions.keys())
        self.n = len(self.states)

    def solve(self) -> dict[tuple[int, int], float]:
        n = self.n
        A = np.zeros((n, n), dtype=float)
        b = np.zeros(n, dtype=float)
        idx = {s: k for k, s in enumerate(self.states)}
        for s in self.states:
            s_idx = idx[s]
            outs = self.transitions[s]
            outgoing_sum = sum(outs.values())
            A[s_idx, s_idx] -= outgoing_sum
            for t, rate in outs.items():
                t_idx = idx[t]
                A[t_idx, s_idx] += rate
        A[-1, :] = 1.0
        b[-1] = 1.0
        probs = np.linalg.solve(A, b)
        return {self.states[i]: float(probs[i]) for i in range(n)}
