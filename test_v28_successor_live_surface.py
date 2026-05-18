from __future__ import annotations

import csv
import unittest
from pathlib import Path

from train_v28_successor_candidates import predict_monotonic_tabular
from v28_successor_live_surface import DEFAULT_CANDIDATE_ID, DEFAULT_MODEL_HASH, load_surface


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "research_particle" / "v28_successor" / "candidate_manifests_logged_events_latest.json"
PREDICTIONS = ROOT / "research_particle" / "v28_successor" / "candidate_predictions_logged_events_latest.csv"


class V28SuccessorLiveSurfaceTests(unittest.TestCase):
    def test_live_surface_matches_frozen_training_formula(self) -> None:
        surface = load_surface(MANIFEST, candidate_id=DEFAULT_CANDIDATE_ID, expected_model_hash=DEFAULT_MODEL_HASH)
        checked = 0
        with PREDICTIONS.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("candidate_id") != DEFAULT_CANDIDATE_ID:
                    continue
                features = {
                    "target_v28_p_yes": float(row["v28_p_yes"]),
                    "abs_d_sigma": float(row["abs_d_sigma"]),
                    "seconds_to_close": float(row["seconds_to_close"]),
                }
                live = surface.predict(
                    raw_p_yes=features["target_v28_p_yes"],
                    features=features,
                )
                expected = predict_monotonic_tabular(surface.model_parameters, features)
                self.assertAlmostEqual(live.p_yes, expected, places=12)
                self.assertAlmostEqual(live.p_yes, float(row["candidate_p_yes"]), places=12)
                checked += 1
                if checked >= 25:
                    break
        self.assertEqual(checked, 25)

    def test_time_safe_gate_reverts_to_raw_inside_final_240_seconds(self) -> None:
        surface = load_surface(MANIFEST, candidate_id=DEFAULT_CANDIDATE_ID, expected_model_hash=DEFAULT_MODEL_HASH)
        raw = 0.86
        late = surface.predict(raw_p_yes=raw, features={"abs_d_sigma": 0.5, "seconds_to_close": 180.0})
        full = surface.predict(raw_p_yes=raw, features={"abs_d_sigma": 0.5, "seconds_to_close": 600.0})

        self.assertAlmostEqual(late.p_yes, raw, places=12)
        self.assertNotAlmostEqual(full.p_yes, raw, places=8)
        self.assertEqual(late.time_weight, 0.0)
        self.assertEqual(full.time_weight, 1.0)


if __name__ == "__main__":
    unittest.main()
