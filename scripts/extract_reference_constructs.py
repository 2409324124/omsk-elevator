"""Extract reference-only construct summaries without emitting item text."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_DIR = ROOT / "data" / "reference"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=DEFAULT_REFERENCE_DIR,
        help="Reference data directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for a JSON summary. Defaults to stdout.",
    )
    args = parser.parse_args()

    summary = build_summary(args.reference_dir)
    output = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)
    assert_no_item_text(output, args.reference_dir)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


def build_summary(reference_dir: Path) -> dict[str, Any]:
    return {
        "usage": "reference_only_not_game_text",
        "do_not_copy_items_into_scenes": True,
        "do_not_report_clinical_or_real_world_political_labels": True,
        "sources": {
            "ipip_neo_120": summarize_ipip(reference_dir / "ipip_neo_120"),
            "8values": summarize_8values(reference_dir / "8values"),
        },
    }


def summarize_ipip(source_dir: Path) -> dict[str, Any]:
    questions_payload = read_json(source_dir / "questions_raw.json")
    mapping_payload = read_json(source_dir / "construct_mapping_draft.json")
    questions = questions_payload.get("questions", [])
    constructs = mapping_payload.get("constructs", [])

    return {
        "source": mapping_payload.get("source", "IPIP-NEO-120"),
        "usage": mapping_payload.get("usage", "reference_only_not_game_text"),
        "raw_question_count": len(questions),
        "raw_item_text_emitted": False,
        "available_raw_fields_excluding_text": sorted(
            {
                key
                for question in questions
                if isinstance(question, dict)
                for key in question
                if key != "text"
            }
        ),
        "mapped_construct_count": len(constructs),
        "mapped_game_constructs": sorted(
            {
                construct["game_construct"]
                for construct in constructs
                if "game_construct" in construct
            }
        ),
        "source_domains": sorted(
            {
                construct["source_domain"]
                for construct in constructs
                if "source_domain" in construct
            }
        ),
    }


def summarize_8values(source_dir: Path) -> dict[str, Any]:
    questions = parse_8values_questions(source_dir / "questions_raw.js")
    mapping_payload = read_json(source_dir / "construct_mapping_draft.json")
    axes = mapping_payload.get("source_axes", {})

    return {
        "source": mapping_payload.get("source", "8values"),
        "usage": mapping_payload.get("usage", "reference_only_not_game_text"),
        "license": mapping_payload.get("license", "MIT"),
        "raw_question_count": len(questions),
        "raw_item_text_emitted": False,
        "axis_effect_summary": summarize_axis_effects(questions, axes),
        "mapped_construct_count": len(mapping_payload.get("game_constructs", [])),
        "mapped_game_constructs": sorted(
            {
                construct["game_construct"]
                for construct in mapping_payload.get("game_constructs", [])
                if "game_construct" in construct
            }
        ),
    }


def parse_8values_questions(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    body = re.sub(r"^\s*questions\s*=\s*", "", raw, count=1)
    body = re.sub(r";\s*$", "", body.strip(), count=1)
    parsed = json.loads(body)
    if not isinstance(parsed, list):
        raise ValueError(f"{path}: expected questions array")
    return parsed


def summarize_axis_effects(
    questions: list[dict[str, Any]],
    axes: dict[str, str],
) -> dict[str, dict[str, float | int | str]]:
    summary: dict[str, dict[str, float | int | str]] = {}
    for axis, description in axes.items():
        values = [
            float(question.get("effect", {}).get(axis, 0.0))
            for question in questions
            if isinstance(question, dict)
        ]
        nonzero = [value for value in values if value != 0.0]
        summary[axis] = {
            "description": description,
            "nonzero_item_count": len(nonzero),
            "positive_weight_sum": sum(value for value in values if value > 0.0),
            "negative_weight_sum": sum(value for value in values if value < 0.0),
            "max_abs_weight": max((abs(value) for value in values), default=0.0),
        }
    return summary


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def assert_no_item_text(output: str, reference_dir: Path) -> None:
    leaked = []
    ipip_questions = read_json(reference_dir / "ipip_neo_120" / "questions_raw.json").get(
        "questions",
        [],
    )
    leaked.extend(
        question.get("text", "")
        for question in ipip_questions
        if isinstance(question, dict) and question.get("text")
    )
    leaked.extend(
        question.get("question", "")
        for question in parse_8values_questions(reference_dir / "8values" / "questions_raw.js")
        if isinstance(question, dict) and question.get("question")
    )

    for item_text in leaked:
        if item_text and item_text in output:
            raise ValueError("Reference extraction attempted to emit raw item text.")


if __name__ == "__main__":
    raise SystemExit(main())
