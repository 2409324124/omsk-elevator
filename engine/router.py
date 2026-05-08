"""Lightweight NumPy scene router for the CLI prototype."""

from __future__ import annotations

import numpy as np

from engine.schema import Preconditions, Scene
from engine.state import PlayerState


PHASES: dict[str, dict[str, float]] = {
    "surface_fixed": {"alpha": 0.0, "beta": 1.0, "gamma": 0.4, "delta": 0.0, "temperature": 0.0},
    "early_adaptive": {"alpha": 0.4, "beta": 1.0, "gamma": 0.6, "delta": 0.2, "temperature": 1.0},
    "underground_router": {"alpha": 0.8, "beta": 1.0, "gamma": 0.7, "delta": 0.4, "temperature": 0.7},
    "ending_converge": {"alpha": 0.4, "beta": 0.8, "gamma": 0.5, "delta": 1.0, "temperature": 0.2},
}


def get_valid_scenes(state: PlayerState, scenes: list[Scene]) -> list[Scene]:
    return [
        scene
        for scene in scenes
        if scene.id not in state.visited_scenes and _preconditions_met(scene.preconditions, state)
    ]


def score_scene(scene: Scene, state: PlayerState, phase: str) -> float:
    params = PHASES.get(phase, PHASES["early_adaptive"])
    theta_values = np.array(
        [state.theta.get(key, 0.0) for key in scene.hidden_constructs],
        dtype=float,
    )

    info_gain = float(np.mean(1.0 / (1.0 + np.abs(theta_values)))) if theta_values.size else 0.0
    narrative_fit = 1.0 if scene.phase == phase else 0.2
    unresolved_thread = _unresolved_thread_score(scene, state)
    basin_pressure = _choice_basin_pressure(scene)
    repetition_penalty = 2.0 if scene.id in state.visited_scenes else 0.0

    return (
        params["alpha"] * info_gain
        + params["beta"] * narrative_fit
        + params["gamma"] * unresolved_thread
        + params["delta"] * basin_pressure
        - repetition_penalty
    )


def choose_next_scene(
    valid_scenes: list[Scene],
    state: PlayerState,
    phase: str,
    rng: np.random.Generator | None = None,
) -> Scene | None:
    if not valid_scenes:
        return None

    scores = np.array([score_scene(scene, state, phase) for scene in valid_scenes], dtype=float)
    temperature = PHASES.get(phase, PHASES["early_adaptive"])["temperature"]
    if temperature <= 0.0:
        return valid_scenes[int(np.argmax(scores))]

    generator = rng if rng is not None else np.random.default_rng()
    probabilities = _softmax(scores, temperature)
    index = int(generator.choice(len(valid_scenes), p=probabilities))
    return valid_scenes[index]


def _preconditions_met(preconditions: Preconditions, state: PlayerState) -> bool:
    if not set(preconditions.required_flags).issubset(state.flags):
        return False
    if preconditions.required_flags_any and not state.flags.intersection(preconditions.required_flags_any):
        return False
    if state.flags.intersection(preconditions.forbidden_flags):
        return False
    if preconditions.min_choice_index is not None and state.choice_index < preconditions.min_choice_index:
        return False
    if preconditions.max_choice_index is not None and state.choice_index > preconditions.max_choice_index:
        return False
    if (
        preconditions.min_surveillance_heat is not None
        and state.surveillance_heat < preconditions.min_surveillance_heat
    ):
        return False
    if (
        preconditions.max_surveillance_heat is not None
        and state.surveillance_heat > preconditions.max_surveillance_heat
    ):
        return False
    if preconditions.min_evidence_count is not None and state.evidence_count < preconditions.min_evidence_count:
        return False
    if preconditions.max_evidence_count is not None and state.evidence_count > preconditions.max_evidence_count:
        return False
    return True


def _unresolved_thread_score(scene: Scene, state: PlayerState) -> float:
    score = 0.0
    if "underground_hint" in scene.tags and (
        "saw_b1_button" in state.flags or "noted_b1_button" in state.flags
    ):
        score += 1.0
    if "monitoring" in scene.tags and state.surveillance_heat >= 2.0:
        score += 1.0
    if "evidence" in scene.tags and state.evidence_count > 0.0:
        score += 0.5
    return score


def _choice_basin_pressure(scene: Scene) -> float:
    values = [
        abs(float(value))
        for choice in scene.choices
        for value in choice.basin_pressure.values()
    ]
    return float(np.mean(values)) if values else 0.0


def _softmax(scores: np.ndarray, temperature: float) -> np.ndarray:
    scaled = scores / temperature
    shifted = scaled - np.max(scaled)
    exp_scores = np.exp(shifted)
    return exp_scores / np.sum(exp_scores)
