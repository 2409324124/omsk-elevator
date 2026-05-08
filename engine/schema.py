"""Dataclass schema for scene JSON files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Preconditions:
    required_flags: list[str] = field(default_factory=list)
    required_flags_any: list[str] = field(default_factory=list)
    forbidden_flags: list[str] = field(default_factory=list)
    min_choice_index: int | None = None
    max_choice_index: int | None = None
    min_surveillance_heat: float | None = None
    max_surveillance_heat: float | None = None
    min_evidence_count: float | None = None
    max_evidence_count: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Preconditions":
        if not data:
            return cls()

        known = {
            "required_flags",
            "required_flags_any",
            "forbidden_flags",
            "min_choice_index",
            "max_choice_index",
            "min_surveillance_heat",
            "max_surveillance_heat",
            "min_evidence_count",
            "max_evidence_count",
        }
        values = {key: data[key] for key in known if key in data}
        values["extra"] = {key: value for key, value in data.items() if key not in known}
        return cls(**values)


@dataclass
class Choice:
    id: str
    text: str
    effects: dict[str, float] = field(default_factory=dict)
    heat_delta: float = 0.0
    evidence_delta: float = 0.0
    relationship_effects: dict[str, float] = field(default_factory=dict)
    flags_add: list[str] = field(default_factory=list)
    basin_pressure: dict[str, float] = field(default_factory=dict)
    force_next_if: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Choice":
        known = {
            "id",
            "text",
            "effects",
            "heat_delta",
            "evidence_delta",
            "relationship_effects",
            "flags_add",
            "basin_pressure",
            "force_next_if",
        }
        values = {key: data[key] for key in known if key in data}
        values["extra"] = {key: value for key, value in data.items() if key not in known}
        return cls(**values)


@dataclass
class Scene:
    id: str
    act: int
    location: str
    phase: str
    title: str
    visible_text: str
    hidden_constructs: list[str] = field(default_factory=list)
    preconditions: Preconditions = field(default_factory=Preconditions)
    choices: list[Choice] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scene":
        known = {
            "id",
            "act",
            "location",
            "phase",
            "title",
            "visible_text",
            "hidden_constructs",
            "preconditions",
            "choices",
            "tags",
        }
        values = {key: data[key] for key in known if key in data}
        values["preconditions"] = Preconditions.from_dict(data.get("preconditions"))
        values["choices"] = [Choice.from_dict(choice) for choice in data.get("choices", [])]
        values["extra"] = {key: value for key, value in data.items() if key not in known}
        return cls(**values)


@dataclass
class Ending:
    id: str
    title: str
    text: str = ""
    basin: str | None = None
    preconditions: Preconditions = field(default_factory=Preconditions)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ending":
        known = {"id", "title", "text", "basin", "preconditions"}
        values = {key: data[key] for key in known if key in data}
        values["preconditions"] = Preconditions.from_dict(data.get("preconditions"))
        values["extra"] = {key: value for key, value in data.items() if key not in known}
        return cls(**values)
