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

    def get_balance_equations(self) -> list[str]:
        equations = []
        for s in self.states:
            outs = self.transitions[s]
            incoming = []
            for t, t_outs in self.transitions.items():
                if s in t_outs:
                    rate = t_outs[s]
                    incoming.append(f"{rate}·P{t}")
            outgoing_sum = sum(outs.values())
            if incoming:
                left = " + ".join(incoming)
            else:
                left = "0"
            right = f"{outgoing_sum}·P{s}"
            equations.append(f"{left} = {right}")
        norm = " + ".join(f"P{s}" for s in self.states) + " = 1"
        equations.append(norm)
        return equations
