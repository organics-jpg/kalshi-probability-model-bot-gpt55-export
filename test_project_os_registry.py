from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_os.adapters import logs_adapter
from project_os.family import infer_family
from project_os.models import ProjectNode
from project_os.node_audit import write_node_audit
from project_os.patterns import normalized_metric_snapshot
from project_os.registry import _apply_verdict_constraints, build_registry, infer_next_action


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class ProjectOsRegistryTests(unittest.TestCase):
    def test_family_normalization_core_families(self) -> None:
        self.assertEqual(infer_family("probe_rv600_objective_state_audit.py"), "rv600")
        self.assertEqual(infer_family("OU_MISPRICING_BACKTEST_LATEST.md"), "ou_mispricing")
        self.assertEqual(infer_family("v28_successor_live_pnl_policy_score_latest.json"), "v28_successor")
        self.assertEqual(infer_family("threshold_touch_exit_gate.py"), "ninety_touch")
        self.assertEqual(infer_family("truffle_exit_supervisor_prompt.txt"), "truffle")
        self.assertEqual(infer_family("mushroom_v28_common_clock_phi_reward_memory"), "live_v28")
        self.assertEqual(infer_family("particle_fixed_terminal_oos_GAUSS45LOCK001"), "particle_sim")
        self.assertEqual(infer_family("RESEARCH_OS_V2_STRATEGY_MEMORY_DECISION_ENGINE_SPEC.md"), "research_os")
        self.assertEqual(infer_family("living_analytics_dashboard_pixel_spec.md"), "dashboard_ui")
        self.assertEqual(infer_family("live_90_78"), "legacy_live")

    def test_registry_builds_nodes_edges_and_sensitive_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "stats" / "live_mushroom_v28_size2" / "summary.json",
                {"net_pnl_total_dollars": 12.5, "entries_total": 4, "win_rate": 75.0, "score_mode": "live_only"},
            )
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json",
                {"candidate_id": "RV600NEAR001", "params": {"edge": 4}},
            )
            write_json(
                root / "logs" / "particle_research" / "reports" / "rv600_objective_state_latest.json",
                {"promotion_allowed": False, "blocked_by": ["avg_entry_below_10c"], "selected_pnl_cents": 350},
            )
            write_json(
                root / "research_data" / "rv600_next_evidence_shadow_20260515T213152Z" / "metadata" / "dataset_manifest.json",
                {"dataset_tag": "rv600_next_evidence_shadow_20260515T213152Z", "recorder_type": "native_passive", "market_tickers": ["A", "B"]},
            )
            (root / ".env").write_text("SECRET_TOKEN=visible-by-user-preference\n", encoding="utf-8")
            registry = build_registry(root, write=True)
            node_ids = {node.id for node in registry.nodes}
            self.assertIn("stats:live_v28:live_mushroom_v28_size2", node_ids)
            self.assertIn("candidate:rv600:RV600NEAR001", node_ids)
            report = next(node for node in registry.nodes if node.id == "report:rv600:rv600_objective_state_latest")
            self.assertEqual(report.metrics.get("net_pnl_source_key"), "selected_pnl_cents")
            self.assertEqual(report.metrics.get("net_pnl_unit_hint"), "cents")
            stats = next(node for node in registry.nodes if node.id == "stats:live_v28:live_mushroom_v28_size2")
            stats_snapshot = normalized_metric_snapshot(stats)
            self.assertEqual(stats_snapshot["pnl_confidence"], "high")
            self.assertEqual(stats_snapshot["pnl_unit"], "dollars")
            plan_candidate = next(node for node in registry.nodes if node.id == "candidate:rv600:RV600NEAR001")
            self.assertIn(plan_candidate.metrics.get("pnl_status"), {"no_actual_pnl_in_locked_plan", "no_source_pnl"})
            self.assertIn("locked plan", plan_candidate.metrics.get("pnl_missing_reason", ""))
            secret = next(node for node in registry.nodes if node.kind == "secret" and node.sensitive)
            self.assertEqual(secret.raw_preview, "")
            self.assertFalse(any(node.kind == "health_issue" and "sensitive file indexed" in node.label for node in registry.nodes))
            self.assertNotIn("SECRET_TOKEN", (root / "logs" / "project_os" / "registry_latest.json").read_text(encoding="utf-8"))
            self.assertTrue(any(edge.source.startswith("family:rv600") for edge in registry.edges))
            self.assertTrue(any(edge.source == "report:rv600:rv600_objective_state_latest" and edge.relation == "blocks" for edge in registry.edges))
            self.assertTrue((root / "logs" / "project_os" / "registry_latest.json").exists())
            self.assertTrue(list((root / "logs" / "project_os").glob("registry_*.json")))

    def test_missing_stats_summary_is_classified_not_health_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stats" / "default").mkdir(parents=True)
            registry = build_registry(root, write=False)

            stats_node = next(node for node in registry.nodes if node.id == "stats:infrastructure:default")

            self.assertIn("missing_summary", stats_node.tags)
            self.assertEqual(stats_node.status, "diagnostic_only")
            self.assertEqual(stats_node.evidence_level, "metadata_only")
            self.assertIn("Regenerate summary.json", stats_node.next_action)
            self.assertFalse(any(node.kind == "health_issue" and "missing stats summary" in node.label for node in registry.nodes))

    def test_large_log_folder_is_classified_not_health_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_folder = root / "logs" / "particle_research"
            log_folder.mkdir(parents=True)
            (log_folder / "bot.log").write_text("ok\n", encoding="utf-8")
            original_threshold = logs_adapter.LARGE_LOG_FOLDER_BYTES
            logs_adapter.LARGE_LOG_FOLDER_BYTES = 1
            try:
                registry = build_registry(root, write=False)
            finally:
                logs_adapter.LARGE_LOG_FOLDER_BYTES = original_threshold

            log_node = next(node for node in registry.nodes if node.id == "log:particle_sim:particle_research")

            self.assertIn("large_folder", log_node.tags)
            self.assertTrue(log_node.metrics.get("large_folder"))
            self.assertIn("metadata only", log_node.summary.lower())
            self.assertFalse(any(node.kind == "health_issue" and "large log folder" in node.label for node in registry.nodes))

    def test_malformed_json_becomes_health_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "logs" / "particle_research" / "reports" / "rv600_bad_latest.json"
            bad.parent.mkdir(parents=True, exist_ok=True)
            bad.write_text("{not json", encoding="utf-8")
            registry = build_registry(root, write=False)
            self.assertTrue(any(node.kind == "health_issue" and "limited report parse" in node.label for node in registry.nodes))

    def test_replay_only_next_action_freezes_before_counting_evidence(self) -> None:
        node = ProjectNode(
            id="candidate:rv600:test",
            kind="candidate",
            label="test",
            family="rv600",
            status="strong_candidate",
            evidence_level="backtest",
        )
        self.assertEqual(infer_next_action(node), "Freeze candidate before counting future evidence.")
        constrained = _apply_verdict_constraints(node)
        self.assertEqual(constrained.status, "worth_watching")

    def test_status_override_cannot_make_replay_only_strong(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "reports" / "rv600_backtest_latest.json",
                {"promotion_allowed": True, "net_pnl_dollars": 12.5},
            )
            write_json(
                root / "project_os" / "overrides.json",
                {"status_overrides": {"report:rv600:rv600_backtest_latest": "strong_candidate"}},
            )
            registry = build_registry(root, write=False)
            report = next(node for node in registry.nodes if node.id == "report:rv600:rv600_backtest_latest")
            self.assertEqual(report.evidence_level, "backtest")
            self.assertEqual(report.status, "worth_watching")
            self.assertIn("downgraded_replay_only", report.tags)

    def test_locked_plan_prior_diagnostic_pnl_is_tagged_as_cents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json",
                {
                    "plan_id": "RV600NEAR001",
                    "rationale": {
                        "prior_diagnostic_metrics": {
                            "selected_pnl_cents": 339.0,
                            "avg_pnl_per_entry_cents": 8.26,
                            "positive_market_rate": 0.6071,
                        }
                    },
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:rv600:RV600NEAR001")
            snapshot = normalized_metric_snapshot(candidate)

            self.assertEqual(snapshot["pnl_unit"], "cents")
            self.assertEqual(snapshot["pnl_confidence"], "high")
            self.assertAlmostEqual(snapshot["pnl_value"], 3.39)
            self.assertEqual(candidate.metrics.get("pnl_provenance"), "prior_diagnostic_metrics_from_locked_plan")

    def test_candidate_pnl_is_standardized_to_one_week_from_market_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "fixed_terminal_GAUSS45LOCK009_locked_oos_plan.json",
                {
                    "hypothesis_id": "gaussian_vol45_terminal_v1",
                    "artifact_root": "logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK009",
                },
            )
            write_json(
                root / "logs" / "particle_research" / "real_shadow" / "particle_fixed_terminal_oos_GAUSS45LOCK009" / "reports" / "fixed_terminal_oos_locked.json",
                {
                    "market_count": 96,
                    "gate_results": {"all_passed": True, "locked_oos_scope": True},
                    "selected_variant": {
                        "selected_count": 960,
                        "total_counterfactual_pnl_cents": 9600.0,
                    },
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:particle_sim:GAUSS45LOCK009")

            self.assertEqual(candidate.metrics.get("actual_pnl_source_key"), "net_pnl")
            self.assertAlmostEqual(candidate.metrics.get("actual_pnl_source_dollars"), 96.0)
            self.assertAlmostEqual(candidate.metrics.get("pnl_observed_window_days"), 1.0)
            self.assertEqual(candidate.metrics.get("pnl_observed_window_confidence"), "assumed")
            self.assertAlmostEqual(candidate.metrics.get("actual_pnl_7d_dollars"), 672.0)
            self.assertAlmostEqual(candidate.metrics.get("projected_pnl_7d_dollars"), 672.0)
            self.assertEqual(candidate.metrics.get("pnl_7d_display"), "$672.00")

    def test_paired_slice_locked_plan_reads_local_oos_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "paired_sidecar_slice_PSLICELOCK001_locked_plan.json",
                {
                    "run_id": "PSLICELOCK001",
                    "evaluation_scope": "locked_forward_shadow",
                },
            )
            write_json(
                root / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_oos_PSLICELOCK001_latest.json",
                {
                    "evaluation_scope": "locked_forward_shadow",
                    "gate_results": {
                        "all_passed": False,
                        "locked_forward_scope": True,
                        "beats_baseline_brier": False,
                        "beats_baseline_logloss": False,
                        "positive_selected_pnl": True,
                    },
                    "selected_metrics": {
                        "selected_pnl_cents": 450.5,
                        "selected_count": 177,
                        "markets": 24,
                        "positive_selected_market_count": 9,
                    },
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:v28_successor:PSLICELOCK001")

            self.assertEqual(candidate.status, "blocked")
            self.assertEqual(candidate.evidence_level, "forward_shadow")
            self.assertEqual(candidate.metrics.get("pnl_provenance"), "paired_sidecar_slice_oos_report")
            self.assertIn("linked_oos_gate_failed:beats_baseline_brier", candidate.blockers)
            self.assertAlmostEqual(candidate.metrics.get("actual_pnl_source_dollars"), 4.505)
            self.assertEqual(candidate.metrics.get("pnl_standardization_status"), "standardized")

    def test_next_step_outcome_adapter_updates_existing_node_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "rv600_revision_RV600REV001_locked_plan.json",
                {"plan_id": "RV600REV001"},
            )
            write_json(
                root / "logs" / "project_os" / "next_step_outcomes_latest.json",
                {
                    "summary": "fixture",
                    "outcomes": [
                        {
                            "node_id": "candidate:rv600:RV600REV001",
                            "kind": "candidate",
                            "label": "RV600REV001",
                            "family": "rv600",
                            "status": "blocked",
                            "evidence_level": "metadata_only",
                            "completion_status": "completed",
                            "outcome": "reviewed",
                            "next_action": "Fixture reviewed next action.",
                            "blockers": ["next_step:fixture_blocker"],
                        }
                    ],
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:rv600:RV600REV001")

            self.assertEqual(candidate.next_action, "Fixture reviewed next action.")
            self.assertIn("next_step:fixture_blocker", candidate.blockers)
            self.assertIn("next_step_reviewed", candidate.tags)
            self.assertNotIn("report:research_os:next_step_outcomes_latest", {node.id for node in registry.nodes})

    def test_node_audit_updates_each_node_without_summary_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "stats" / "live_mushroom_v28_size2" / "summary.json",
                {"net_pnl_total_dollars": 12.5, "entries_total": 4, "win_rate": 75.0},
            )
            first_registry = build_registry(root, write=True)
            write_node_audit(root)

            registry = build_registry(root, write=False)
            audited = [node for node in registry.nodes if "atlas_node_audited" in (node.tags or [])]

            self.assertEqual(len(audited), len(first_registry.nodes))
            self.assertFalse(any(node.id == "report:research_os:node_audit_latest" for node in registry.nodes))
            stats = next(node for node in registry.nodes if node.id == "stats:live_v28:live_mushroom_v28_size2")
            self.assertTrue(stats.metrics.get("atlas_node_reviewed"))
            self.assertEqual(stats.metrics.get("atlas_node_audit_status"), "verified")
            self.assertEqual(registry.adapter_summaries.get("node_audit_adapter", {}).get("node_update_mode"), "direct_node_updates_only")

    def test_rv600_locked_plan_reads_project_os_forward_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "rv600_revision_RV600REV001_locked_plan.json",
                {
                    "plan_id": "RV600REV001",
                    "rationale": {
                        "prior_diagnostic_metrics": {
                            "selected_pnl_cents": 1198.0,
                            "avg_pnl_per_entry_cents": 19.0,
                            "positive_market_rate": 0.61,
                        }
                    },
                },
            )
            write_json(
                root / "logs" / "project_os" / "rv_positive_candidate_forward_audit_RV600REV001.json",
                {
                    "decision": "locked_plan_forward_incomplete_or_failed",
                    "root_count": 15,
                    "calendar_day_count": 1,
                    "sample_gates": {"accepted_entries": False, "distinct_markets": False},
                    "primary_summary": {
                        "accepted_entries": 32,
                        "distinct_markets": 15,
                        "selected_pnl_cents": -136.0,
                        "avg_pnl_per_entry_cents": -4.25,
                        "rejection_reason": "nonpositive_pnl;does_not_beat_matched_v28_by_20pct",
                    },
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:rv600:RV600REV001")

            self.assertEqual(candidate.status, "blocked")
            self.assertEqual(candidate.evidence_level, "forward_shadow")
            self.assertEqual(candidate.metrics.get("rv_forward_selected_pnl_cents"), -136.0)
            self.assertIn("rv_forward_gate_failed:sample_accepted_entries", candidate.blockers)
            self.assertIn("rv_forward_gate_failed:nonpositive_pnl", candidate.blockers)
            self.assertIn("Forward audit refreshed", candidate.next_action)
            self.assertEqual(candidate.metrics.get("actual_pnl_source_key"), "rv_forward_selected_pnl_cents")
            self.assertAlmostEqual(candidate.metrics.get("pnl_observed_window_days"), 1.0)
            self.assertAlmostEqual(candidate.metrics.get("pnl_7d_dollars"), -9.52)

    def test_locked_plan_reads_linked_oos_report_pnl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "fixed_terminal_GAUSS45LOCK001_locked_oos_plan.json",
                {
                    "hypothesis_id": "gaussian_vol45_terminal_v1",
                    "artifact_root": "logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK001",
                    "gate_config": {"min_total_pnl_cents": 1.0},
                },
            )
            write_json(
                root / "logs" / "particle_research" / "real_shadow" / "particle_fixed_terminal_oos_GAUSS45LOCK001" / "reports" / "fixed_terminal_oos_locked.json",
                {
                    "market_count": 4,
                    "selected_variant": {
                        "selected_count": 2330,
                        "total_counterfactual_pnl_cents": 47330.0,
                    },
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:particle_sim:GAUSS45LOCK001")
            snapshot = normalized_metric_snapshot(candidate)

            self.assertEqual(snapshot["pnl_unit"], "cents")
            self.assertAlmostEqual(snapshot["pnl_value"], 473.30)
            self.assertEqual(candidate.metrics.get("pnl_provenance"), "linked_oos_report")
            self.assertEqual(snapshot["entries"], 2330)

    def test_locked_plan_surfaces_linked_oos_gate_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "fixed_terminal_GAUSS45LOCK002_locked_oos_plan.json",
                {
                    "hypothesis_id": "gaussian_vol45_terminal_v1",
                    "artifact_root": "logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK002",
                },
            )
            write_json(
                root / "logs" / "particle_research" / "real_shadow" / "particle_fixed_terminal_oos_GAUSS45LOCK002" / "reports" / "fixed_terminal_oos_locked.json",
                {
                    "evaluation_scope": "locked_oos_shadow",
                    "market_count": 7,
                    "gate_results": {
                        "all_passed": False,
                        "locked_oos_scope": True,
                        "positive_total_pnl": True,
                        "beats_brownian_probability": False,
                    },
                    "selected_variant": {
                        "selected_count": 4378,
                        "total_counterfactual_pnl_cents": 49703.0,
                    },
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:particle_sim:GAUSS45LOCK002")

            self.assertEqual(candidate.status, "blocked")
            self.assertEqual(candidate.evidence_level, "forward_shadow")
            self.assertIn("linked_oos_gate_failed:beats_brownian_probability", candidate.blockers)
            self.assertIn("linked OOS failed gates", candidate.next_action)

    def test_report_pnl_count_is_not_used_as_money(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "reports" / "paired_sidecar_online_calibration_latest.json",
                {
                    "summary": {
                        "best_blend_positive_market_selected_pnl_count": 33,
                        "best_model_by_pnl": "candle_brownian",
                    },
                    "model_rows": [
                        {"markets": 68, "selected_count": 683, "selected_pnl_cents": 2108.1},
                    ],
                },
            )

            registry = build_registry(root, write=False)
            report = next(node for node in registry.nodes if node.id == "report:v28_successor:paired_sidecar_online_calibration_latest")
            snapshot = normalized_metric_snapshot(report)

            self.assertEqual(report.metrics.get("net_pnl_source_key"), "model_rows.selected_pnl_cents")
            self.assertEqual(snapshot["pnl_unit"], "cents")
            self.assertAlmostEqual(snapshot["pnl_value"], 21.081)

    def test_multi_candidate_report_does_not_smear_report_pnl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "reports" / "rv600_multi_latest.json",
                {
                    "note": "Compares GAUSS45LOCK001 and CONSENSUSLOCK001 as siblings.",
                    "selected_pnl_cents": 10918,
                },
            )

            registry = build_registry(root, write=False)
            candidate_ids = {node.id for node in registry.nodes if node.kind == "candidate"}

            self.assertNotIn("candidate:rv600:GAUSS45LOCK001", candidate_ids)
            self.assertNotIn("candidate:rv600:CONSENSUSLOCK001", candidate_ids)

    def test_v28_successor_verifier_rows_become_distinct_candidate_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "edge_research" / "v28_successor_promotion_verifier_latest.json",
                {
                    "candidates": [
                        {
                            "candidate_id": "v28s_boundary_monotonic_time_safe_v001",
                            "variant": "logged_events_diagnostic",
                            "verdict": "promotable",
                            "model_hash": "abc123",
                            "model_type": "monotonic_tabular_calibration",
                            "model_track": "pure_physics",
                            "failed_gates": [],
                            "passed_gates": ["candidate_is_not_baseline", "shadow_economics_reported"],
                            "gates": [
                                {"gate": "candidate_is_not_baseline", "passed": True, "evidence": "candidate_id=v28s_boundary_monotonic_time_safe_v001"},
                                {"gate": "holdout_coverage", "passed": True, "evidence": "rows=412 markets=24 required_rows=100 required_markets=20"},
                                {"gate": "shadow_economics_reported", "passed": True, "evidence": "shadow_net_pnl_cents=2800.0 shadow_expected_ev_cents=3050.0"},
                            ],
                        },
                        {
                            "candidate_id": "v28s_boundary_monotonic_time_safe_v001",
                            "variant": "seed_diagnostic",
                            "verdict": "blocked",
                            "model_hash": "def456",
                            "failed_gates": ["holdout_brier_better_than_v28"],
                            "passed_gates": ["candidate_is_not_baseline"],
                            "gates": [
                                {"gate": "candidate_is_not_baseline", "passed": True, "evidence": "candidate_id=v28s_boundary_monotonic_time_safe_v001"},
                                {"gate": "holdout_brier_better_than_v28", "passed": False, "evidence": "candidate=0.2 baseline=0.1"},
                            ],
                        },
                    ],
                    "summary": {},
                },
            )

            registry = build_registry(root, write=False)
            node_ids = {node.id for node in registry.nodes}

            self.assertIn("candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_logged_events_diagnostic", node_ids)
            self.assertIn("candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_seed_diagnostic", node_ids)
            logged = next(node for node in registry.nodes if node.id.endswith("logged_events_diagnostic"))
            seed = next(node for node in registry.nodes if node.id.endswith("seed_diagnostic"))
            self.assertEqual(logged.status, "strong_candidate")
            self.assertEqual(logged.metrics.get("net_pnl_unit_hint"), "cents")
            self.assertEqual(seed.status, "blocked")
            self.assertIn("promotion_verifier_gate_failed:holdout_brier_better_than_v28", seed.blockers)

    def test_candidate_readiness_adapter_updates_each_candidate_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "logs" / "particle_research" / "locked_oos_plans" / "paired_sidecar_slice_PSLICELOCK001_locked_plan.json",
                {"run_id": "PSLICELOCK001", "evaluation_scope": "locked_forward_shadow"},
            )
            write_json(
                root / "logs" / "project_os" / "candidate_readiness_reevaluation_latest.json",
                {
                    "schema": "project_os_candidate_readiness_reevaluation_v1",
                    "generated_at_utc": "2026-05-18T00:00:00Z",
                    "candidates": [
                        {
                            "node_id": "candidate:v28_successor:PSLICELOCK001",
                            "label": "PSLICELOCK001",
                            "family": "v28_successor",
                            "status_update": "needs_more_proof",
                            "evidence_level": "forward_shadow",
                            "readiness_level": "near_miss_review",
                            "readiness_score": 55,
                            "metrics_update": {
                                "readiness_rubric_version": "fixture",
                                "readiness_level": "near_miss_review",
                                "controlled_live_test_ready": False,
                            },
                            "blockers": ["readiness:baseline_or_calibration_failed"],
                            "next_action": "Fixture readiness action.",
                        }
                    ],
                },
            )

            registry = build_registry(root, write=False)
            candidate = next(node for node in registry.nodes if node.id == "candidate:v28_successor:PSLICELOCK001")

            self.assertEqual(candidate.status, "needs_more_proof")
            self.assertEqual(candidate.next_action, "Fixture readiness action.")
            self.assertEqual(candidate.metrics.get("readiness_level"), "near_miss_review")
            self.assertIn("candidate_readiness_reviewed", candidate.tags)


if __name__ == "__main__":
    unittest.main()
