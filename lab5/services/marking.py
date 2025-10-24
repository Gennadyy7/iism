from dataclasses import dataclass

from lab5.services.types import MarkingDict, MarkingTuple, PlaceName


@dataclass(frozen=True)
class Marking:
    values: MarkingTuple
    place_order: tuple[PlaceName, ...]

    @classmethod
    def from_dict(cls, d: MarkingDict, place_order: tuple[PlaceName, ...]) -> "Marking":
        values = tuple(d.get(p, 0) for p in place_order)
        return cls(values=values, place_order=place_order)

    def to_dict(self) -> MarkingDict:
        return {p: v for p, v in zip(self.place_order, self.values)}

    def __ge__(self, other: "Marking") -> bool:
        if self.place_order != other.place_order:
            raise ValueError("Incompatible place orders")
        for a, b in zip(self.values, other.values):
            if a == "ω":
                continue
            if b == "ω":
                return False
            if a < b:
                return False
        return True

    def __add__(self, other: "Marking") -> "Marking":
        raise NotImplementedError("Marking addition is not defined")

    def __hash__(self) -> int:
        return hash(self.values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Marking):
            return False
        return self.values == other.values and self.place_order == other.place_order
