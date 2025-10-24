from lab5.services.graph_builder import ReachabilityGraphBuilder
from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet


class PetriNetAnalyzer:
    def __init__(self, petri_net: PetriNet):
        self.net = petri_net
        builder = ReachabilityGraphBuilder(petri_net)
        self.graph = builder.build()
        self.all_markings = list(self.graph.keys())

    def is_bounded(self) -> bool:
        for m in self.all_markings:
            if "ω" in m.values:
                return False
        return True

    def is_safe(self) -> bool:
        for m in self.all_markings:
            if any(v != "ω" and v > 1 for v in m.values):
                return False
        return True

    def is_conservative(self) -> bool:
        if not self.is_bounded():
            return False
        sums = set()
        for m in self.all_markings:
            s = sum(v for v in m.values if v != "ω")
            sums.add(s)
        return len(sums) == 1

    def is_liveness(self) -> bool:
        fired: set[str] = set()
        for _, edges in self.graph.items():
            for t, _ in edges:
                fired.add(t)
        return len(fired) == len(self.net.transitions)

    def has_parallel_firing(self) -> bool:
        for m in self.all_markings:
            enabled = self.net.enabled_transitions(m)
            if len(enabled) < 2:
                continue
            trans_list = list(enabled)
            for i in range(len(trans_list)):
                for j in range(i + 1, len(trans_list)):
                    t1, t2 = trans_list[i], trans_list[j]
                    out1 = set(self.net.output_arcs.get(t1, []))
                    out2 = set(self.net.output_arcs.get(t2, []))
                    in1 = set(self.net.input_arcs.get(t1, []))
                    in2 = set(self.net.input_arcs.get(t2, []))
                    if in1.isdisjoint(in2) and out1.isdisjoint(out2):
                        return True
        return False

    def classify(self) -> dict[str, bool]:
        places = set(self.net.places)
        transitions = set(self.net.transitions)

        is_automaton = all(
            len(self.net.input_arcs.get(t, [])) <= 1 and
            len(self.net.output_arcs.get(t, [])) <= 1
            for t in transitions
        )

        is_marked_graph = all(
            sum(1 for t in transitions if p in self.net.input_arcs.get(t, [])) == 1 and
            sum(1 for t in transitions if p in self.net.output_arcs.get(t, [])) == 1
            for p in places
        )

        is_free_choice = True
        for t1 in transitions:
            for t2 in transitions:
                if t1 == t2:
                    continue
                common_inputs = set(self.net.input_arcs.get(t1, [])) & set(self.net.input_arcs.get(t2, []))
                if common_inputs:
                    if len(self.net.input_arcs[t1]) > 1 or len(self.net.input_arcs[t2]) > 1:
                        is_free_choice = False
                        break
            if not is_free_choice:
                break

        return {
            "automaton": is_automaton,
            "marked_graph": is_marked_graph,
            "free_choice": is_free_choice,
        }

    def is_reachable(self, target: Marking) -> bool:
        return target in self.all_markings
