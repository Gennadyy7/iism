from collections import deque

from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet
from lab5.services.types import TransitionName


class ReachabilityGraphBuilder:
    MAX_MARKINGS = 10

    def __init__(self, petri_net: PetriNet):
        self.net = petri_net
        self.graph: dict[Marking, list[tuple[TransitionName, Marking]]] = {}
        self.omega_nodes: set[Marking] = set()

    def build(self) -> dict[Marking, list[tuple[TransitionName, Marking]]]:
        initial = self.net.initial_marking
        queue: deque[Marking] = deque([initial])
        visited: set[Marking] = {initial}
        self.graph = {initial: []}

        while queue and len(self.graph) < self.MAX_MARKINGS:
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

        if len(self.graph) >= self.MAX_MARKINGS:
            self._mark_unbounded_due_to_limit()

        return self.graph

    def _mark_unbounded_due_to_limit(self) -> None:
        initial_vals = self.net.initial_marking.values
        last_mark = next(reversed(self.graph))
        new_vals = []
        for init_v, last_v in zip(initial_vals, last_mark.values):
            if isinstance(last_v, int) and isinstance(init_v, int) and last_v > init_v:
                new_vals.append("ω")
            else:
                new_vals.append(last_v)
        unbounded_mark = Marking(tuple(new_vals), last_mark.place_order)
        self.graph[unbounded_mark] = []
        for src, edge_list in self.graph.items():
            self.graph[src] = [
                (t, unbounded_mark if m == last_mark else m)
                for t, m in edge_list
            ]

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
