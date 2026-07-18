"""Existing inventory behavior used only as Brownfield evidence in this fixture."""


def available(on_hand: int, reserved: int) -> int:
    return max(on_hand - reserved, 0)
