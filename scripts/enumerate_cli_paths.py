"""Enumerate CLI prototype choice paths and ending basins.

This is a diagnostic script for the small CLI demo. It does not change routing,
state update, or ending rules; it only replays them across many choice paths.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.ending import choose_ending, compute_ending_scores, load_endings
from engine.router import get_valid_scenes, score_scene
from engine.schema import Ending, Scene
from engine.state import PlayerState
from engine.update import apply_choice
from scripts.run_cli_demo import forced_next_scene_id, load_scenes, phase_for_choice_index


@dataclass
class PathStep:
    scene_id: str
    scene_title: str
    choice_index: int
    choice_id: str
    choice_text: str


@dataclass
class PathResult:
    ending_id: str
    ending_title: str
    steps: list[PathStep]
    state: PlayerState
    scores: dict[str, float]


def main() -> int:
    args = parse_args()
    scenes = load_scenes(args.scene_dir)
    endings = load_endings(args.endings)
    results = enumerate_paths(
        scenes=scenes,
        endings=endings,
        max_steps=args.max_steps,
        scene_mode=args.scene_mode,
    )
    print_report(results, sample_limit=args.samples)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enumerate choice paths for the current CLI demo.",
    )
    parser.add_argument("--scene-dir", type=Path, default=Path("data/scenes"))
    parser.add_argument("--endings", type=Path, default=Path("data/scenes/endings.json"))
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument(
        "--scene-mode",
        choices=("argmax", "all"),
        default="argmax",
        help="argmax mirrors a deterministic router; all also branches over every valid scene.",
    )
    parser.add_argument("--samples", type=int, default=3, help="sample paths to show per ending")
    return parser.parse_args()


def enumerate_paths(
    scenes: list[Scene],
    endings: list[Ending],
    max_steps: int,
    scene_mode: str,
) -> list[PathResult]:
    results: list[PathResult] = []

    def visit(state: PlayerState, forced_scene_id: str | None, steps: list[PathStep]) -> None:
        if state.choice_index >= max_steps:
            results.append(make_result(state, endings, steps))
            return

        candidates = next_scene_candidates(
            scenes=scenes,
            state=state,
            forced_scene_id=forced_scene_id,
            scene_mode=scene_mode,
        )
        if not candidates:
            results.append(make_result(state, endings, steps))
            return

        for scene in candidates:
            scene_state = copy.deepcopy(state)
            scene_state.visited_scenes.append(scene.id)
            for index, choice in enumerate(scene.choices, start=1):
                next_state = copy.deepcopy(scene_state)
                apply_choice(next_state, choice)
                next_steps = steps + [
                    PathStep(
                        scene_id=scene.id,
                        scene_title=scene.title,
                        choice_index=index,
                        choice_id=choice.id,
                        choice_text=choice.text,
                    )
                ]
                visit(next_state, forced_next_scene_id(choice, next_state), next_steps)

    visit(PlayerState(), None, [])
    return results


def next_scene_candidates(
    scenes: list[Scene],
    state: PlayerState,
    forced_scene_id: str | None,
    scene_mode: str,
) -> list[Scene]:
    if forced_scene_id is not None and forced_scene_id not in state.visited_scenes:
        forced = next((scene for scene in scenes if scene.id == forced_scene_id), None)
        return [forced] if forced is not None else []

    phase = phase_for_choice_index(state.choice_index)
    valid_scenes = get_valid_scenes(state, scenes)
    if not valid_scenes:
        return []

    ranked = sorted(
        valid_scenes,
        key=lambda scene: (score_scene(scene, state, phase), scene.id),
        reverse=True,
    )
    if scene_mode == "all":
        return ranked
    return ranked[:1]


def make_result(state: PlayerState, endings: list[Ending], steps: list[PathStep]) -> PathResult:
    ending = choose_ending(state, endings)
    return PathResult(
        ending_id=ending.basin or ending.id,
        ending_title=ending.title,
        steps=steps,
        state=copy.deepcopy(state),
        scores=compute_ending_scores(state),
    )


def print_report(results: list[PathResult], sample_limit: int) -> None:
    print(f"Enumerated paths: {len(results)}")
    if not results:
        return

    grouped: dict[str, list[PathResult]] = {}
    for result in results:
        grouped.setdefault(result.ending_id, []).append(result)

    print("\nEnding distribution:")
    for ending_id, ending_results in sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), item[0]),
    ):
        percent = len(ending_results) / len(results) * 100.0
        title = ending_results[0].ending_title
        print(f"  {ending_id:22s} {len(ending_results):4d}  {percent:5.1f}%  {title}")

    print("\nSample paths:")
    for ending_id, ending_results in sorted(grouped.items()):
        print(f"\n[{ending_id}]")
        for result in ending_results[: max(sample_limit, 0)]:
            state = result.state
            choice_numbers = "-".join(str(step.choice_index) for step in result.steps)
            scene_ids = " > ".join(step.scene_id for step in result.steps)
            print(f"  choices: {choice_numbers}")
            print(f"  scenes : {scene_ids}")
            print(
                "  state  : "
                f"heat={state.surveillance_heat:.1f}, "
                f"evidence={state.evidence_count:.1f}, "
                f"flags={','.join(sorted(state.flags)) or '-'}"
            )
            print(f"  top score: {top_score(result.scores)}")


def top_score(scores: dict[str, float]) -> str:
    basin, score = max(scores.items(), key=lambda item: item[1])
    return f"{basin}={score:.2f}"


if __name__ == "__main__":
    raise SystemExit(main())
