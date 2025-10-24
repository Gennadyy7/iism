from dataclasses import dataclass

from lab5.services.marking import Marking
from lab5.services.types import Arcs, PlaceName, TransitionName


@dataclass(frozen=True)
class PetriNet:
    places: tuple[PlaceName, ...]
    transitions: tuple[TransitionName, ...]
    input_arcs: Arcs
    output_arcs: Arcs
    initial_marking: Marking

    def __post_init__(self) -> None:
        all_places = set(self.places)
        for arcs in (self.input_arcs, self.output_arcs):
            for t, plist in arcs.items():
                if t not in self.transitions:
                    raise ValueError(f"Transition {t} not declared")
                for p in plist:
                    if p not in all_places:
                        raise ValueError(f"Place {p} not declared")

    def enabled_transitions(self, marking: Marking) -> set[TransitionName]:
        enabled = set()
        mark_dict = marking.to_dict()
        for t in self.transitions:
            inputs = self.input_arcs.get(t, [])
            if all(mark_dict.get(p, 0) >= 1 for p in inputs):
                enabled.add(t)
        return enabled

    def fire(self, marking: Marking, transition: TransitionName) -> Marking:
        if transition not in self.transitions:
            raise ValueError(f"Unknown transition: {transition}")
        if transition not in self.enabled_transitions(marking):
            raise ValueError(f"Transition {transition} is not enabled in {marking}")

        mark_dict = marking.to_dict()
        for p in self.input_arcs.get(transition, []):
            mark_dict[p] = mark_dict[p] - 1
        for p in self.output_arcs.get(transition, []):
            mark_dict[p] = mark_dict.get(p, 0) + 1

        return Marking.from_dict(mark_dict, self.places)
