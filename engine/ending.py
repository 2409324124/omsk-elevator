"""Ending basin scoring for the adaptive visual novel prototype."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from engine.schema import Ending
from engine.state import PlayerState


ENDING_BASINS: tuple[str, ...] = (
    "safe_exit",
    "evidence_escape",
    "missing_tourist",
    "collaborator",
    "sacrifice_stay",
    "underground_stranded",
)

HARD_MISSING_TOURIST_HEAT = 7.0

FEATURE_KEYS: tuple[str, ...] = (
    "truth_seek",
    "group_safety",
    "local_empathy",
    "authority_compliance",
    "self_preservation",
    "risk_tolerance",
    "control_strategy",
    "surveillance_heat",
    "evidence_count",
    "reporter_trust",
    "guide_trust",
    "major_suspicion",
)

ENDING_WEIGHTS: dict[str, tuple[float, ...]] = {
    "safe_exit": (
        -0.4,
        0.2,
        0.0,
        0.8,
        1.0,
        -0.3,
        0.2,
        -0.6,
        -0.5,
        -0.2,
        0.3,
        -0.4,
    ),
    "evidence_escape": (
        1.2,
        1.0,
        0.1,
        -0.2,
        0.0,
        0.4,
        0.3,
        -0.8,
        1.0,
        0.3,
        -0.1,
        -0.3,
    ),
    "missing_tourist": (
        0.8,
        -0.2,
        0.0,
        -0.5,
        -0.2,
        0.3,
        0.0,
        1.5,
        0.1,
        0.6,
        -0.2,
        0.8,
    ),
    "collaborator": (
        -0.3,
        0.0,
        -0.6,
        0.7,
        1.1,
        -0.1,
        1.0,
        -0.2,
        -0.4,
        -0.1,
        0.4,
        -0.2,
    ),
    "sacrifice_stay": (
        0.5,
        1.0,
        1.2,
        -0.2,
        -1.0,
        0.3,
        -0.1,
        0.2,
        0.2,
        0.1,
        0.4,
        0.2,
    ),
    "underground_stranded": (
        0.4,
        -0.8,
        0.7,
        -0.4,
        -0.3,
        0.8,
        0.2,
        0.6,
        0.8,
        0.1,
        0.0,
        0.5,
    ),
}

ENDING_BIASES: dict[str, float] = {
    "safe_exit": 0.2,
    "evidence_escape": 0.0,
    "missing_tourist": -0.4,
    "collaborator": -0.1,
    "sacrifice_stay": -0.2,
    "underground_stranded": -0.3,
}

ENDING_FLAG_BONUSES: dict[str, dict[str, float]] = {
    "translated_hard_slogan": {
        "evidence_escape": 0.3,
        "missing_tourist": 0.2,
    },
    "unauthorized_translation_to_reporter": {
        "evidence_escape": 0.5,
        "missing_tourist": 0.9,
    },
    "asked_about_underground": {
        "evidence_escape": 0.4,
        "missing_tourist": 0.6,
        "underground_stranded": 0.4,
    },
    "took_translation_fragment": {
        "evidence_escape": 0.8,
        "missing_tourist": 0.4,
    },
    "memorized_translation_fragment": {
        "evidence_escape": 0.4,
        "safe_exit": 0.2,
    },
    "noted_b1_button": {
        "evidence_escape": 0.3,
        "underground_stranded": 0.3,
    },
    "copied_behavior_log": {
        "evidence_escape": 1.0,
        "missing_tourist": 0.5,
        "underground_stranded": 0.4,
    },
    "softened_official_translation": {
        "safe_exit": 0.5,
        "collaborator": 0.3,
    },
    "framed_b1_as_fault": {
        "safe_exit": 0.4,
        "collaborator": 0.8,
    },
    "left_behavior_log": {
        "safe_exit": 0.5,
    },
    "distracted_major_for_reporter": {
        "evidence_escape": 0.3,
        "missing_tourist": 0.7,
    },
}


def load_endings(path: str | Path = "data/scenes/endings.json") -> list[Ending]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("endings.json must contain a list of ending objects")
    endings = [Ending.from_dict(item) for item in payload]
    _validate_endings(endings)
    return endings


def compute_ending_scores(state: PlayerState) -> dict[str, float]:
    features = _feature_vector(state)
    scores: dict[str, float] = {}
    for basin in ENDING_BASINS:
        weights = np.array(ENDING_WEIGHTS[basin], dtype=float)
        scores[basin] = float(weights @ features + ENDING_BIASES.get(basin, 0.0))
    _apply_flag_bonuses(scores, state.flags)
    return scores


def choose_ending(
    state: PlayerState,
    endings: list[Ending] | None = None,
) -> Ending:
    endings_by_basin = _ending_index(endings if endings is not None else load_endings())
    basin = choose_ending_basin(state)
    try:
        return endings_by_basin[basin]
    except KeyError as exc:
        raise ValueError(f"Missing ending data for basin '{basin}'") from exc


def choose_ending_basin(state: PlayerState) -> str:
    if state.surveillance_heat >= HARD_MISSING_TOURIST_HEAT:
        return "missing_tourist"
    scores = compute_ending_scores(state)
    return max(ENDING_BASINS, key=lambda basin: scores[basin])


def ending_probabilities(state: PlayerState, temperature: float = 0.2) -> dict[str, float]:
    scores = np.array(
        [compute_ending_scores(state)[basin] for basin in ENDING_BASINS],
        dtype=float,
    )
    scaled = scores / max(temperature, 1e-9)
    scaled = scaled - np.max(scaled)
    values = np.exp(scaled)
    probabilities = values / np.sum(values)
    return dict(zip(ENDING_BASINS, probabilities.tolist(), strict=True))


def _feature_vector(state: PlayerState) -> np.ndarray:
    return np.array(
        [
            state.theta.get("truth_seek", 0.0),
            state.theta.get("group_safety", 0.0),
            state.theta.get("local_empathy", 0.0),
            state.theta.get("authority_compliance", 0.0),
            state.theta.get("self_preservation", 0.0),
            state.theta.get("risk_tolerance", 0.0),
            state.theta.get("control_strategy", 0.0),
            state.surveillance_heat,
            state.evidence_count,
            state.relationships.get("reporter_trust", 0.0),
            state.relationships.get("guide_trust", 0.0),
            state.relationships.get("major_suspicion", 0.0),
        ],
        dtype=float,
    )


def _ending_index(endings: list[Ending]) -> dict[str, Ending]:
    index: dict[str, Ending] = {}
    for ending in endings:
        basin = ending.basin or ending.id
        index[basin] = ending
    return index


def _apply_flag_bonuses(scores: dict[str, float], flags: set[str]) -> None:
    for flag in flags:
        for basin, bonus in ENDING_FLAG_BONUSES.get(flag, {}).items():
            scores[basin] = scores.get(basin, 0.0) + bonus


def _validate_endings(endings: list[Ending]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for ending in endings:
        basin = ending.basin or ending.id
        if basin in seen:
            duplicates.add(basin)
        seen.add(basin)

    missing = set(ENDING_BASINS) - seen
    extra = seen - set(ENDING_BASINS)
    if duplicates:
        raise ValueError(f"Duplicate ending basin(s): {', '.join(sorted(duplicates))}")
    if missing:
        raise ValueError(f"Missing ending basin(s): {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"Unknown ending basin(s): {', '.join(sorted(extra))}")
