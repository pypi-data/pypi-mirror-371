"""The enumeration of the different supported positions."""

from enum import StrEnum


class Position(StrEnum):
    """An enumeration over the different positions."""

    GOALKEEPER = "G"
    CENTRE_DEFENDER_LEFT = "CD-L"
    CENTRE_DEFENDER_RIGHT = "CD-R"
    LEFT_BACK = "LB"


_POSITIONS = {str(x): x for x in Position}


def position_from_str(position_str: str) -> Position:
    """Find a position from a string."""
    position = _POSITIONS.get(position_str)
    if position is None:
        raise ValueError(f"Unrecognised position: {position_str}")
    return position
