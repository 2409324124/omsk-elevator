from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engine.ending import (
    ENDING_BASINS,
    choose_ending_basin,
    compute_ending_scores,
    load_endings,
)
from engine.update import apply_choice
from engine.state import PlayerState
from scripts.enumerate_cli_paths import next_scene_candidates
from scripts.run_cli_demo import forced_next_scene_id, load_scenes


class EndingTests(unittest.TestCase):
    def test_hard_heat_triggers_missing_tourist(self) -> None:
        state = PlayerState(surveillance_heat=7.0)
        self.assertEqual(choose_ending_basin(state), "missing_tourist")

    def test_missing_theta_and_relationship_keys_do_not_crash(self) -> None:
        state = PlayerState(theta={}, relationships={})
        scores = compute_ending_scores(state)
        self.assertEqual(set(scores), set(ENDING_BASINS))

    def test_each_basin_can_be_selected(self) -> None:
        cases = {
            "safe_exit": PlayerState(
                theta={"self_preservation": 5.0, "authority_compliance": 3.0}
            ),
            "evidence_escape": PlayerState(
                theta={"truth_seek": 5.0, "group_safety": 3.0},
                evidence_count=3.0,
            ),
            "missing_tourist": PlayerState(
                theta={"truth_seek": 2.0},
                surveillance_heat=6.8,
                relationships={"reporter_trust": 2.0, "major_suspicion": 2.0},
                flags={"unauthorized_translation_to_reporter"},
            ),
            "collaborator": PlayerState(
                theta={
                    "self_preservation": 4.0,
                    "control_strategy": 4.0,
                    "authority_compliance": 3.0,
                    "local_empathy": -2.0,
                }
            ),
            "sacrifice_stay": PlayerState(
                theta={"local_empathy": 5.0, "group_safety": 4.0, "self_preservation": -3.0}
            ),
            "underground_stranded": PlayerState(
                theta={"risk_tolerance": 4.0, "local_empathy": 2.0},
                evidence_count=3.0,
                surveillance_heat=4.0,
                relationships={"major_suspicion": 2.0},
            ),
        }
        for expected, state in cases.items():
            with self.subTest(expected=expected):
                self.assertEqual(choose_ending_basin(state), expected)

    def test_flags_change_scores_without_item_text_or_llm(self) -> None:
        baseline = compute_ending_scores(PlayerState())
        evidence = compute_ending_scores(PlayerState(flags={"copied_behavior_log"}))
        collaborator = compute_ending_scores(PlayerState(flags={"framed_b1_as_fault"}))

        self.assertGreater(evidence["evidence_escape"], baseline["evidence_escape"])
        self.assertGreater(collaborator["collaborator"], baseline["collaborator"])
        self.assertGreater(collaborator["safe_exit"], baseline["safe_exit"])

    def test_unknown_flag_is_ignored(self) -> None:
        baseline = compute_ending_scores(PlayerState())
        unknown = compute_ending_scores(PlayerState(flags={"future_scene_flag"}))
        self.assertEqual(unknown, baseline)

    def test_load_endings_requires_all_basins(self) -> None:
        endings = load_endings()
        self.assertEqual({ending.basin or ending.id for ending in endings}, set(ENDING_BASINS))

    def test_load_endings_rejects_missing_basin(self) -> None:
        payload = """[
          {"id": "safe_exit", "basin": "safe_exit", "title": "x"},
          {"id": "evidence_escape", "basin": "evidence_escape", "title": "x"}
        ]"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "endings.json"
            path.write_text(payload, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing ending basin"):
                load_endings(path)

    def test_conservative_cli_path_does_not_go_missing(self) -> None:
        state = state_for_cli_choices([1, 2, 2, 2, 4])
        self.assertEqual(choose_ending_basin(state), "safe_exit")

    def test_high_risk_cli_path_still_goes_missing(self) -> None:
        state = state_for_cli_choices([3, 2, 3, 1, 1])
        self.assertEqual(choose_ending_basin(state), "missing_tourist")

    def test_sacrifice_cli_path_is_reachable(self) -> None:
        state = state_for_cli_choices([1, 1, 1, 1, 3])
        self.assertEqual(choose_ending_basin(state), "sacrifice_stay")


def state_for_cli_choices(choices: list[int]) -> PlayerState:
    state = PlayerState()
    scenes = load_scenes(Path("data/scenes"))
    forced_scene_id = None
    for choice_number in choices:
        candidates = next_scene_candidates(scenes, state, forced_scene_id, "argmax")
        if not candidates:
            raise AssertionError("choice path ended before all choices were applied")
        scene = candidates[0]
        state.visited_scenes.append(scene.id)
        choice = scene.choices[choice_number - 1]
        apply_choice(state, choice)
        forced_scene_id = forced_next_scene_id(choice, state)
    return state


if __name__ == "__main__":
    unittest.main()
