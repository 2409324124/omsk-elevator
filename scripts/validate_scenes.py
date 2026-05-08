"""Basic validator for scene JSON files under data/scenes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_EFFECTS = {
    "truth_seek",
    "risk_tolerance",
    "authority_compliance",
    "local_empathy",
    "self_preservation",
    "control_strategy",
    "group_safety",
}

VALID_FORCE_NEXT_CONDITIONS = {
    "surveillance_heat_gte",
    "surveillance_heat_lte",
    "evidence_count_gte",
    "evidence_count_lte",
    "choice_index_gte",
    "choice_index_lte",
    "flag_present",
    "flag_absent",
    "scene",
}


def load_scene_documents(scene_dir: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in sorted(scene_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            for item in data:
                item["_source_file"] = str(path)
                documents.append(item)
        elif isinstance(data, dict):
            data["_source_file"] = str(path)
            documents.append(data)
        else:
            raise ValueError(f"{path}: top-level JSON must be an object or list")
    return documents


def validate_scenes(scenes: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    scene_ids: set[str] = set()
    all_scene_ids: set[str] = set()
    choice_ids: set[str] = set()

    for scene in scenes:
        scene_id = scene.get("id")
        source = scene.get("_source_file", "<memory>")
        if not isinstance(scene_id, str) or not scene_id:
            errors.append(f"{source}: scene id is required")
            continue
        if scene_id in scene_ids:
            errors.append(f"{source}: duplicate scene id '{scene_id}'")
        scene_ids.add(scene_id)
        all_scene_ids.add(scene_id)

    for scene in scenes:
        scene_id = scene.get("id", "<missing scene id>")
        source = scene.get("_source_file", "<memory>")
        choices = scene.get("choices", [])
        if not isinstance(choices, list):
            errors.append(f"{source}:{scene_id}: choices must be a list")
            continue

        for choice in choices:
            choice_id = choice.get("id")
            if not isinstance(choice_id, str) or not choice_id:
                errors.append(f"{source}:{scene_id}: choice id is required")
                continue
            if choice_id in choice_ids:
                errors.append(f"{source}:{scene_id}: duplicate choice id '{choice_id}'")
            choice_ids.add(choice_id)

            effects = choice.get("effects", {})
            if not isinstance(effects, dict):
                errors.append(f"{source}:{scene_id}:{choice_id}: effects must be an object")
            else:
                for key, value in effects.items():
                    if key not in VALID_EFFECTS:
                        errors.append(
                            f"{source}:{scene_id}:{choice_id}: unknown effect '{key}'"
                        )
                    if not isinstance(value, int | float):
                        errors.append(
                            f"{source}:{scene_id}:{choice_id}: effect '{key}' must be numeric"
                        )

            force_next_if = choice.get("force_next_if")
            if force_next_if is not None:
                validate_force_next_if(
                    force_next_if,
                    all_scene_ids,
                    errors,
                    source,
                    scene_id,
                    choice_id,
                )

    return errors


def validate_force_next_if(
    force_next_if: Any,
    all_scene_ids: set[str],
    errors: list[str],
    source: str,
    scene_id: str,
    choice_id: str,
) -> None:
    if not isinstance(force_next_if, dict):
        errors.append(f"{source}:{scene_id}:{choice_id}: force_next_if must be an object")
        return

    for key, value in force_next_if.items():
        if key not in VALID_FORCE_NEXT_CONDITIONS:
            errors.append(
                f"{source}:{scene_id}:{choice_id}: unknown force_next_if key '{key}'"
            )
        if key == "scene" and value not in all_scene_ids:
            errors.append(
                f"{source}:{scene_id}:{choice_id}: force_next_if scene '{value}' not found"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scene_dir",
        nargs="?",
        default="data/scenes",
        help="Directory containing scene JSON files.",
    )
    args = parser.parse_args()

    scene_dir = Path(args.scene_dir)
    scenes = load_scene_documents(scene_dir)
    errors = validate_scenes(scenes)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: validated {len(scenes)} scene(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
