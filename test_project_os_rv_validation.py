from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_os.models import ProjectNode, ProjectRegistry
from project_os.rv_validation import build_rv_positive_validation, positive_rv_candidate_nodes


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class ProjectOsRvValidationTests(unittest.TestCase):
    def test_positive_rv_candidate_filter_excludes_negative_siblings(self) -> None:
        registry = ProjectRegistry(
            generated_at_utc="2026-05-18T00:00:00Z",
            root=".",
            nodes=[
                ProjectNode(
                    id="candidate:rv600:RV600REV001",
                    kind="candidate",
                    label="RV600REV001",
                    family="rv600",
                    metrics={"net_pnl": 1198.0, "net_pnl_unit_hint": "cents"},
                ),
                ProjectNode(
                    id="candidate:rv600:RESIDLOCK001",
                    kind="candidate",
                    label="RESIDLOCK001",
                    family="rv600",
                    metrics={"net_pnl": -28864.0, "net_pnl_unit_hint": "cents"},
                ),
                ProjectNode(
                    id="candidate:v28_successor:RVTERMLOCK001",
                    kind="candidate",
                    label="RVTERMLOCK001",
                    family="v28_successor",
                    metrics={"net_pnl": 17528.0, "net_pnl_unit_hint": "cents"},
                ),
            ],
        )

        labels = [node.label for node in positive_rv_candidate_nodes(registry)]

        self.assertEqual(labels, ["RVTERMLOCK001", "RV600REV001"])

    def test_positive_rv_candidate_filter_prefers_standardized_weekly_pnl(self) -> None:
        registry = ProjectRegistry(
            generated_at_utc="2026-05-18T00:00:00Z",
            root=".",
            nodes=[
                ProjectNode(
                    id="candidate:rv600:RV600A",
                    kind="candidate",
                    label="RV600A",
                    family="rv600",
                    metrics={
                        "net_pnl": 10000.0,
                        "net_pnl_unit_hint": "cents",
                        "pnl_7d_dollars": 10.0,
                        "pnl_7d_display": "$10.00",
                    },
                ),
                ProjectNode(
                    id="candidate:rv600:RV600B",
                    kind="candidate",
                    label="RV600B",
                    family="rv600",
                    metrics={
                        "net_pnl": 100.0,
                        "net_pnl_unit_hint": "cents",
                        "pnl_7d_dollars": 70.0,
                        "pnl_7d_display": "$70.00",
                    },
                ),
            ],
        )

        labels = [node.label for node in positive_rv_candidate_nodes(registry)]

        self.assertEqual(labels, ["RV600B", "RV600A"])

    def test_rv600_forward_audit_classifies_positive_but_underpowered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "logs" / "particle_research" / "locked_oos_plans" / "rv600_revision_RV600REV001_locked_plan.json"
            write_json(
                plan_path,
                {
                    "plan_id": "RV600REV001",
                    "candidate": {
                        "required_accounting_modes": [
                            "all_entries",
                            "one_per_side_per_market",
                            "position_capped",
                        ]
                    },
                    "rationale": {
                        "prior_diagnostic_metrics": {
                            "selected_pnl_cents": 1198.0,
                            "avg_pnl_per_entry_cents": 19.0,
                            "positive_root_rate": 0.6,
                            "positive_market_rate": 0.61,
                            "max_single_market_pnl_share": 0.23,
                            "last_window_pnl_cents": 28.0,
                        }
                    },
                    "forward_gates": {
                        "target_accepted_entries": 100,
                        "target_distinct_markets": 40,
                        "target_calendar_days": 10,
                        "target_weekend_sessions": 2,
                    },
                },
            )
            write_json(
                root / "logs" / "project_os" / "rv_positive_candidate_forward_audit_RV600REV001.json",
                {
                    "decision": "locked_plan_forward_incomplete_or_failed",
                    "plan_json": str(plan_path),
                    "sample_gates": {
                        "accepted_entries": False,
                        "distinct_markets": False,
                        "calendar_days": False,
                        "weekend_sessions": False,
                    },
                    "calendar_day_count": 1,
                    "weekend_day_count": 0,
                    "primary_summary": {
                        "accepted_entries": 32,
                        "distinct_markets": 15,
                        "selected_pnl_cents": -136.0,
                        "avg_pnl_per_entry_cents": -4.25,
                        "positive_root_rate": 0.4,
                        "positive_market_rate": 0.4,
                        "max_single_market_pnl_share": 0.0,
                        "last_window_pnl_cents": 12.0,
                        "no_fill_penalty_pnl_cents": -136.0,
                        "repeated_entry_gate_pass": False,
                        "rejection_reason": "nonpositive_pnl;does_not_beat_matched_v28_by_20pct",
                    },
                    "summary_rows": [
                        {"accounting_mode": "all_entries"},
                        {"accounting_mode": "one_per_side_per_market"},
                        {"accounting_mode": "position_capped"},
                    ],
                },
            )
            registry = ProjectRegistry(
                generated_at_utc="2026-05-18T00:00:00Z",
                root=str(root),
                nodes=[
                    ProjectNode(
                        id="candidate:rv600:RV600REV001",
                        kind="candidate",
                        label="RV600REV001",
                        family="rv600",
                        path=str(plan_path),
                        metrics={"net_pnl": 1198.0, "net_pnl_unit_hint": "cents"},
                    )
                ],
            )
            write_json(root / "logs" / "project_os" / "registry_latest.json", registry.to_dict())

            payload = build_rv_positive_validation(root)
            row = payload["candidate_results"][0]

            self.assertEqual(row["candidate_id"], "RV600REV001")
            self.assertIn("registry_pnl_7d_display", row)
            self.assertEqual(row["verdict"], "blocked_forward_failed_and_underpowered")
            self.assertIn("forward_selected_pnl_positive", row["blocking_gates"])
            self.assertIn("forward_entries_at_least_target", row["blocking_gates"])

    def test_terminal_oos_positive_pnl_can_still_fail_robustness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "logs" / "particle_research" / "locked_oos_plans" / "particle_spot_rv_terminal_oos_RVTERMLOCK001_locked_oos_plan.json"
            report_path = root / "logs" / "particle_research" / "real_shadow" / "particle_spot_rv_terminal_oos_RVTERMLOCK001" / "reports" / "spot_realized_vol_terminal_oos_locked.json"
            write_json(plan_path, {"artifact_root": "logs/particle_research/real_shadow/particle_spot_rv_terminal_oos_RVTERMLOCK001"})
            write_json(
                report_path,
                {
                    "market_count": 7,
                    "candidate_count": 4512,
                    "gate_config": {"min_candidate_count": 1000, "min_market_count": 5, "min_selected_count": 250},
                    "gate_results": {
                        "all_passed": False,
                        "locked_oos_scope": True,
                        "enough_candidates": True,
                        "enough_markets": True,
                        "enough_selected": True,
                        "positive_total_pnl": True,
                        "positive_avg_pnl": True,
                        "beats_static_particle_pnl": True,
                        "beats_current_calibrated_pnl": False,
                        "beats_current_probability": False,
                        "beats_market_probability": False,
                        "beats_brownian_probability": True,
                        "positive_ev_rank": False,
                        "positive_top_ev_bucket": False,
                    },
                    "selected_variant": {
                        "selected_count": 4108,
                        "total_counterfactual_pnl_cents": 17528.0,
                    },
                },
            )
            registry = ProjectRegistry(
                generated_at_utc="2026-05-18T00:00:00Z",
                root=str(root),
                nodes=[
                    ProjectNode(
                        id="candidate:v28_successor:RVTERMLOCK001",
                        kind="candidate",
                        label="RVTERMLOCK001",
                        family="v28_successor",
                        path=str(plan_path),
                        metrics={
                            "net_pnl": 17528.0,
                            "net_pnl_unit_hint": "cents",
                            "net_pnl_source_key": str(report_path) + ":selected_variant.total_counterfactual_pnl_cents",
                        },
                    )
                ],
            )
            write_json(root / "logs" / "project_os" / "registry_latest.json", registry.to_dict())

            payload = build_rv_positive_validation(root)
            row = payload["candidate_results"][0]

            self.assertEqual(row["verdict"], "blocked_oos_robustness_failed")
            self.assertIn("beats_current_probability", row["blocking_gates"])
            self.assertEqual(row["forward_or_oos_pnl_cents"], 17528.0)


if __name__ == "__main__":
    unittest.main()
