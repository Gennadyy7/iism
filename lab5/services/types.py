from typing import Literal, NewType

Token = int | Literal['ω']
PlaceName = NewType('PlaceName', str)
TransitionName = NewType('TransitionName', str)

MarkingTuple = tuple[Token, ...]
MarkingDict = dict[PlaceName, Token]

Arcs = dict[TransitionName, list[PlaceName]]
