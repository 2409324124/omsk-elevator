"""Player state for the adaptive visual novel prototype."""

from __future__ import annotations

from dataclasses import dataclass, field


THETA_KEYS: tuple[str, ...] = (
    "truth_seek",
    "risk_tolerance",
    "authority_compliance",
    "local_empathy",
    "self_preservation",
    "control_strategy",
    "group_safety",
)

DEFAULT_REGRESSION_RATE = 0.85


def default_theta() -> dict[str, float]:
    return {key: 0.0 for key in THETA_KEYS}


@dataclass
class PlayerState:
    theta: dict[str, float] = field(default_factory=default_theta)
    surveillance_heat: float = 0.0
    evidence_count: float = 0.0
    relationships: dict[str, float] = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)
    choice_index: int = 0
    visited_scenes: list[str] = field(default_factory=list)
    regression_rate: float = DEFAULT_REGRESSION_RATE

    def ensure_theta_keys(self) -> None:
        for key in THETA_KEYS:
            self.theta.setdefault(key, 0.0)
