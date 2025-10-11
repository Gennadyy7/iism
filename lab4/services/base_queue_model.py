from dataclasses import dataclass


@dataclass(frozen=True)
class QueueState:
    i: int
    j: int

    def tuple(self) -> tuple:
        return self.i, self.j


class BaseQueueModel:
    def __init__(self, r: int):
        if r < 0:
            raise ValueError("R must be non-negative")
        self.R = r
        self.K = 1 + self.R

    def get_states(self) -> list[QueueState]:
        states: list[QueueState] = []
        for i in range(self.K + 1):
            for j in range(self.K + 1):
                if i + j <= self.K:
                    states.append(QueueState(i, j))
        return states
