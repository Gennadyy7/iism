class PerformanceMetrics:
    def __init__(
        self,
        probs: dict[tuple[int, int], float],
        lambda1: float,
        lambda2: float,
        mu1: float,
        mu2: float,
    ):
        self.P = probs
        self.l1 = lambda1
        self.l2 = lambda2
        self.m1 = mu1
        self.m2 = mu2

        self.K = max(i + j for (i, j) in self.P.keys())

    def blocking_probabilities(self) -> dict[str, float]:
        P = self.P
        P_block_I = sum(p for (i, j), p in P.items() if (i + j == self.K and i > 0))
        P_block_II = sum(p for (i, j), p in P.items() if (i + j == self.K))
        return {"I": float(P_block_I), "II": float(P_block_II)}

    def entrance_intensities(self) -> dict[str, float]:
        blocks = self.blocking_probabilities()
        lam1_in = self.l1 * (1.0 - blocks['I'])
        lam2_in = self.l2 * (1.0 - blocks['II'])
        return {"lambda1_in": float(lam1_in), "lambda2_in": float(lam2_in)}

    def served_probabilities(self) -> dict[str, dict[str, float | None]]:
        P = self.P
        prob_server_I = sum(p for (i, j), p in P.items() if i > 0)
        prob_server_II = sum(p for (i, j), p in P.items() if i == 0 and j > 0)
        throughput_I = self.m1 * prob_server_I
        throughput_II = self.m2 * prob_server_II
        lam1_in = self.entrance_intensities()['lambda1_in']
        lam2_in = self.entrance_intensities()['lambda2_in']
        res = {
            'I': {
                'throughput': float(throughput_I),
                'of_arrivals': float(throughput_I / self.l1) if self.l1 > 0 else None,
                'of_entered': float(throughput_I / lam1_in) if lam1_in > 0 else None,
            },
            'II': {
                'throughput': float(throughput_II),
                'of_arrivals': float(throughput_II / self.l2) if self.l2 > 0 else None,
                'of_entered': float(throughput_II / lam2_in) if lam2_in > 0 else None,
            }
        }
        return res

    def average_counts(self) -> dict[str, float]:
        P = self.P
        L1 = sum(i * p for (i, j), p in P.items())
        L2 = sum(j * p for (i, j), p in P.items())
        return {'L1': float(L1), 'L2': float(L2)}

    def average_queue_lengths(self) -> dict[str, float]:
        """
        Если есть заявки I (i > 0) → прибор занят I → все заявки II находятся в очереди → их число = j.
        Если нет заявок I (i == 0) → прибор занят II → в очереди = j - 1.
        Для Q1 проще:
            Если i > 0, то одна заявка I на приборе, остальные (i - 1) — в очереди.
            Если i == 0 → max(0, -1) = 0.
        """
        P = self.P
        Q1 = sum(max(0, i - 1) * p for (i, j), p in P.items())
        Q2 = 0.0
        for (i, j), p in P.items():
            if i > 0:
                Q2 += j * p
            else:
                Q2 += max(0, j - 1) * p
        return {'Q1': float(Q1), 'Q2': float(Q2)}

    def average_times(self) -> dict[str, float | None]:
        entr = self.entrance_intensities()
        L = self.average_counts()
        Q = self.average_queue_lengths()
        lam1_in = entr['lambda1_in']
        lam2_in = entr['lambda2_in']
        W1 = float(L['L1'] / lam1_in) if lam1_in > 0 else None
        W2 = float(L['L2'] / lam2_in) if lam2_in > 0 else None
        Wq1 = float(Q['Q1'] / lam1_in) if lam1_in > 0 else None
        Wq2 = float(Q['Q2'] / lam2_in) if lam2_in > 0 else None
        lam_total_in = lam1_in + lam2_in
        W = (lam1_in * W1 + lam2_in * W2) / lam_total_in if lam_total_in > 0 else None
        Wq = (lam1_in * Wq1 + lam2_in * Wq2) / lam_total_in if lam_total_in > 0 else None
        return {
            'W1': W1,
            'W2': W2,
            'Wq1': Wq1,
            'Wq2': Wq2,
            'W': W,
            'Wq': Wq,
        }
