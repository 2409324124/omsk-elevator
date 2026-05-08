"""Minimal interactive CLI for the adaptive Omsk VN prototype."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.ending import choose_ending, load_endings
from engine.router import choose_next_scene, get_valid_scenes
from engine.schema import Choice, Ending, Scene
from engine.state import PlayerState
from engine.update import apply_choice
from scripts.validate_scenes import load_scene_documents, validate_scenes


MAX_STEPS = 5


def main() -> int:
    scenes = load_scenes(Path("data/scenes"))
    endings = load_endings(Path("data/scenes/endings.json"))
    state = PlayerState()
    rng = np.random.default_rng(7)
    forced_scene_id: str | None = None

    print("《电梯向下》CLI 原型")
    print("你是美国参访团的随团翻译。你只知道这是一场重建观察访问。\n")

    for _ in range(MAX_STEPS):
        phase = phase_for_choice_index(state.choice_index)
        scene = pop_forced_scene(forced_scene_id, scenes, state)
        forced_scene_id = None
        if scene is None:
            scene = choose_next_scene(get_valid_scenes(state, scenes), state, phase, rng)
        if scene is None:
            break

        state.visited_scenes.append(scene.id)
        print_scene(scene, state)
        choice = read_choice(scene)
        apply_choice(state, choice)
        forced_scene_id = forced_next_scene_id(choice, state)
        print()

    print_state_summary(state)
    print_ending(choose_ending(state, endings))
    return 0


def load_scenes(scene_dir: Path) -> list[Scene]:
    documents = load_scene_documents(scene_dir)
    errors = validate_scenes(documents)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    scene_documents = [
        document
        for document in documents
        if "visible_text" in document and "choices" in document
    ]
    return [Scene.from_dict(document) for document in scene_documents]


def phase_for_choice_index(choice_index: int) -> str:
    if choice_index <= 2:
        return "surface_fixed"
    if choice_index <= 4:
        return "early_adaptive"
    return "underground_router"


def print_scene(scene: Scene, state: PlayerState) -> None:
    print(f"[{state.choice_index + 1}] {scene.title}")
    print(scene.visible_text)
    for index, choice in enumerate(scene.choices, start=1):
        print(f"  {index}. {choice.text}")


def read_choice(scene: Scene) -> Choice:
    while True:
        raw = input("> ").strip()
        try:
            index = int(raw)
        except ValueError:
            print("请输入选项编号。")
            continue
        if 1 <= index <= len(scene.choices):
            return scene.choices[index - 1]
        print("没有这个选项。")


def pop_forced_scene(
    scene_id: str | None,
    scenes: list[Scene],
    state: PlayerState,
) -> Scene | None:
    if scene_id is None or scene_id in state.visited_scenes:
        return None
    return next((scene for scene in scenes if scene.id == scene_id), None)


def forced_next_scene_id(choice: Choice, state: PlayerState) -> str | None:
    rule = choice.force_next_if
    if not rule:
        return None
    if "surveillance_heat_gte" in rule and state.surveillance_heat < float(rule["surveillance_heat_gte"]):
        return None
    if "surveillance_heat_lte" in rule and state.surveillance_heat > float(rule["surveillance_heat_lte"]):
        return None
    if "evidence_count_gte" in rule and state.evidence_count < float(rule["evidence_count_gte"]):
        return None
    if "evidence_count_lte" in rule and state.evidence_count > float(rule["evidence_count_lte"]):
        return None
    if "choice_index_gte" in rule and state.choice_index < int(rule["choice_index_gte"]):
        return None
    if "choice_index_lte" in rule and state.choice_index > int(rule["choice_index_lte"]):
        return None
    if "flag_present" in rule and str(rule["flag_present"]) not in state.flags:
        return None
    if "flag_absent" in rule and str(rule["flag_absent"]) in state.flags:
        return None
    return str(rule["scene"]) if "scene" in rule else None


def print_state_summary(state: PlayerState) -> None:
    print("访问暂告一段落。")
    print(f"已做选择：{state.choice_index}")
    print(f"被注意到的程度：{state.surveillance_heat:.1f}")
    print(f"带走或记住的线索：{state.evidence_count:.1f}")
    print(narrative_tendency(state))


def print_ending(ending: Ending) -> None:
    print()
    print(f"结局：{ending.title}")
    print(ending.text)


def narrative_tendency(state: PlayerState) -> str:
    truth = state.theta.get("truth_seek", 0.0)
    safety = state.theta.get("self_preservation", 0.0)
    compliance = state.theta.get("authority_compliance", 0.0)
    if truth > safety and truth > compliance:
        return "你的路线显示：压力升高时，你仍倾向于让事实留下痕迹。"
    if safety >= truth and safety >= compliance:
        return "你的路线显示：在陌生秩序里，你更倾向于先保护队伍和自己。"
    return "你的路线显示：你正在用配合换取更多观察空间。"


if __name__ == "__main__":
    raise SystemExit(main())
