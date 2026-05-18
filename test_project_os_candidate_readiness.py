from __future__ import annotations

import unittest

from project_os.candidate_readiness import evaluate_candidate
from project_os.models import ProjectNode


class CandidateReadinessTests(unittest.TestCase):
    def test_promotable_forward_candidate_is_controlled_live_test_ready(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_logged_events_diagnostic",
            kind="candidate",
            label="v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic",
            family="v28_successor",
            status="strong_candidate",
            evidence_level="forward_shadow",
            metrics={
                "promotion_verifier_verdict": "promotable",
                "net_pnl": 2800.0,
                "net_pnl_unit_hint": "cents",
                "rows": 226,
                "markets": 44,
                "forward_gate_forward_evidence_promotable": True,
                "forward_gate_delta_brier_candidate_minus_v28": -0.0002,
                "forward_gate_delta_logloss_candidate_minus_v28": -0.002,
                "forward_gate_near_boundary_delta_brier_candidate_minus_v28": -0.00008,
            },
        )

        row = evaluate_candidate(node)

        self.assertEqual(row["readiness_level"], "controlled_live_test_ready")
        self.assertTrue(row["controlled_live_test_ready"])
        self.assertFalse(row["live_order_ready"])
        self.assertEqual(row["status_update"], "strong_candidate")

    def test_positive_but_baseline_failed_candidate_is_not_live_ready(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:PSLICELOCK001",
            kind="candidate",
            label="PSLICELOCK001",
            family="v28_successor",
            status="blocked",
            evidence_level="forward_shadow",
            metrics={
                "net_pnl": 450.5,
                "net_pnl_unit_hint": "cents",
                "entries": 177,
                "markets": 28,
                "linked_oos_failed_gates": ["beats_baseline_brier", "beats_baseline_logloss"],
            },
        )

        row = evaluate_candidate(node)

        self.assertFalse(row["controlled_live_test_ready"])
        self.assertIn("readiness:baseline_or_calibration_failed", row["blockers"])
        self.assertEqual(row["readiness_level"], "near_miss_review")

    def test_level_two_false_policy_stays_shadow_ready(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:v28s_live_pnl_midband_no_fade_yes_v019",
            kind="candidate",
            label="v28s_live_pnl_midband_no_fade_yes_v019",
            family="v28_successor",
            status="worth_watching",
            evidence_level="live_forward",
            metrics={
                "net_pnl": 70.0,
                "net_pnl_unit_hint": "cents",
                "rows": 314,
                "markets": 12,
                "entries": 3,
                "primary_delta_vs_v28_cents": 762.3,
                "level_1_complete": True,
                "level_2_controlled_live_test_ready": False,
            },
        )

        row = evaluate_candidate(node)

        self.assertEqual(row["readiness_level"], "live_shadow_ready")
        self.assertTrue(row["live_shadow_ready"])
        self.assertFalse(row["controlled_live_test_ready"])
        self.assertIn("readiness:explicit_level_2_controlled_live_test_false", row["blockers"])

    def test_baseline_control_row_is_not_near_miss(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:v28_raw_logged_events_diagnostic",
            kind="candidate",
            label="v28_raw / logged_events_diagnostic",
            family="v28_successor",
            status="blocked",
            evidence_level="forward_shadow",
            metrics={
                "net_pnl": 2800.0,
                "net_pnl_unit_hint": "cents",
                "rows": 578,
                "markets": 88,
                "promotion_verifier_failed_gates": ["candidate_is_not_baseline"],
            },
        )

        row = evaluate_candidate(node)

        self.assertEqual(row["readiness_level"], "baseline_control_only")
        self.assertEqual(row["status_update"], "blocked")
        self.assertFalse(row["controlled_live_test_ready"])

    def test_prior_readiness_blocker_does_not_self_contaminate_refresh(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:v28s_positive_shadow_candidate",
            kind="candidate",
            label="v28s_positive_shadow_candidate",
            family="v28_successor",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            metrics={
                "net_pnl": 100.0,
                "net_pnl_unit_hint": "cents",
                "rows": 120,
                "markets": 24,
                "forward_gate_forward_evidence_promotable": True,
                "forward_gate_delta_brier_candidate_minus_v28": -0.0001,
                "forward_gate_delta_logloss_candidate_minus_v28": -0.0001,
                "forward_gate_near_boundary_delta_brier_candidate_minus_v28": -0.0001,
            },
            blockers=["readiness:baseline_or_calibration_failed"],
        )

        row = evaluate_candidate(node)

        self.assertEqual(row["readiness_level"], "controlled_live_test_ready")
        self.assertNotIn("readiness:baseline_or_calibration_failed", row["source_failures"])


if __name__ == "__main__":
    unittest.main()
