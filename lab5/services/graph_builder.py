from collections import deque

from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet
from lab5.services.types import TransitionName


class ReachabilityGraphBuilder:
    def __init__(self, petri_net: PetriNet):
        self.net = petri_net
        self.graph: dict[Marking, list[tuple[TransitionName, Marking]]] = {}
        self.omega_nodes: set[Marking] = set()

    def build(self) -> dict[Marking, list[tuple[TransitionName, Marking]]]:
        initial = self.net.initial_marking
        queue: deque[Marking] = deque([initial])
        visited: set[Marking] = {initial}
        self.graph = {initial: []}

        while queue:
            current = queue.popleft()
            enabled = self.net.enabled_transitions(current)

            for t in enabled:
                try:
                    next_mark = self.net.fire(current, t)
                except ValueError:
                    continue

                next_mark = self._apply_omega_rules(current, next_mark)

                if next_mark not in self.graph:
                    self.graph[next_mark] = []
                    if next_mark not in visited:
                        visited.add(next_mark)
                        queue.append(next_mark)

                self.graph[current].append((t, next_mark))

        return self.graph

    def _apply_omega_rules(self, prev: Marking, candidate: Marking) -> Marking:
        if "ω" in candidate.values:
            return candidate

        for existing in self.graph:
            if prev <= existing <= candidate and existing != candidate:
                new_vals = []
                for a, b in zip(existing.values, candidate.values):
                    if isinstance(a, int) and isinstance(b, int):
                        if b > a:
                            new_vals.append("ω")
                        else:
                            new_vals.append(b)
                    else:
                        new_vals.append(b)
                return Marking(tuple(new_vals), candidate.place_order)

        return candidate
