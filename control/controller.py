"""
Rule-based controller: maps vision feedback to simulated control signals.
No RL; explicit rules: object left → rotate left, centered → forward, lost → search.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ControlSignal:
    """Simulated control output for visualization / future robot interface."""

    linear: float   # forward/back, e.g. [-1, 1]
    angular: float  # rotate left/right, e.g. [-1, 1]
    mode: str       # "forward" | "rotate_left" | "rotate_right" | "search" | "stop"


class Controller:
    """
    Rule-based controller from tracker state (cx_norm, found).
    Object left  → rotate left
    Object right → rotate right
    Object centered → move forward
    Object lost → search mode (slow rotation)
    """

    def __init__(
        self,
        center_margin: float = 0.15,
        forward_speed: float = 0.5,
        rotate_speed: float = 0.4,
        search_speed: float = 0.2,
    ) -> None:
        self.center_margin = center_margin  # band around center (0.5) considered "centered"
        self.forward_speed = forward_speed
        self.rotate_speed = rotate_speed
        self.search_speed = search_speed

    def update(self, tracker_state: dict[str, Any]) -> ControlSignal:
        """
        Compute control from tracker_state: found, cx_norm, cy_norm.
        """
        found = tracker_state.get("found", False)
        cx_norm = tracker_state.get("cx_norm", 0.5)
        center = 0.5
        margin = self.center_margin

        if not found:
            return ControlSignal(
                linear=0.0,
                angular=self.search_speed,
                mode="search",
            )
        if cx_norm < center - margin:
            return ControlSignal(
                linear=0.0,
                angular=self.rotate_speed,
                mode="rotate_left",
            )
        if cx_norm > center + margin:
            return ControlSignal(
                linear=0.0,
                angular=-self.rotate_speed,
                mode="rotate_right",
            )
        return ControlSignal(
            linear=self.forward_speed,
            angular=0.0,
            mode="forward",
        )
