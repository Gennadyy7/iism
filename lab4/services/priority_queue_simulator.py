import heapq
import random
from typing import NamedTuple, Any


class Event(NamedTuple):
    time: float
    event_type: str
    job_type: str | None = None


class PriorityQueueSimulator:
    def __init__(
        self,
        r: int,
        lambda1: float,
        lambda2: float,
        mu1: float,
        mu2: float,
        simulation_time: float,
        seed: int | None = None
    ):
        if r < 0:
            raise ValueError("R must be non-negative")
        if any(x <= 0 for x in [lambda1, lambda2, mu1, mu2]):
            raise ValueError("All rates must be > 0")
        if simulation_time <= 0:
            raise ValueError("Simulation time must be > 0")

        self.R = r
        self.K = 1 + r
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.mu1 = mu1
        self.mu2 = mu2
        self.T = simulation_time

        if seed is not None:
            random.seed(seed)

        self.i = 0
        self.j = 0
        self.server_busy = False
        self.server_job_type = None

        self.queue_I: list[float] = []
        self.queue_II: list[float] = []

        self.arrivals_I = 0
        self.arrivals_II = 0
        self.blocked_I = 0
        self.blocked_II = 0
        self.served_I = 0
        self.served_II = 0
        self.total_time = 0.0
        self.area_i = 0.0
        self.area_j = 0.0
        self.area_q1 = 0.0
        self.area_q2 = 0.0
        self.last_event_time = 0.0

        self.event_queue: list[Event] = []

    def _get_service_time(self, job_type: str) -> float:
        if job_type == 'I':
            return random.expovariate(self.mu1)
        else:
            return random.expovariate(self.mu2)

    def _get_arrival_time(self, stream: str) -> float:
        if stream == 'I':
            return random.expovariate(self.lambda1)
        else:
            return random.expovariate(self.lambda2)

    def _update_areas(self, current_time: float) -> None:
        dt = current_time - self.last_event_time
        self.area_i += self.i * dt
        self.area_j += self.j * dt

        q1 = max(0, self.i - 1) if self.i > 0 else 0
        if self.i > 0:
            q2 = self.j
        else:
            q2 = max(0, self.j - 1) if self.j > 0 else 0

        self.area_q1 += q1 * dt
        self.area_q2 += q2 * dt

        self.last_event_time = current_time

    def _start_service(self, current_time: float) -> None:
        if self.i > 0:
            self.server_job_type = 'I'
            self.server_busy = True
            service_time = self._get_service_time('I')
            heapq.heappush(self.event_queue, Event(current_time + service_time, 'departure', 'I'))
        elif self.j > 0:
            self.server_job_type = 'II'
            self.server_busy = True
            service_time = self._get_service_time('II')
            heapq.heappush(self.event_queue, Event(current_time + service_time, 'departure', 'II'))

    def _handle_arrival_I(self, current_time: float) -> None:
        self.arrivals_I += 1
        total = self.i + self.j

        if total < self.K:
            self.i += 1
            if not self.server_busy:
                self._start_service(current_time)
        elif total == self.K:
            if self.server_job_type == 'II':
                self.j -= 1
                self.server_busy = False
                self.server_job_type = None

                current_queue_len = len(self.queue_I) + len(self.queue_II)
                if current_queue_len < self.R:
                    self.queue_II.append(current_time)
                    self.j += 1

                self.i += 1
                self._start_service(current_time)
            else:
                self.blocked_I += 1
                return
        else:
            self.blocked_I += 1
            return

    def _handle_arrival_II(self, current_time: float) -> None:
        self.arrivals_II += 1
        if self.i + self.j < self.K:
            self.j += 1
            if not self.server_busy:
                self._start_service(current_time)
        else:
            self.blocked_II += 1

    def _handle_departure(self, current_time: float, job_type: str) -> None:
        if job_type == 'I':
            self.served_I += 1
            self.i -= 1
        else:
            self.served_II += 1
            self.j -= 1

        self.server_busy = False
        self.server_job_type = None

        if self.i > 0 or self.j > 0:
            self._start_service(current_time)

    def run(self) -> dict[str, Any]:
        first_I = self._get_arrival_time('I')
        first_II = self._get_arrival_time('II')
        heapq.heappush(self.event_queue, Event(first_I, 'arrival_I'))
        heapq.heappush(self.event_queue, Event(first_II, 'arrival_II'))

        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            if event.time > self.T:
                break

            self._update_areas(event.time)

            if event.event_type == 'arrival_I':
                self._handle_arrival_I(event.time)
            elif event.event_type == 'arrival_II':
                self._handle_arrival_II(event.time)
            elif event.event_type == 'departure':
                self._handle_departure(event.time, event.job_type)

        self._update_areas(self.T)

        lambda1_in = self.arrivals_I - self.blocked_I
        lambda2_in = self.arrivals_II - self.blocked_II

        P_block_I = self.blocked_I / self.arrivals_I if self.arrivals_I > 0 else 0.0
        P_block_II = self.blocked_II / self.arrivals_II if self.arrivals_II > 0 else 0.0

        L1 = self.area_i / self.T
        L2 = self.area_j / self.T
        Q1 = self.area_q1 / self.T
        Q2 = self.area_q2 / self.T

        W1 = L1 / (lambda1_in / self.T) if lambda1_in > 0 else None
        W2 = L2 / (lambda2_in / self.T) if lambda2_in > 0 else None
        Wq1 = Q1 / (lambda1_in / self.T) if lambda1_in > 0 else None
        Wq2 = Q2 / (lambda2_in / self.T) if lambda2_in > 0 else None

        lam_total_in = (lambda1_in + lambda2_in) / self.T
        W = (L1 + L2) / lam_total_in if lam_total_in > 0 else None
        Wq = (Q1 + Q2) / lam_total_in if lam_total_in > 0 else None

        return {
            'blocking': {'I': P_block_I, 'II': P_block_II},
            'entrance_intensities': {
                'lambda1_in': lambda1_in / self.T,
                'lambda2_in': lambda2_in / self.T,
            },
            'served': {
                'I': {'throughput': self.served_I / self.T},
                'II': {'throughput': self.served_II / self.T},
            },
            'average_counts': {'L1': L1, 'L2': L2},
            'queue_lengths': {'Q1': Q1, 'Q2': Q2},
            'times': {
                'W1': W1, 'W2': W2,
                'Wq1': Wq1, 'Wq2': Wq2,
                'W': W, 'Wq': Wq,
            },
            'simulation_time': self.T,
            'arrivals': {'I': self.arrivals_I, 'II': self.arrivals_II},
        }
