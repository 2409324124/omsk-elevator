"""State update rules for player choices."""

from __future__ import annotations

import numpy as np

from engine.schema import Choice
from engine.state import PlayerState


def apply_choice(state: PlayerState, choice: Choice) -> PlayerState:
    """Apply deterministic numeric effects from a choice to player state."""
    state.ensure_theta_keys()

    for key, delta in choice.effects.items():
        state.theta[key] = state.theta.get(key, 0.0) + float(delta)

    theta_keys = list(state.theta.keys())
    theta_values = np.array([state.theta[key] for key in theta_keys], dtype=float)
    theta_values = theta_values * float(state.regression_rate)
    state.theta.update(dict(zip(theta_keys, theta_values.tolist(), strict=True)))

    state.surveillance_heat += float(choice.heat_delta)
    state.evidence_count += float(choice.evidence_delta)

    for key, delta in choice.relationship_effects.items():
        state.relationships[key] = state.relationships.get(key, 0.0) + float(delta)

    state.flags.update(choice.flags_add)
    state.choice_index += 1
    return state
