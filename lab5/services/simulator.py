from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet


class PetriNetSimulator:
    @staticmethod
    def simulate_one_path(
            petri_net: PetriNet,
            max_steps: int = 20
    ) -> tuple[list[Marking], bool]:
        path = [petri_net.initial_marking]
        current = petri_net.initial_marking
        seen_markings = {current}
        is_cyclic = False
        for step in range(max_steps):
            enabled = sorted(petri_net.enabled_transitions(current))
            if not enabled:
                break
            transition = enabled[0]
            next_mark = petri_net.fire(current, transition)
            if next_mark in seen_markings:
                path.append(next_mark)
                is_cyclic = True
                break
            path.append(next_mark)
            seen_markings.add(next_mark)
            current = next_mark
        return path, is_cyclic
