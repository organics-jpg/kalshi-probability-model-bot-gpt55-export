from __future__ import annotations

import csv
import json
import math
import unittest
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fetch_v28_successor_sidecar_batch_settlement_labels as sidecar_label_fetcher
import build_v28_successor_public_rest_sidecar_batch as public_rest_batch_builder

from build_v28_successor_causal_dataset import (
    CALIBRATION_CSV,
    canonicalize_calibration_row,
    infer_decision_ts,
    parse_market_close_ts,
    build as build_seed_dataset,
)
from build_v28_successor_features import (
    build as build_features,
    has_leaky_token,
)
from train_v28_successor_candidates import (
    build as build_candidate_training,
    predict_fixed_logit_residual,
    predict_monotonic_tabular,
)
from replay_v28_successor_baselines import (
    build as build_baseline_replay_audit,
    normalize_v28_event,
)
from register_v28_successor_forward_predictions import build_registry_rows
from build_v28_successor_logged_event_dataset import event_to_row
from build_v28_successor_logged_event_features import build as build_logged_event_features
from train_v28_successor_logged_event_candidates import build as build_logged_event_candidate_training
from verify_v28_successor_promotion import build as build_promotion_verifier
from validate_v28_successor_source_contract import build as build_source_contract
from validate_v28_successor_source_contract import evaluate_forward_cleanliness
from replay_v28_successor_logged_event_api import build as build_logged_event_api_replay
from build_v28_successor_passive_forward_snapshots import build as build_passive_forward_snapshots
from preflight_v28_successor_forward_freeze import build as build_forward_freeze_preflight
from preflight_v28_successor_forward_freeze import row_blockers as forward_preflight_row_blockers
from freeze_v28_successor_forward_candidates import build as build_forward_freezer
from freeze_v28_successor_forward_candidates import FROZEN_FIELDS
from freeze_v28_successor_forward_candidates import row_freeze_blockers
from validate_v28_successor_forward_packet import build as build_forward_packet_contract
from build_v28_successor_shadow_forward_packets import build_rows as build_shadow_forward_packets
from score_v28_successor_forward_packets import (
    build as build_forward_packet_candidate_scoring,
    feature_row as build_forward_packet_feature_row,
)
from build_v28_successor_forward_collection_spec import build as build_forward_collection_spec
from build_v28_successor_forward_packet_adapter import (
    build_candidate_packet_rows as build_forward_packet_adapter_rows,
    build_demo as build_forward_packet_adapter_demo,
    collection_manifests as forward_packet_adapter_collection_manifests,
    demo_btc_history as forward_packet_adapter_demo_btc_history,
    demo_edge_batch as forward_packet_adapter_demo_edge_batch,
    demo_passive_row as forward_packet_adapter_demo_passive_row,
)
from build_v28_successor_public_rest_sidecar_bundle import (
    build as build_public_rest_sidecar_bundle,
    build_bundle_from_inputs as build_public_rest_bundle_from_inputs,
    fixture_payloads as public_rest_fixture_payloads,
)
from build_v28_successor_public_rest_sidecar_batch import (
    active_market_rows as public_rest_batch_active_market_rows,
    build as build_public_rest_sidecar_batch,
)
from replay_v28_successor_sidecar_bundles import build as build_sidecar_bundle_replay
from validate_v28_successor_forward_packet import FIELD_GROUPS, row_group_missing, row_temporal_blockers
from join_v28_successor_forward_labels import join_rows as join_forward_label_rows
from score_v28_successor_forward_evidence import score_rows as score_forward_evidence_rows
from score_v28_successor_sidecar_batch_evidence import build as build_sidecar_batch_evidence_score
from audit_v28_successor_forward_source_readiness import build as build_forward_source_readiness
from collect_v28_successor_forward_packets import (
    build_from_input_bundle as build_sidecar_packet_collector_from_input_bundle,
    build_demo as build_sidecar_packet_collector_demo,
    demo_market_and_checkpoint as sidecar_collector_demo_market_and_checkpoint,
    packet_rows_from_checkpoint as build_sidecar_packet_rows_from_checkpoint,
)
from validate_v28_successor_sidecar_input_bundle import (
    build as build_sidecar_input_bundle_contract,
    build_template_bundle as build_sidecar_input_bundle_template,
    validate_bundle as validate_sidecar_input_bundle,
)
from run_v28_successor_forward_packet_freeze import build as build_forward_packet_freeze_handoff
from run_v28_successor_sidecar_bundle_batch_handoff import build as build_sidecar_bundle_batch_handoff
from run_v28_successor_sidecar_batch_label_join_handoff import build as build_sidecar_batch_label_join_handoff
from run_v28_successor_sidecar_bundle_freeze_handoff import build as build_sidecar_bundle_freeze_handoff
from run_v28_successor_sidecar_collection_cycle import (
    RESEARCH_ONLY_GUARDRAILS as SIDECAR_CYCLE_GUARDRAILS,
    cycle_status as sidecar_cycle_status,
)
from stage_v28_successor_sidecar_forward_evidence import build as build_sidecar_forward_stage
from run_v28_successor_market_coverage_loop import (
    RESEARCH_ONLY_GUARDRAILS as MARKET_COVERAGE_LOOP_GUARDRAILS,
    run_loop as run_market_coverage_loop,
    summarize_candidate_forward_gates as summarize_market_coverage_candidate_gates,
    target_met as market_coverage_target_met,
)
from research_particle.paired_sidecar_spot_capture import (
    batch_report_for_alignment as paired_sidecar_batch_report_for_alignment,
    build_manifest as build_paired_sidecar_spot_manifest,
    build_sidecar_spot_alignment,
)
from research_particle.paired_sidecar_spot_enrichment import build_enriched_sidecar_spot_packets
from research_particle.paired_sidecar_spot_diagnostic import build_sidecar_spot_diagnostic
from research_particle.paired_sidecar_spot_aggregate import build_paired_sidecar_spot_aggregate
from research_particle.paired_sidecar_online_calibration import build_paired_sidecar_online_calibration
from research_particle.paired_sidecar_blend_failure_analysis import (
    build_paired_sidecar_blend_failure_analysis,
)
from research_particle.paired_sidecar_slice_locked_plan import (
    build_paired_sidecar_slice_locked_plan,
)
from research_particle.paired_sidecar_slice_oos import (
    PairedSidecarSliceGateConfig,
    evaluate_paired_sidecar_slice_oos,
)
from research_particle.paired_sidecar_slice_refresh import (
    _pending_manifest_status,
    refresh_paired_sidecar_slice_status,
)
from research_particle.paired_sidecar_slice_lock_comparison import (
    build_slice_lock_comparison,
    write_slice_lock_comparison,
)
from research_particle.paired_sidecar_slice_market_breakdown import (
    build_slice_market_breakdown,
    write_slice_market_breakdown,
)
from research_particle.paired_sidecar_slice_retirement import (
    build_slice_retirement_report,
    write_slice_retirement_report,
)
from research_particle.paired_sidecar_slice_stability import (
    build_slice_stability_report,
    write_slice_stability_report,
)
from research_particle.paired_sidecar_slice_trajectory import (
    build_slice_trajectory_report,
    write_slice_trajectory_report,
)
from research_particle.paired_sidecar_slice_promotion_readiness import (
    build_slice_promotion_readiness_report,
    write_slice_promotion_readiness_report,
)
from research_particle.paired_sidecar_spot_refresh import refresh_paired_sidecar_spot_evidence
from research_particle.spot_ticker_recorder import SpotTickerRecorderStatus
from audit_v28_successor_goal_completion import build_checklist as build_goal_completion_checklist
from run_v28_successor_research_pipeline import (
    KEY_ARTIFACTS,
    PIPELINE_STEPS,
    RESEARCH_ONLY_GUARDRAILS,
    build_plan,
    run_pipeline,
)


def expected_sidecar_packet_rows(markets: int = 1) -> int:
    return 2 * markets * len(forward_packet_adapter_collection_manifests())


class V28SuccessorPipelineTests(unittest.TestCase):
    def test_market_timestamp_parsing_and_decision_inference(self) -> None:
        close_ts = parse_market_close_ts("KXBTC15M-26MAY051415-15")

        self.assertEqual(close_ts, "2026-05-05T14:15:00Z")
        self.assertEqual(
            infer_decision_ts(close_ts, 221.567),
            "2026-05-05T14:11:18.433Z",
        )

    def test_no_side_row_recovers_yes_axis_probability_and_label(self) -> None:
        raw = {
            "source": "rejected_actionable",
            "market": "KXBTC15M-26MAY051415-15",
            "side": "no",
            "reason": "p_below_floor",
            "p_side": "0.003616",
            "outcome": "0.0",
            "seconds_to_close": "221.567",
            "actionable": "True",
        }

        row, rejection = canonicalize_calibration_row(raw, line_number=4, source_path=CALIBRATION_CSV)

        self.assertIsNone(rejection)
        self.assertIsNotNone(row)
        assert row is not None
        self.assertAlmostEqual(float(row["v28_p_yes"]), 0.996384)
        self.assertAlmostEqual(float(row["v28_p_no"]), 0.003616)
        self.assertEqual(float(row["y_yes_win"]), 1.0)
        self.assertFalse(row["allowed_for_forward_promotion"])

    def test_seed_dataset_smoke_build_is_diagnostic_not_promotion(self) -> None:
        rows, _sources, _rejections, summary = build_seed_dataset(limit_rows=25)

        self.assertEqual(len(rows), 25)
        self.assertEqual(len({row["row_id"] for row in rows}), 25)
        self.assertEqual(summary["eligibility_counts"]["forward_promotion"], 0)
        self.assertEqual(summary["missing_counts"]["decision_ts_utc"], 0)
        self.assertEqual(summary["missing_counts"]["v28_p_yes"], 0)
        self.assertEqual(summary["leakage_audit"]["status"], "pass_for_diagnostic_seed_not_promotion")

    def test_leakage_token_check_does_not_flag_window(self) -> None:
        self.assertFalse(has_leaky_token("late_window_lte_180s"))
        self.assertFalse(has_leaky_token("final_avg_effective_horizon_minutes"))
        self.assertTrue(has_leaky_token("settlement_price"))
        self.assertTrue(has_leaky_token("target_win_label"))

    def test_feature_manifest_excludes_labels_and_metrics(self) -> None:
        _rows, feature_rows, manifest, summary = build_features(limit_rows=25)
        feature_names = [row["feature_name"] for row in manifest]

        self.assertEqual(len(feature_rows), 25)
        self.assertEqual(summary["leakage_audit"]["status"], "pass")
        self.assertFalse(summary["leakage_audit"]["leaky_feature_names"])
        self.assertFalse(summary["leakage_audit"]["leaky_source_columns"])
        self.assertIn("final_avg_effective_horizon_minutes", feature_names)
        self.assertIn("final_avg_variance_compression", feature_names)
        self.assertIn("final_avg_abs_d_sigma_proxy", feature_names)
        self.assertNotIn("target_y_yes_win", feature_names)
        self.assertNotIn("target_brier_yes", feature_names)
        for row in feature_rows:
            for name in feature_names:
                value = float(row[name])
                self.assertTrue(math.isfinite(value), msg=f"{name} was not finite")

    def test_candidate_training_is_chronological_and_not_promotable(self) -> None:
        rows, predictions, manifests, _metrics, _bins, summary = build_candidate_training(limit_rows=180)
        feature_names = {row["feature_name"] for row in build_features(limit_rows=5)[2]}

        split_by_market: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            split_by_market[str(row["market_ticker"])].add(str(row["chronological_split"]))

        self.assertTrue(rows)
        self.assertTrue(predictions)
        self.assertEqual(summary["promotion_verdict"], "not_promotable")
        self.assertGreater(summary["split_summary"]["chronological_holdout"]["rows"], 0)
        self.assertTrue(all(len(splits) == 1 for splits in split_by_market.values()))
        self.assertEqual(len(predictions), len(rows) * len(manifests))

        for manifest in manifests:
            self.assertFalse(manifest["allowed_for_forward_registry"])
            if manifest["candidate_id"] != "v28_raw":
                self.assertTrue(manifest["allowed_for_forward_collection"])
                self.assertEqual(manifest["forward_collection_gate"]["status"], "allowed_for_shadow_forward_collection")
                gate = manifest["promotion_gate"]
                self.assertFalse(gate["promotable"])
                self.assertIn("no_post_lock_forward_rows", gate["fail_reasons"])
                self.assertIn("seed_rows_are_posthoc_diagnostic", gate["fail_reasons"])
            else:
                self.assertFalse(manifest["allowed_for_forward_collection"])
            for column in manifest["feature_columns"]:
                if column.startswith("target_"):
                    self.assertEqual(column, "target_v28_p_yes")
                else:
                    self.assertIn(column, feature_names)

        for prediction in predictions[:50]:
            p_yes = float(prediction["candidate_p_yes"])
            fair_yes = float(prediction["candidate_fair_yes_cents"])
            fair_no = float(prediction["candidate_fair_no_cents"])
            self.assertGreater(p_yes, 0.0)
            self.assertLess(p_yes, 1.0)
            self.assertAlmostEqual(fair_yes + fair_no, 100.0, places=6)

    def test_boundary_monotonic_candidate_tapers_to_raw_v28_away_from_boundary(self) -> None:
        model = {
            "bins": 2,
            "bucket_table": [
                {"monotonic_p_yes": 0.20},
                {"monotonic_p_yes": 0.80},
            ],
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "missing_distance_policy": "raw_v28",
            },
        }

        raw = 0.25
        near = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 0.5})
        mid = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 1.5})
        far = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 2.5})
        missing_distance = predict_monotonic_tabular(model, {"target_v28_p_yes": raw})

        self.assertLess(near, raw)
        self.assertLess(mid, raw)
        self.assertGreater(mid, near)
        self.assertAlmostEqual(far, raw, places=9)
        self.assertAlmostEqual(missing_distance, raw, places=9)

    def test_boundary_monotonic_candidate_honors_correction_scale(self) -> None:
        model = {
            "bins": 2,
            "bucket_table": [
                {"monotonic_p_yes": 0.20},
                {"monotonic_p_yes": 0.80},
            ],
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "correction_scale": 0.33,
            },
        }

        raw = 0.25
        full_model = dict(model)
        full_model["boundary_blend"] = {**model["boundary_blend"], "correction_scale": 1.0}
        scaled = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 0.5})
        full = predict_monotonic_tabular(full_model, {"target_v28_p_yes": raw, "abs_d_sigma": 0.5})

        self.assertAlmostEqual(scaled, raw + 0.33 * (full - raw), places=9)

    def test_boundary_monotonic_candidate_honors_time_gate(self) -> None:
        model = {
            "bins": 2,
            "bucket_table": [
                {"monotonic_p_yes": 0.20},
                {"monotonic_p_yes": 0.80},
            ],
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "correction_scale": 1.0,
                "time_gate": {
                    "seconds_to_close_feature": "seconds_to_close",
                    "zero_correction_seconds_lte": 240.0,
                    "full_correction_seconds_gte": 600.0,
                },
            },
        }

        raw = 0.25
        late = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 0.5, "seconds_to_close": 180.0})
        full = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 0.5, "seconds_to_close": 600.0})
        half = predict_monotonic_tabular(model, {"target_v28_p_yes": raw, "abs_d_sigma": 0.5, "seconds_to_close": 420.0})

        self.assertAlmostEqual(late, raw, places=9)
        self.assertLess(full, raw)
        self.assertAlmostEqual(half, raw + 0.5 * (full - raw), places=9)

    def test_fixed_logit_residual_candidate_applies_late_dsigma_gate(self) -> None:
        model = {
            "base_probability_feature": "target_v28_p_yes",
            "residual_terms": [{"feature": "d_sigma", "coefficient": -0.20}],
            "time_gate": {
                "seconds_to_close_feature": "seconds_to_close",
                "full_correction_seconds_lte": 240.0,
                "zero_correction_seconds_gte": 600.0,
                "missing_time_policy": "zero_correction",
            },
            "max_abs_logit_adjustment": 0.75,
        }

        raw = 0.80
        late_positive_d = predict_fixed_logit_residual(
            model,
            {"target_v28_p_yes": raw, "d_sigma": 2.0, "seconds_to_close": 120.0},
        )
        early_positive_d = predict_fixed_logit_residual(
            model,
            {"target_v28_p_yes": raw, "d_sigma": 2.0, "seconds_to_close": 700.0},
        )
        late_negative_d = predict_fixed_logit_residual(
            model,
            {"target_v28_p_yes": raw, "d_sigma": -2.0, "seconds_to_close": 120.0},
        )

        self.assertLess(late_positive_d, raw)
        self.assertAlmostEqual(early_positive_d, raw, places=9)
        self.assertGreater(late_negative_d, raw)

    def test_baseline_replay_audit_separates_logged_from_recomputed(self) -> None:
        event = normalize_v28_event(
            {
                "event_type": "mushroom_v28_approved",
                "ts_wall": "2026-05-05T12:00:00+00:00",
                "market": "KXBTC15M-26MAY051300-00",
                "mushroom_v28_side": "yes",
                "mushroom_v28_seconds_to_close": 600.0,
                "mushroom_v28_p_yes": 0.86,
                "mushroom_v28_p_side": 0.86,
                "mushroom_v28_fair_yes_cents": 86.0,
                "mushroom_v28_fair_no_cents": 14.0,
                "mushroom_v28_ask_cents": 81,
                "mushroom_v28_strike": 100000.0,
                "mushroom_v28_btc_price": 100100.0,
            },
            line_number=7,
        )

        self.assertIsNotNone(event)
        assert event is not None
        self.assertTrue(event["has_logged_v28_probability"])
        self.assertTrue(event["has_logged_v28_market_state"])
        self.assertFalse(event["true_api_recompute_ready"])
        self.assertIn("missing_serialized_v28_engine_transport_state", event["api_recompute_blockers"])

        seed_rows, replay_rows, summary = build_baseline_replay_audit(limit_rows=10, limit_events=500)
        self.assertEqual(len(seed_rows), 10)
        self.assertEqual(len(replay_rows), 10)
        self.assertEqual(summary["baseline_replay_verdict"], "logged_baseline_audited_true_api_recompute_blocked")
        self.assertEqual(summary["seed_forward_promotion_rows"], 0)
        self.assertEqual(summary["missing_seed_fields"]["strike"], 10)

    def test_forward_registry_stays_empty_without_forward_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            rows, summary = build_registry_rows(frozen_csv=Path(temp_dir) / "missing_frozen.csv")

        self.assertEqual(rows, [])
        self.assertEqual(summary["feature_forward_row_ids"], 0)
        self.assertEqual(summary["registry_status"], "active_empty_no_forward_rows")
        self.assertFalse(summary["promotion_ready"])
        self.assertIn("frozen forward prediction ledger is empty", summary["blockers"])

    def test_logged_event_row_uses_event_clock_for_pre_resolution(self) -> None:
        row = event_to_row(
            {
                "event_source_file": "logs/live_mushroom_v28_size2/execution_events.ndjson",
                "event_line": 99,
                "event_type": "mushroom_v28_approved",
                "event_ts_wall": "2026-05-05T20:07:17.198Z",
                "market_ticker": "KXBTC15M-26MAY051615-15",
                "side": "no",
                "logged_seconds_to_close": 462.817,
                "logged_p_yes": 0.121282,
                "logged_p_side": 0.878718,
                "logged_fair_yes_cents": 12.1282,
                "logged_fair_no_cents": 87.8718,
                "logged_fair_side_cents": 87.8718,
                "logged_ask_cents": 79,
                "logged_edge_cents": 5.37,
                "logged_sigma_t_dollars": 93.99,
                "logged_d_sigma": 0.96,
                "logged_abs_d_sigma": 0.96,
                "logged_arrow": 0.09,
                "logged_strike": 81612.38,
                "logged_btc_price": 81521.98,
                "logged_btc_age_ms": 15.0,
                "logged_book_age_ms": 375.0,
                "logged_feed_age_ms": 694.5,
                "logged_history_bars": 1878,
                "v28_status": "ok",
                "v28_version": "v0.28_fast_fv",
                "v28_approved": True,
            },
            y_yes=1.0,
        )

        self.assertEqual(row["market_close_ts_utc"], "2026-05-05T20:15:00.015Z")
        self.assertTrue(row["is_pre_resolution"])
        self.assertEqual(row["strike_source"], "logged_mushroom_v28_strike")
        self.assertFalse(row["allowed_for_forward_promotion"])

    def test_logged_event_features_and_candidates_use_true_boundary_but_stay_blocked(self) -> None:
        _rows, feature_rows, manifest, summary = build_logged_event_features(limit_rows=120)
        feature_names = {row["feature_name"] for row in manifest}

        self.assertEqual(len(feature_rows), 120)
        self.assertEqual(summary["leakage_audit"]["status"], "pass")
        self.assertIn("abs_d_sigma", feature_names)
        self.assertIn("freshness_max_age_ms", feature_names)
        self.assertIn("v28_book_disagreement_abs", feature_names)
        self.assertIn("prior_adverse_path_memory_dollars", feature_names)
        self.assertIn("btc_drift_from_prev_event_dollars", feature_names)
        self.assertIn("final_avg_effective_horizon_minutes", feature_names)
        self.assertIn("final_avg_uncertainty_scale", feature_names)
        self.assertIn("final_avg_abs_d_sigma_proxy", feature_names)
        self.assertIn("v28_api_replay_p_anchor", feature_names)
        self.assertIn("v28_api_replay_p_static_boundary_field", feature_names)
        self.assertIn("v28_api_replay_p_recent_transport", feature_names)
        self.assertIn("log1p_v28_api_replay_transport_recent_n", feature_names)
        self.assertIn("v28_api_replay_abs_p_delta", feature_names)
        self.assertEqual(summary["api_replay_join"]["feature_rows_with_api_replay"], 120)
        self.assertEqual(summary["eligibility_counts"]["forward_promotion"], 0)
        self.assertTrue(any(float(row["abs_d_sigma"]) >= 0.0 for row in feature_rows))
        self.assertTrue(all(float(row["prior_adverse_path_memory_dollars"]) >= 0.0 for row in feature_rows))
        self.assertTrue(all(float(row["v28_api_replay_available"]) == 1.0 for row in feature_rows))

        rows, predictions, manifests, metrics, _bins, train_summary = build_logged_event_candidate_training(limit_rows=240)
        self.assertEqual(train_summary["promotion_verdict"], "not_promotable")
        self.assertEqual(train_summary["split_summary"]["post_freeze_forward"]["rows"], 0)
        self.assertTrue(predictions)
        self.assertEqual(len(predictions), len(rows) * len(manifests))

        true_boundary_metrics = [
            row
            for row in metrics
            if row["candidate_id"] == "v28_raw"
            and row["split"] == "chronological_holdout"
            and row["slice"] == "near_boundary_abs_d_lte_1"
        ]
        self.assertEqual(len(true_boundary_metrics), 1)
        self.assertGreater(true_boundary_metrics[0]["rows"], 0)
        for manifest_row in manifests:
            self.assertFalse(manifest_row["allowed_for_forward_registry"])
            if manifest_row["candidate_id"] != "v28_raw":
                self.assertTrue(manifest_row["allowed_for_forward_collection"])
                self.assertIn("no_post_lock_forward_rows", manifest_row["promotion_gate"]["fail_reasons"])
                self.assertIn("source_rows_are_diagnostic_not_forward_registered", manifest_row["promotion_gate"]["fail_reasons"])
            if manifest_row["candidate_id"] == "v28s_logistic_boundary_physics_v001":
                self.assertIn("final_avg_effective_horizon_minutes", manifest_row["feature_columns"])
                self.assertIn("final_avg_abs_d_sigma_proxy", manifest_row["feature_columns"])
            if manifest_row["candidate_id"] == "v28s_boundary_monotonic_micro_time_safe_v001":
                self.assertEqual(manifest_row["model_parameters"]["boundary_blend"]["correction_scale"], 0.03)
                self.assertIn("seconds_to_close", manifest_row["feature_columns"])
            if manifest_row["candidate_id"] == "v28s_late_dsigma_residual_tilt_v001":
                self.assertEqual(manifest_row["model_type"], "fixed_logit_residual")
                self.assertEqual(manifest_row["model_parameters"]["residual_terms"][0]["coefficient"], -0.20)
                self.assertEqual(manifest_row["model_parameters"]["time_gate"]["full_correction_seconds_lte"], 240.0)

    def test_promotion_verifier_blocks_all_diagnostic_candidates(self) -> None:
        evaluations, summary = build_promotion_verifier()

        self.assertIn(summary["overall_verdict"], {"blocked", "promotable"})
        self.assertEqual(summary["candidate_count"], 20)
        self.assertEqual(summary["candidate_count"], len(evaluations))
        self.assertEqual(summary["blocked_candidate_count"], sum(row["verdict"] == "blocked" for row in evaluations))
        self.assertEqual(len(summary["promotable_candidates"]), sum(row["verdict"] == "promotable" for row in evaluations))
        self.assertNotIn("source_quality_forward_registered", summary["hard_blockers"])
        self.assertNotIn("candidate_manifest_frozen_and_inspectable", summary["hard_blockers"])
        self.assertTrue(evaluations)
        if summary["overall_verdict"] == "blocked":
            self.assertEqual(summary["promotable_candidates"], [])
            self.assertIn("forward_evidence_scored_and_promotable", summary["hard_blockers"])
            self.assertTrue(all(row["verdict"] == "blocked" for row in evaluations))
        else:
            self.assertTrue(summary["promotable_candidates"])
            self.assertEqual(summary["hard_blockers"], [])
            self.assertTrue(all(not row["failed_gates"] for row in summary["promotable_candidates"]))
        source_contract_expected_pass = "source_contract_promotion_ready" not in summary["hard_blockers"]
        for row in evaluations:
            by_gate = {gate["gate"]: gate for gate in row["gates"]}
            self.assertIn("source_contract_promotion_ready", by_gate)
            self.assertEqual(by_gate["source_contract_promotion_ready"]["passed"], source_contract_expected_pass)
            self.assertIn("source_quality_forward_registered", by_gate)
            self.assertTrue(by_gate["source_quality_forward_registered"]["passed"])
            self.assertIn("candidate_manifest_frozen_and_inspectable", by_gate)
            self.assertEqual(
                by_gate["candidate_manifest_frozen_and_inspectable"]["passed"],
                row["candidate_id"] != "v28_raw",
            )

    def test_logged_event_api_replay_regenerates_v28_components_without_promotion(self) -> None:
        rows, summary = build_logged_event_api_replay(limit_rows=20)

        self.assertEqual(summary["replay_verdict"], "research_reconstructed_v28_api_replay_available_not_promotion")
        self.assertEqual(summary["row_count"], 20)
        self.assertEqual(summary["replayed_rows"], 20)
        self.assertEqual(summary["blocked_rows"], 0)
        self.assertFalse(summary["promotion_status"]["allowed_for_forward_promotion"])
        self.assertEqual(summary["component_coverage"]["replay_p_anchor"], 20)
        self.assertEqual(summary["component_coverage"]["replay_p_static_boundary_field"], 20)
        self.assertEqual(summary["component_coverage"]["replay_p_recent_transport"], 20)
        self.assertGreater(summary["delta_summary"]["p_yes"]["count"], 0)
        self.assertTrue(rows)
        for row in rows[:5]:
            self.assertEqual(row["replay_status"], "replayed_v28_api_from_predecision_btc_cache")
            self.assertFalse(row["allowed_for_forward_promotion"])
            self.assertIsNotNone(row["replay_p_anchor"])
            self.assertIsNotNone(row["replay_transport_recent_n"])

    def test_passive_forward_snapshots_stage_book_rows_without_promotion(self) -> None:
        rows, summary = build_passive_forward_snapshots(limit_checkpoints=3)

        self.assertEqual(summary["snapshot_status"], "staging_not_promotable")
        self.assertEqual(summary["checkpoint_count"], 3)
        self.assertEqual(summary["row_count"], 6)
        self.assertEqual(summary["forward_promotion_rows"], 0)
        self.assertEqual(summary["missing_counts"]["btc_state"], 6)
        self.assertEqual(summary["missing_counts"]["v28_baseline"], 6)
        self.assertEqual(summary["missing_counts"]["candidate_prediction"], 6)
        self.assertEqual(summary["missing_counts"]["settlement_label"], 6)
        self.assertTrue(rows)
        self.assertEqual({row["side"] for row in rows}, {"yes", "no"})
        self.assertTrue(all(row["is_pre_resolution"] for row in rows))
        self.assertTrue(all(not row["allowed_for_forward_promotion"] for row in rows))
        self.assertTrue(all("missing_btc_state" in row["exclusion_reason"] for row in rows))

    def test_forward_freeze_preflight_blocks_unenriched_passive_rows(self) -> None:
        evaluations, summary = build_forward_freeze_preflight()

        self.assertEqual(summary["preflight_status"], "blocked")
        self.assertGreater(summary["passive_rows"], 0)
        self.assertEqual(summary["freeze_ready_rows"], 0)
        self.assertEqual(summary["freeze_ready_markets"], 0)
        self.assertIn("missing_btc_state", summary["readiness_blockers"])
        self.assertIn("missing_v28_baseline", summary["readiness_blockers"])
        self.assertIn("missing_candidate_prediction", summary["readiness_blockers"])
        self.assertGreater(summary["forward_collection_candidate_count"], 0)
        self.assertNotIn("no_candidate_manifest_allowed_for_forward_collection", summary["readiness_blockers"])
        self.assertNotIn("forward_registry_empty", summary["readiness_blockers"])
        self.assertTrue(evaluations)
        self.assertTrue(all(not row["freeze_ready"] for row in evaluations))

    def test_forward_packet_contract_blocks_passive_rows_missing_btc_v28_and_candidates(self) -> None:
        evaluations, summary, template = build_forward_packet_contract(limit_rows=12)

        self.assertEqual(summary["packet_status"], "blocked")
        self.assertEqual(summary["input_rows"], 12)
        self.assertEqual(summary["packet_ready_rows"], 0)
        self.assertIn("btc_and_feed", template["field_groups"])
        self.assertIn("v28_baseline", template["field_groups"])
        self.assertIn("candidate_prediction", template["field_groups"])
        self.assertEqual(summary["group_missing_counts"]["btc_and_feed"], 12)
        self.assertEqual(summary["group_missing_counts"]["v28_baseline"], 12)
        self.assertEqual(summary["group_missing_counts"]["candidate_prediction"], 12)
        self.assertTrue(evaluations)
        self.assertTrue(all(not row["packet_ready"] for row in evaluations))

    def test_shadow_forward_packets_bridge_captures_but_do_not_promote(self) -> None:
        packet_rows, labeled_rows, summary = build_shadow_forward_packets(limit_snapshots=5)

        self.assertEqual(summary["packet_rows"], 10)
        self.assertEqual(summary["labeled_rows"], 10)
        self.assertEqual(summary["forward_promotion_rows"], 0)
        self.assertEqual(summary["packet_ready_rows"], 0)
        self.assertEqual(summary["group_missing_counts"]["identity_and_clock"], 0)
        self.assertEqual(summary["group_missing_counts"]["causality"], 0)
        self.assertEqual(summary["group_missing_counts"]["market_and_book"], 0)
        self.assertEqual(summary["group_missing_counts"]["candidate_prediction"], 0)
        self.assertEqual(summary["group_missing_counts"]["v28_baseline"], 10)
        self.assertTrue(packet_rows)
        self.assertEqual({row["side"] for row in packet_rows}, {"yes", "no"})
        self.assertTrue(all(row["allowed_for_forward_promotion"] == "False" for row in packet_rows))
        self.assertTrue(all("native_v28_component_fields_incomplete" in row["exclusion_reason"] for row in packet_rows))
        self.assertTrue(all(row["candidate_id"] == "shadow_particle_calibrated_v001" for row in packet_rows))
        self.assertTrue(all(row["y_yes_win"] in {"0", "1"} for row in labeled_rows))

    def test_forward_packet_candidate_scoring_applies_collection_manifests_without_freeze(self) -> None:
        predictions, summary = build_forward_packet_candidate_scoring(limit_rows=3)
        scorer_features = build_forward_packet_feature_row(
            {
                "seconds_to_close": "45",
                "v28_sigma_t_dollars": "90",
                "strike": "100100",
                "btc_spot": "100000",
                "v28_p_yes": "0.52",
            }
        )

        self.assertEqual(summary["packet_rows"], 3)
        self.assertEqual(summary["candidate_count"], 9)
        self.assertEqual(summary["prediction_rows"], 27)
        self.assertEqual(summary["freeze_eligible_prediction_rows"], 0)
        self.assertEqual(summary["promotion_allowed_rows"], 0)
        self.assertEqual(summary["status_counts"], {"diagnostic_scored_not_freeze_ready": 27})
        self.assertTrue(predictions)
        self.assertTrue(all(row["allowed_for_forward_collection"] == "True" for row in predictions))
        self.assertTrue(all(row["allowed_for_forward_registry"] == "False" for row in predictions))
        self.assertTrue(all(row["promotion_allowed"] == "False" for row in predictions))
        self.assertTrue(all(row["eligible_for_forward_freeze"] == "False" for row in predictions))
        self.assertIn("final_avg_effective_horizon_minutes", scorer_features)
        self.assertLess(float(scorer_features["final_avg_uncertainty_scale"]), 1.0)

    def test_forward_packet_adapter_demo_builds_contract_ready_sidecar_rows(self) -> None:
        rows, summary = build_forward_packet_adapter_demo()

        self.assertEqual(summary["adapter_status"], "contract_demo_ready")
        self.assertGreater(summary["candidate_count"], 0)
        self.assertEqual(summary["demo_rows"], summary["candidate_count"])
        self.assertEqual(summary["demo_packet_ready_rows"], summary["demo_rows"])
        self.assertFalse(summary["promotion_status"]["allowed"])
        self.assertTrue(rows)
        self.assertTrue(all(row["allowed_for_forward_promotion"] == "False" for row in rows))
        self.assertTrue(all(row["is_simulated"] == "True" for row in rows))
        self.assertTrue(all(row["has_btc_state"] == "True" for row in rows))
        self.assertTrue(all(row["has_v28_baseline"] == "True" for row in rows))
        self.assertTrue(all(row["has_candidate_prediction"] == "True" for row in rows))
        for row in rows:
            self.assertFalse(row_temporal_blockers(row))
            for group in FIELD_GROUPS:
                self.assertEqual(row_group_missing(row, group), [], msg=f"{group} missing in adapter demo row")
        now_before_demo_close = datetime(2026, 5, 11, 11, 59, tzinfo=timezone.utc)
        freezer_blockers = row_freeze_blockers(rows[0], now_before_demo_close, [{"candidate_id": "fixture"}])
        preflight_blockers = forward_preflight_row_blockers(rows[0], now_before_demo_close, True)
        self.assertIn("simulated_row_not_freezable", freezer_blockers)
        self.assertIn("diagnostic_row_not_freezable", freezer_blockers)
        self.assertIn("simulated_row_not_freezable", preflight_blockers)
        self.assertIn("diagnostic_row_not_freezable", preflight_blockers)

    def test_forward_packet_adapter_real_sidecar_shape_is_freezable_before_close(self) -> None:
        manifest = forward_packet_adapter_collection_manifests()[0]
        passive = forward_packet_adapter_demo_passive_row()
        passive["is_simulated"] = "False"
        passive["is_diagnostic_only"] = "False"
        passive["exclusion_reason"] = "missing_btc_state;missing_v28_baseline;missing_candidate_prediction"
        rows = build_forward_packet_adapter_rows(
            passive,
            btc_history_rows=forward_packet_adapter_demo_btc_history(),
            edge_batch=forward_packet_adapter_demo_edge_batch(),
            candidate_manifests=[manifest],
        )
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["has_btc_state"], "True")
        self.assertEqual(row["has_v28_baseline"], "True")
        self.assertEqual(row["has_candidate_prediction"], "True")
        self.assertEqual(row["has_settlement_label"], "False")
        self.assertEqual(row["is_simulated"], "False")
        self.assertEqual(row["is_diagnostic_only"], "False")
        self.assertEqual(row["exclusion_reason"], "not_frozen_candidate_prediction_registry")
        self.assertFalse(row_temporal_blockers(row))
        for group in FIELD_GROUPS:
            self.assertEqual(row_group_missing(row, group), [], msg=f"{group} missing in adapter row")
        self.assertEqual(row_freeze_blockers(row, now_before_close, [manifest]), [])
        self.assertEqual(forward_preflight_row_blockers(row, now_before_close, True), [])
        with TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "real_sidecar_packet.csv"
            with source_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
                writer.writeheader()
                writer.writerow(row)
            evaluations, packet_summary, _template = build_forward_packet_contract(source_csv=source_csv)

        self.assertEqual(packet_summary["packet_status"], "ready")
        self.assertEqual(packet_summary["packet_ready_rows"], 1)
        self.assertEqual(packet_summary["packet_ready_markets"], 1)
        self.assertEqual(evaluations[0]["packet_ready"], True)

    def test_sidecar_packet_collector_demo_is_contract_ready_not_evidence(self) -> None:
        rows, summary = build_sidecar_packet_collector_demo()

        self.assertEqual(summary["collector_status"], "contract_demo_ready_not_evidence")
        self.assertIn("input_bundle_json", summary["input_modes"])
        self.assertEqual(summary["demo_packet_ready_rows"], summary["demo_rows"])
        self.assertGreater(summary["demo_rows"], 0)
        self.assertFalse(summary["promotion_status"]["allowed"])
        self.assertTrue(rows)
        self.assertTrue(all(row["is_simulated"] == "True" for row in rows))
        self.assertTrue(all(row["is_diagnostic_only"] == "True" for row in rows))
        self.assertEqual({row["side"] for row in rows}, {"yes", "no"})
        for row in rows:
            self.assertFalse(row_temporal_blockers(row))
            for group in FIELD_GROUPS:
                self.assertEqual(row_group_missing(row, group), [], msg=f"{group} missing in collector demo row")

    def test_sidecar_packet_collector_input_bundle_builds_real_packet_csv_rows(self) -> None:
        manifest = forward_packet_adapter_collection_manifests()[0]
        market, checkpoint, registered_utc = sidecar_collector_demo_market_and_checkpoint()
        bundle = {
            "registered_utc": registered_utc,
            "market": market,
            "checkpoint": checkpoint,
            "btc_history_rows": forward_packet_adapter_demo_btc_history(),
            "candidate_manifests": [manifest],
            "edge_batch": {
                "p_yes": [0.571],
                "p_no": [0.429],
                "fair_yes_cents": [57.1],
                "fair_no_cents": [42.9],
                "yes_net_edge_cents": [2.1],
                "no_net_edge_cents": [-5.1],
                "best_side": ["yes"],
                "best_edge_cents": [2.1],
                "best_fair_cents": [57.1],
                "side_probability": [0.571],
                "components": {
                    "p_anchor": [0.552],
                    "p_static_boundary_field": [0.558],
                    "p_recent_transport": [0.568],
                    "p_long_transport": [0.561],
                    "edge_gate": [0.52],
                    "static_gate": [0.91],
                    "arrow": 0.04,
                    "volshock": 0.12,
                    "transport_recent_n": 320.0,
                    "transport_long_n": 2100.0,
                    "learned_horizon_minutes": 10.0,
                    "effective_horizon_minutes": 10.0,
                    "sigma_t_dollars": 115.0,
                    "d_sigma": [-0.1739130435],
                },
            },
        }

        with TemporaryDirectory() as temp_dir:
            input_json = Path(temp_dir) / "sidecar_input_bundle.json"
            input_json.write_text(json.dumps(bundle), encoding="utf-8")
            rows, summary = build_sidecar_packet_collector_from_input_bundle(input_json=input_json)

        self.assertEqual(summary["collector_mode"], "input_bundle")
        self.assertEqual(summary["collector_status"], "input_bundle_packet_ready_for_freeze_handoff")
        self.assertEqual(summary["packet_ready_rows"], 2)
        self.assertEqual(summary["rows"], 2)
        self.assertFalse(summary["promotion_status"]["allowed"])
        self.assertEqual({row["side"] for row in rows}, {"yes", "no"})
        self.assertTrue(all(row["is_simulated"] == "False" for row in rows))
        self.assertTrue(all(row["is_diagnostic_only"] == "False" for row in rows))
        self.assertTrue(all(row["has_candidate_prediction"] == "True" for row in rows))
        for row in rows:
            self.assertFalse(row_temporal_blockers(row))
            for group in FIELD_GROUPS:
                self.assertEqual(row_group_missing(row, group), [], msg=f"{group} missing in input-bundle collector row")

    def test_sidecar_input_bundle_contract_template_is_ready_but_not_evidence(self) -> None:
        report, bundle = build_sidecar_input_bundle_contract()
        summary = report["summary"]

        self.assertEqual(summary["bundle_status"], "contract_demo_ready_not_evidence")
        self.assertTrue(summary["bundle_ready"])
        self.assertFalse(summary["promotion_allowed"])
        self.assertTrue(bundle["simulated"])
        self.assertTrue(bundle["diagnostic_only"])
        self.assertGreater(summary["btc_history_rows"], 0)
        self.assertGreater(summary["forward_collection_candidate_count"], 0)
        self.assertEqual(summary["blocker_counts"], {})

    def test_sidecar_input_bundle_contract_blocks_future_ticks_and_labels(self) -> None:
        bundle = build_sidecar_input_bundle_template()
        bundle["simulated"] = False
        bundle["diagnostic_only"] = False
        bundle["settlement_price"] = "100100"
        bundle["btc_history_rows"].append({"ts_utc": "2026-05-11T12:00:01Z", "price": 100030.0})

        _details, summary = validate_sidecar_input_bundle(bundle)

        self.assertEqual(summary["bundle_status"], "blocked")
        self.assertFalse(summary["bundle_ready"])
        self.assertIn("btc_tick_after_checkpoint", summary["blocker_counts"])
        self.assertIn("forbidden_pre_freeze_field_present", summary["blocker_counts"])
        self.assertFalse(summary["promotion_allowed"])

    def test_sidecar_input_bundle_contract_rejects_non_btc15m_market_family(self) -> None:
        bundle = build_sidecar_input_bundle_template()
        bundle["market"]["market_ticker"] = "KXBTC-26MAY1106-T89799.99"
        bundle["checkpoint"]["market_ticker"] = "KXBTC-26MAY1106-T89799.99"

        _details, summary = validate_sidecar_input_bundle(bundle)

        self.assertEqual(summary["bundle_status"], "blocked")
        self.assertFalse(summary["bundle_ready"])
        self.assertIn("market_not_btc15m_boundary", summary["blocker_counts"])

    def test_public_rest_sidecar_bundle_fixture_is_contract_ready_not_evidence(self) -> None:
        report, bundle = build_public_rest_sidecar_bundle()
        summary = report["summary"]
        details, contract_summary = validate_sidecar_input_bundle(bundle)

        self.assertEqual(summary["mode"], "fixture")
        self.assertEqual(summary["bundle_status"], "contract_demo_ready_not_evidence")
        self.assertTrue(summary["bundle_ready"])
        self.assertFalse(summary["promotion_allowed"])
        self.assertEqual(summary["packet_rows"], expected_sidecar_packet_rows())
        self.assertEqual(contract_summary["bundle_status"], "contract_demo_ready_not_evidence")
        self.assertTrue(details)

    def test_public_rest_sidecar_bundle_builder_creates_real_ready_bundle_from_payloads(self) -> None:
        market_payload, orderbook_payload, candle_payload, now_utc = public_rest_fixture_payloads()
        market_payload = dict(market_payload)
        market_payload["strike_source"] = "previous_market_expiration_value_official_public_rest"
        market_payload["strike_source_market_ticker"] = "KXBTC15M-26MAY111345-45"
        market_payload["strike_source_market_status"] = "finalized"
        bundle = build_public_rest_bundle_from_inputs(
            market_payload=market_payload,
            orderbook_payload=orderbook_payload,
            candle_payload=candle_payload,
            now_utc=now_utc,
            simulated=False,
            diagnostic_only=False,
        )
        _details, summary = validate_sidecar_input_bundle(bundle)

        self.assertEqual(summary["bundle_status"], "input_bundle_ready_for_collection")
        self.assertTrue(summary["bundle_ready"])
        self.assertFalse(summary["promotion_allowed"])
        self.assertFalse(bundle["simulated"])
        self.assertFalse(bundle["diagnostic_only"])
        self.assertEqual(summary["btc_history_rows"], 240)
        self.assertEqual(bundle["market"]["strike_source"], "previous_market_expiration_value_official_public_rest")
        self.assertEqual(bundle["market"]["strike_source_market_ticker"], "KXBTC15M-26MAY111345-45")

    def test_sidecar_bundle_replay_recomputes_recorded_v28_edge_batch(self) -> None:
        market_payload, orderbook_payload, candle_payload, now_utc = public_rest_fixture_payloads()
        bundle = build_public_rest_bundle_from_inputs(
            market_payload=market_payload,
            orderbook_payload=orderbook_payload,
            candle_payload=candle_payload,
            now_utc=now_utc,
            simulated=False,
            diagnostic_only=False,
        )

        with TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / "bundle.json"
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            rows, summary = build_sidecar_bundle_replay(input_jsons=[bundle_path])

        self.assertEqual(summary["replay_status"], "pass")
        self.assertEqual(summary["bundle_count"], 1)
        self.assertEqual(summary["replayed_bundle_count"], 1)
        self.assertEqual(rows[0]["status"], "pass")
        self.assertLessEqual(float(rows[0]["max_abs_delta"]), float(summary["tolerance"]))

    def test_public_rest_sidecar_batch_fixture_is_contract_ready_not_evidence(self) -> None:
        report, bundles = build_public_rest_sidecar_batch()
        summary = report["summary"]

        self.assertEqual(summary["mode"], "fixture")
        self.assertEqual(summary["batch_status"], "contract_demo_ready_not_evidence")
        self.assertEqual(summary["markets_selected"], 2)
        self.assertEqual(summary["bundle_ready_files"], 2)
        self.assertEqual(summary["packet_rows"], expected_sidecar_packet_rows(markets=2))
        self.assertEqual(summary["packet_markets"], 2)
        self.assertFalse(summary["promotion_allowed"])
        self.assertEqual(len(bundles), 2)
        self.assertTrue(all(item["bundle"]["simulated"] for item in bundles))
        self.assertTrue(all(item["bundle"]["diagnostic_only"] for item in bundles))

    def test_public_rest_sidecar_batch_selects_nearest_close_boundary_markets(self) -> None:
        now_utc = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        payload = {
            "markets": [
                {"ticker": "KXBTC15M-26MAY111210-100500", "close_time": "2026-05-11T12:10:00Z", "strike": 100500},
                {"ticker": "KXBTC15M-26MAY111210-100000", "close_time": "2026-05-11T12:10:00Z", "strike": 100000},
                {"ticker": "KXBTC15M-26MAY111225-100000", "close_time": "2026-05-11T12:25:00Z", "strike": 100000},
                {"ticker": "KXBTC-26MAY111210-T100000", "close_time": "2026-05-11T12:10:00Z", "strike": 100000},
                {"ticker": "KXBTC15M-26MAY111155-99999", "close_time": "2026-05-11T11:55:00Z", "strike": 99999},
            ]
        }

        selected = public_rest_batch_active_market_rows(payload, now_utc=now_utc)

        self.assertEqual(
            [row["ticker"] for row in selected],
            ["KXBTC15M-26MAY111210-100000", "KXBTC15M-26MAY111210-100500"],
        )

    def test_public_rest_sidecar_batch_blocks_expired_market_at_bundle_build(self) -> None:
        now_utc = datetime(2026, 5, 11, 12, 11, tzinfo=timezone.utc)
        report, bundles = public_rest_batch_builder.build_bundles_from_inputs(
            market_payloads=[
                {"ticker": "KXBTC15M-26MAY111210-100000", "close_time": "2026-05-11T12:10:00Z", "strike": 100000},
            ],
            orderbooks_by_ticker={"KXBTC15M-26MAY111210-100000": {"yes": [[50, 10]], "no": [[49, 10]]}},
            candle_payload=[],
            now_utc=now_utc,
            simulated=False,
            diagnostic_only=False,
            mode="public_rest",
        )

        self.assertEqual(report["summary"]["markets_selected"], 1)
        self.assertEqual(report["summary"]["packet_rows"], 0)
        self.assertEqual(report["summary"]["blocker_counts"]["market_not_preclose_at_collection"], 1)
        self.assertFalse(report["markets"][0]["bundle_ready"])
        self.assertEqual(bundles, [])

    def test_public_rest_sidecar_batch_all_open_closes_combines_status_buckets(self) -> None:
        now_utc = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        original_get_json = public_rest_batch_builder.get_json
        calls: list[str | None] = []

        def fake_get_json(base_url: str, endpoint: str, params=None, *, timeout_seconds: float = 10.0):
            self.assertEqual(endpoint, "/markets")
            status = (params or {}).get("status")
            calls.append(status)
            markets_by_status = {
                "active": [
                    {"ticker": "KXBTC15M-26MAY111210-100000", "close_time": "2026-05-11T12:10:00Z", "strike": 100000},
                ],
                "initialized": [
                    {"ticker": "KXBTC15M-26MAY111225-100000", "close_time": "2026-05-11T12:25:00Z", "strike": 100000},
                ],
            }
            return {"markets": markets_by_status.get(status, [])}

        try:
            public_rest_batch_builder.get_json = fake_get_json
            selected = public_rest_batch_builder.fetch_active_markets(
                kalshi_base_url="https://unit.test",
                series_ticker="KXBTC15M",
                now_utc=now_utc,
                timeout_seconds=3.0,
                nearest_close_only=False,
                max_markets=80,
            )
        finally:
            public_rest_batch_builder.get_json = original_get_json

        self.assertIn("active", calls)
        self.assertIn("initialized", calls)
        self.assertEqual(
            [row["ticker"] for row in selected],
            ["KXBTC15M-26MAY111210-100000", "KXBTC15M-26MAY111225-100000"],
        )

    def test_public_rest_sidecar_batch_retries_market_list_429(self) -> None:
        now_utc = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        original_get_json = public_rest_batch_builder.get_json
        original_sleep = public_rest_batch_builder.time.sleep
        calls: list[str | None] = []
        sleeps: list[float] = []

        def fake_get_json(base_url: str, endpoint: str, params=None, *, timeout_seconds: float = 10.0):
            self.assertEqual(endpoint, "/markets")
            calls.append((params or {}).get("status"))
            if len(calls) == 1:
                raise public_rest_batch_builder.urllib.error.HTTPError(
                    url="https://unit.test/markets",
                    code=429,
                    msg="Too Many Requests",
                    hdrs=None,
                    fp=None,
                )
            return {
                "markets": [
                    {
                        "ticker": "KXBTC15M-26MAY111210-100000",
                        "close_time": "2026-05-11T12:10:00Z",
                        "strike": 100000,
                    }
                ]
            }

        try:
            public_rest_batch_builder.get_json = fake_get_json
            public_rest_batch_builder.time.sleep = lambda seconds: sleeps.append(seconds)
            selected = public_rest_batch_builder.fetch_active_markets(
                kalshi_base_url="https://unit.test",
                series_ticker="KXBTC15M",
                now_utc=now_utc,
                timeout_seconds=3.0,
                nearest_close_only=True,
                max_markets=80,
            )
        finally:
            public_rest_batch_builder.get_json = original_get_json
            public_rest_batch_builder.time.sleep = original_sleep

        self.assertEqual(calls[:2], ["active", "active"])
        self.assertEqual(sleeps, [public_rest_batch_builder.RETRY_429_SLEEP_SECONDS])
        self.assertEqual([row["ticker"] for row in selected], ["KXBTC15M-26MAY111210-100000"])

    def test_public_rest_sidecar_batch_uses_previous_official_expiration_for_tbd_up_market(self) -> None:
        now_utc = datetime(2026, 5, 11, 17, 55, tzinfo=timezone.utc)
        market = {
            "ticker": "KXBTC15M-26MAY111400-00",
            "open_time": "2026-05-11T17:45:00Z",
            "close_time": "2026-05-11T18:00:00Z",
            "yes_sub_title": "Target price: TBD",
            "no_sub_title": "Target price: TBD",
        }
        calls: list[str] = []
        original_get_json = public_rest_batch_builder.get_json

        def fake_get_json(base_url: str, endpoint: str, params=None, *, timeout_seconds: float = 10.0):
            calls.append(endpoint)
            self.assertEqual(base_url, "https://unit.test")
            self.assertEqual(params, None)
            return {
                "market": {
                    "ticker": "KXBTC15M-26MAY111345-45",
                    "status": "finalized",
                    "close_time": "2026-05-11T17:45:00Z",
                    "expiration_value": "81995.77",
                }
            }

        try:
            public_rest_batch_builder.get_json = fake_get_json
            enriched = public_rest_batch_builder.enrich_missing_tbd_strikes_from_previous_market(
                [market],
                kalshi_base_url="https://unit.test",
                now_utc=now_utc,
                timeout_seconds=3.0,
            )
        finally:
            public_rest_batch_builder.get_json = original_get_json

        self.assertEqual(calls, ["/markets/KXBTC15M-26MAY111345-45"])
        self.assertEqual(enriched[0]["strike"], 81995.77)
        self.assertEqual(enriched[0]["strike_source"], "previous_market_expiration_value_official_public_rest")
        self.assertEqual(enriched[0]["strike_source_market_ticker"], "KXBTC15M-26MAY111345-45")
        selected = public_rest_batch_active_market_rows({"markets": enriched}, now_utc=now_utc)
        self.assertEqual([row["ticker"] for row in selected], ["KXBTC15M-26MAY111400-00"])

    def test_sidecar_packet_collector_real_rows_can_flow_to_packet_contract_and_freezer(self) -> None:
        manifest = forward_packet_adapter_collection_manifests()[0]
        market, checkpoint, registered_utc = sidecar_collector_demo_market_and_checkpoint()
        rows = build_sidecar_packet_rows_from_checkpoint(
            market=market,
            checkpoint=checkpoint,
            btc_history_rows=forward_packet_adapter_demo_btc_history(),
            edge_batch=forward_packet_adapter_demo_edge_batch(),
            candidate_manifests=[manifest],
            registered_utc=registered_utc,
            simulated=False,
            diagnostic_only=False,
            source_file="unit_test_real_sidecar_packet",
            source_line_or_offset="1",
        )
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)

        self.assertEqual(len(rows), 2)
        self.assertEqual({row["side"] for row in rows}, {"yes", "no"})
        self.assertTrue(all(row["is_simulated"] == "False" for row in rows))
        self.assertTrue(all(row["is_diagnostic_only"] == "False" for row in rows))
        self.assertTrue(all(row["has_btc_state"] == "True" for row in rows))
        self.assertTrue(all(row["has_v28_baseline"] == "True" for row in rows))
        self.assertTrue(all(row["has_candidate_prediction"] == "True" for row in rows))
        self.assertTrue(all(row["exclusion_reason"] == "not_frozen_candidate_prediction_registry" for row in rows))
        for row in rows:
            self.assertEqual(row_freeze_blockers(row, now_before_close, [manifest]), [])
            self.assertEqual(forward_preflight_row_blockers(row, now_before_close, True), [])

        with TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "sidecar_packets.csv"
            with source_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            evaluations, packet_summary, _template = build_forward_packet_contract(source_csv=source_csv)
            frozen_rows, freeze_summary = build_forward_freezer(now_utc=now_before_close, source_csv=source_csv)

        self.assertEqual(packet_summary["packet_status"], "ready")
        self.assertEqual(packet_summary["packet_ready_rows"], 2)
        self.assertTrue(all(row["packet_ready"] for row in evaluations))
        self.assertEqual(freeze_summary["freeze_status"], "frozen_predictions_written")
        self.assertEqual(freeze_summary["frozen_prediction_rows"], 2)
        self.assertEqual({row["source_status"] for row in frozen_rows}, {"frozen_pre_resolution_prediction"})

    def test_forward_packet_freeze_handoff_blocks_demo_rows_but_accepts_real_packets(self) -> None:
        demo_rows, _demo_summary = build_sidecar_packet_collector_demo()
        manifest = forward_packet_adapter_collection_manifests()[0]
        market, checkpoint, registered_utc = sidecar_collector_demo_market_and_checkpoint()
        real_rows = build_sidecar_packet_rows_from_checkpoint(
            market=market,
            checkpoint=checkpoint,
            btc_history_rows=forward_packet_adapter_demo_btc_history(),
            edge_batch=forward_packet_adapter_demo_edge_batch(),
            candidate_manifests=[manifest],
            registered_utc=registered_utc,
            simulated=False,
            diagnostic_only=False,
            source_file="unit_test_real_sidecar_packet",
            source_line_or_offset="1",
        )
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)

        with TemporaryDirectory() as temp_dir:
            demo_csv = Path(temp_dir) / "demo_packets.csv"
            real_csv = Path(temp_dir) / "real_packets.csv"
            with demo_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(demo_rows[0].keys()))
                writer.writeheader()
                writer.writerows(demo_rows)
            with real_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(real_rows[0].keys()))
                writer.writeheader()
                writer.writerows(real_rows)

            demo_report, demo_frozen, demo_registry = build_forward_packet_freeze_handoff(source_csv=demo_csv, now_utc=now_before_close)
            real_report, real_frozen, real_registry = build_forward_packet_freeze_handoff(source_csv=real_csv, now_utc=now_before_close)

        demo_summary = demo_report["summary"]
        real_summary = real_report["summary"]
        self.assertEqual(demo_summary["handoff_status"], "blocked_non_promotable_input_rows")
        self.assertEqual(demo_summary["packet_contract"]["packet_ready_rows"], len(demo_rows))
        self.assertEqual(demo_summary["freeze"]["frozen_prediction_rows"], 0)
        self.assertIn("input_contains_simulated_rows", demo_summary["blockers"])
        self.assertIn("input_contains_diagnostic_rows", demo_summary["blockers"])
        self.assertEqual(demo_frozen, [])
        self.assertEqual(demo_registry, [])

        self.assertEqual(real_summary["handoff_status"], "frozen_handoff_below_coverage_floor")
        self.assertEqual(real_summary["packet_contract"]["packet_ready_rows"], 2)
        self.assertEqual(real_summary["freeze"]["frozen_prediction_rows"], 2)
        self.assertEqual(real_summary["registry"]["row_count"], 2)
        self.assertFalse(real_summary["promotion_allowed"])
        self.assertIn("frozen_registry_below_row_floor", real_summary["blockers"])
        self.assertIn("frozen_registry_below_market_floor", real_summary["blockers"])
        self.assertEqual(len(real_frozen), 2)
        self.assertEqual(len(real_registry), 2)

    def test_sidecar_bundle_freeze_handoff_blocks_template_demo_but_accepts_real_bundle(self) -> None:
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)
        real_bundle = build_sidecar_input_bundle_template()
        real_bundle["simulated"] = False
        real_bundle["diagnostic_only"] = False

        with TemporaryDirectory() as temp_dir:
            demo_packet_csv = Path(temp_dir) / "demo_bundle_packets.csv"
            real_packet_csv = Path(temp_dir) / "real_bundle_packets.csv"
            input_json = Path(temp_dir) / "real_bundle.json"
            input_json.write_text(json.dumps(real_bundle), encoding="utf-8")

            demo_report, demo_packets, demo_frozen, demo_registry = build_sidecar_bundle_freeze_handoff(
                now_utc=now_before_close,
                packet_csv=demo_packet_csv,
            )
            real_report, real_packets, real_frozen, real_registry = build_sidecar_bundle_freeze_handoff(
                input_json=input_json,
                now_utc=now_before_close,
                packet_csv=real_packet_csv,
            )

        demo_summary = demo_report["summary"]
        real_summary = real_report["summary"]
        self.assertEqual(demo_summary["bundle_handoff_status"], "blocked_non_promotable_bundle_rows")
        expected_rows = expected_sidecar_packet_rows()
        self.assertEqual(demo_summary["packet_rows"]["rows"], expected_rows)
        self.assertEqual(demo_summary["freeze_handoff"]["frozen_prediction_rows"], 0)
        self.assertIn("packet_rows_contain_simulated_rows", demo_summary["blockers"])
        self.assertIn("packet_rows_contain_diagnostic_rows", demo_summary["blockers"])
        self.assertEqual(len(demo_packets), expected_rows)
        self.assertEqual(demo_frozen, [])
        self.assertEqual(demo_registry, [])

        self.assertEqual(real_summary["bundle_handoff_status"], "frozen_handoff_below_coverage_floor")
        self.assertEqual(real_summary["bundle"]["bundle_status"], "input_bundle_ready_for_collection")
        self.assertEqual(real_summary["packet_rows"]["rows"], expected_rows)
        self.assertEqual(real_summary["freeze_handoff"]["frozen_prediction_rows"], expected_rows)
        self.assertEqual(real_summary["freeze_handoff"]["registry_rows"], expected_rows)
        self.assertFalse(real_summary["promotion_allowed"])
        self.assertEqual(len(real_packets), expected_rows)
        self.assertEqual(len(real_frozen), expected_rows)
        self.assertEqual(len(real_registry), expected_rows)

    def test_sidecar_bundle_batch_handoff_handles_empty_and_real_bundle_directory(self) -> None:
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)
        first_bundle = build_sidecar_input_bundle_template()
        first_bundle["simulated"] = False
        first_bundle["diagnostic_only"] = False
        second_bundle = json.loads(json.dumps(first_bundle))
        second_bundle["market"]["market_ticker"] = "KXBTC15M-26MAY111210-100500"
        second_bundle["checkpoint"]["market_ticker"] = "KXBTC15M-26MAY111210-100500"
        second_bundle["market"]["strike"] = 100500.0

        with TemporaryDirectory() as temp_dir:
            empty_dir = Path(temp_dir) / "empty"
            bundle_dir = Path(temp_dir) / "bundles"
            empty_dir.mkdir()
            bundle_dir.mkdir()
            (bundle_dir / "bundle_a.json").write_text(json.dumps(first_bundle), encoding="utf-8")
            (bundle_dir / "bundle_b.json").write_text(json.dumps(second_bundle), encoding="utf-8")

            empty_report, empty_packets, empty_frozen, empty_registry = build_sidecar_bundle_batch_handoff(
                bundle_dir=empty_dir,
                now_utc=now_before_close,
                packet_csv=Path(temp_dir) / "empty_packets.csv",
            )
            real_report, real_packets, real_frozen, real_registry = build_sidecar_bundle_batch_handoff(
                bundle_dir=bundle_dir,
                now_utc=now_before_close,
                packet_csv=Path(temp_dir) / "real_packets.csv",
            )

        empty_summary = empty_report["summary"]
        real_summary = real_report["summary"]
        self.assertEqual(empty_summary["batch_handoff_status"], "blocked_no_input_bundles")
        self.assertEqual(empty_summary["input_bundle_files"], 0)
        self.assertEqual(empty_summary["packet_rows"]["rows"], 0)
        self.assertEqual(empty_packets, [])
        self.assertEqual(empty_frozen, [])
        self.assertEqual(empty_registry, [])

        self.assertEqual(real_summary["batch_handoff_status"], "frozen_batch_handoff_below_coverage_floor")
        self.assertEqual(real_summary["input_bundle_files"], 2)
        self.assertEqual(real_summary["ready_bundle_files"], 2)
        expected_rows = expected_sidecar_packet_rows(markets=2)
        self.assertEqual(real_summary["packet_rows"]["rows"], expected_rows)
        self.assertEqual(real_summary["packet_rows"]["markets"], 2)
        self.assertEqual(real_summary["freeze_handoff"]["frozen_prediction_rows"], expected_rows)
        self.assertEqual(real_summary["freeze_handoff"]["registry_rows"], expected_rows)
        self.assertFalse(real_summary["promotion_allowed"])
        self.assertEqual(len(real_packets), expected_rows)
        self.assertEqual(len(real_frozen), expected_rows)
        self.assertEqual(len(real_registry), expected_rows)

    def test_sidecar_bundle_batch_handoff_preserves_existing_frozen_rows_after_close(self) -> None:
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)
        now_after_close = datetime(2026, 5, 11, 12, 12, tzinfo=timezone.utc)
        bundle = build_sidecar_input_bundle_template()
        bundle["simulated"] = False
        bundle["diagnostic_only"] = False

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bundle_dir = temp_path / "bundles"
            bundle_dir.mkdir()
            (bundle_dir / "bundle.json").write_text(json.dumps(bundle), encoding="utf-8")

            _pre_report, _packets, frozen_before_close, _registry = build_sidecar_bundle_batch_handoff(
                bundle_dir=bundle_dir,
                now_utc=now_before_close,
                packet_csv=temp_path / "pre_packets.csv",
            )
            for frozen in frozen_before_close:
                frozen["v28_p_anchor"] = ""
                frozen["v28_p_recent_transport"] = ""
                frozen["v28_transport_recent_n"] = ""
            existing_frozen_csv = temp_path / "existing_frozen.csv"
            with existing_frozen_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(frozen_before_close)

            post_report, _post_packets, preserved_frozen, preserved_registry = build_sidecar_bundle_batch_handoff(
                bundle_dir=bundle_dir,
                now_utc=now_after_close,
                packet_csv=temp_path / "post_packets.csv",
                preserve_existing_frozen=True,
                existing_frozen_csv=existing_frozen_csv,
            )

        summary = post_report["summary"]
        self.assertEqual(summary["batch_handoff_status"], "frozen_batch_handoff_below_coverage_floor")
        self.assertEqual(summary["freeze_handoff"]["newly_frozen_prediction_rows"], 0)
        expected_rows = expected_sidecar_packet_rows()
        self.assertEqual(summary["freeze_handoff"]["frozen_prediction_rows"], expected_rows)
        self.assertEqual(summary["freeze_handoff"]["registry_rows"], expected_rows)
        self.assertTrue(summary["preservation"]["enabled"])
        self.assertEqual(summary["preservation"]["valid_existing_frozen_rows"], expected_rows)
        self.assertEqual(summary["preservation"]["merged_frozen_rows"], expected_rows)
        self.assertEqual(summary["preservation"]["component_enriched_rows"], expected_rows)
        self.assertGreater(summary["preservation"]["component_enriched_fields"], 0)
        self.assertIn("current_replay_produced_no_new_frozen_rows_existing_ledger_preserved", summary["blockers"])
        self.assertEqual(len(preserved_frozen), expected_rows)
        self.assertEqual(len(preserved_registry), expected_rows)
        self.assertTrue(all(row["v28_p_anchor"] for row in preserved_frozen))
        self.assertTrue(all(row["v28_p_recent_transport"] for row in preserved_frozen))
        self.assertTrue(all(row["v28_transport_recent_n"] for row in preserved_frozen))

    def test_sidecar_batch_label_join_handoff_blocks_empty_batch_frozen_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            report, rows = build_sidecar_batch_label_join_handoff(
                frozen_csv=Path(temp_dir) / "missing_batch_frozen.csv",
                label_csvs=[Path(temp_dir) / "missing_labels.csv"],
            )

        summary = report["summary"]
        self.assertEqual(summary["batch_label_join_status"], "blocked_no_batch_frozen_rows")
        self.assertEqual(summary["frozen_rows"], 0)
        self.assertEqual(summary["labeled_rows"], 0)
        self.assertEqual(summary["joined_rows"], 0)
        self.assertFalse(summary["promotion_allowed"])
        self.assertEqual(rows, [])
        self.assertIn("no_batch_frozen_rows", summary["blockers"])

    def test_sidecar_batch_settlement_label_fetcher_waits_until_close(self) -> None:
        frozen = {
            "frozen_prediction_id": "fp",
            "frozen_utc": "2026-05-11T12:01:00Z",
            "row_id": "row",
            "market_ticker": "KXBTC15M-26MAY111210-100000",
            "market_close_ts_utc": "2026-05-11T12:10:00Z",
            "decision_ts_utc": "2026-05-11T12:00:00Z",
            "side": "yes",
            "strike": "100000",
            "candidate_id": "cand",
            "candidate_p_yes": "0.6",
            "v28_p_yes": "0.5",
            "source_status": "frozen_pre_resolution_prediction",
        }
        with TemporaryDirectory() as temp_dir:
            frozen_csv = Path(temp_dir) / "frozen.csv"
            with frozen_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerow(frozen)
            report, labels = sidecar_label_fetcher.build(
                frozen_csv=frozen_csv,
                now_utc=datetime(2026, 5, 11, 12, 5, tzinfo=timezone.utc),
            )

        summary = report["summary"]
        self.assertEqual(summary["label_fetch_status"], "blocked_waiting_for_market_close")
        self.assertEqual(summary["frozen_rows"], 1)
        self.assertEqual(summary["label_rows"], 0)
        self.assertFalse(summary["promotion_allowed"])
        self.assertEqual(labels, [])
        self.assertIn("market_not_closed", summary["blocker_counts"])

    def test_sidecar_batch_settlement_label_fetcher_writes_post_close_labels(self) -> None:
        frozen = {
            "frozen_prediction_id": "fp",
            "frozen_utc": "2026-05-11T12:01:00Z",
            "row_id": "row",
            "market_ticker": "KXBTC15M-26MAY111210-100000",
            "market_close_ts_utc": "2026-05-11T12:10:00Z",
            "decision_ts_utc": "2026-05-11T12:00:00Z",
            "side": "yes",
            "strike": "100000",
            "candidate_id": "cand",
            "candidate_p_yes": "0.6",
            "v28_p_yes": "0.5",
            "source_status": "frozen_pre_resolution_prediction",
        }

        def fake_fetch_market(_base_url: str, ticker: str, *, timeout_seconds: float) -> dict[str, str]:
            self.assertEqual(ticker, "KXBTC15M-26MAY111210-100000")
            return {
                "ticker": ticker,
                "status": "finalized",
                "result": "yes",
                "settlement_ts": "2026-05-11T12:10:07Z",
                "expiration_value": "100123.45",
            }

        with TemporaryDirectory() as temp_dir:
            frozen_csv = Path(temp_dir) / "frozen.csv"
            with frozen_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerow(frozen)
            original = sidecar_label_fetcher.fetch_market
            sidecar_label_fetcher.fetch_market = fake_fetch_market
            try:
                report, labels = sidecar_label_fetcher.build(
                    frozen_csv=frozen_csv,
                    now_utc=datetime(2026, 5, 11, 12, 12, tzinfo=timezone.utc),
                )
            finally:
                sidecar_label_fetcher.fetch_market = original

        summary = report["summary"]
        self.assertEqual(summary["label_fetch_status"], "settlement_labels_available")
        self.assertEqual(summary["label_rows"], 1)
        self.assertEqual(labels[0]["y_yes_win"], "1")
        self.assertEqual(labels[0]["settlement_price"], "100123.45")
        self.assertEqual(summary["fetched_label_rows"], 1)
        self.assertEqual(summary["preserved_existing_label_rows"], 0)
        self.assertFalse(summary["promotion_allowed"])

    def test_sidecar_batch_settlement_label_fetcher_preserves_existing_valid_labels(self) -> None:
        frozen = {
            "frozen_prediction_id": "fp",
            "frozen_utc": "2026-05-11T12:01:00Z",
            "row_id": "row",
            "market_ticker": "KXBTC15M-26MAY111210-100000",
            "market_close_ts_utc": "2026-05-11T12:10:00Z",
            "decision_ts_utc": "2026-05-11T12:00:00Z",
            "side": "yes",
            "strike": "100000",
            "candidate_id": "cand",
            "candidate_p_yes": "0.6",
            "v28_p_yes": "0.5",
            "source_status": "frozen_pre_resolution_prediction",
        }

        def fake_fetch_market(_base_url: str, ticker: str, *, timeout_seconds: float) -> dict[str, str]:
            self.assertEqual(ticker, "KXBTC15M-26MAY111210-100000")
            return {
                "ticker": ticker,
                "status": "finalized",
                "result": "",
            }

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            frozen_csv = temp_path / "frozen.csv"
            with frozen_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerow(frozen)
            existing_labels_csv = temp_path / "labels.csv"
            with existing_labels_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=sidecar_label_fetcher.LABEL_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerow(
                    {
                        "market_ticker": "KXBTC15M-26MAY111210-100000",
                        "y_yes_win": "1",
                        "binary_result": "yes",
                        "settlement_ts_utc": "2026-05-11T12:10:07.000Z",
                        "label_available_ts_utc": "2026-05-11T12:10:30.000Z",
                        "settlement_price": "100123.45",
                        "strike": "100000",
                        "label_source": "unit_test_previous_fetch",
                        "market_status": "finalized",
                    }
                )
            original = sidecar_label_fetcher.fetch_market
            sidecar_label_fetcher.fetch_market = fake_fetch_market
            try:
                report, labels = sidecar_label_fetcher.build(
                    frozen_csv=frozen_csv,
                    existing_labels_csv=existing_labels_csv,
                    now_utc=datetime(2026, 5, 11, 12, 15, tzinfo=timezone.utc),
                )
            finally:
                sidecar_label_fetcher.fetch_market = original

        summary = report["summary"]
        self.assertEqual(summary["label_fetch_status"], "settlement_labels_available")
        self.assertEqual(summary["fetched_label_rows"], 0)
        self.assertEqual(summary["preserved_existing_label_rows"], 1)
        self.assertEqual(summary["label_rows"], 1)
        self.assertEqual(labels[0]["label_source"], "unit_test_previous_fetch")
        self.assertIn("missing_result_after_determination_status:finalized", summary["blocker_counts"])

    def test_sidecar_batch_label_join_handoff_joins_settled_batch_rows(self) -> None:
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)
        first_bundle = build_sidecar_input_bundle_template()
        first_bundle["simulated"] = False
        first_bundle["diagnostic_only"] = False
        second_bundle = json.loads(json.dumps(first_bundle))
        second_bundle["market"]["market_ticker"] = "KXBTC15M-26MAY111210-100500"
        second_bundle["checkpoint"]["market_ticker"] = "KXBTC15M-26MAY111210-100500"
        second_bundle["market"]["strike"] = 100500.0

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bundle_dir = temp_path / "bundles"
            bundle_dir.mkdir()
            (bundle_dir / "bundle_a.json").write_text(json.dumps(first_bundle), encoding="utf-8")
            (bundle_dir / "bundle_b.json").write_text(json.dumps(second_bundle), encoding="utf-8")
            _report, _packets, frozen_rows, _registry = build_sidecar_bundle_batch_handoff(
                bundle_dir=bundle_dir,
                now_utc=now_before_close,
                packet_csv=temp_path / "packets.csv",
            )

            frozen_csv = temp_path / "batch_frozen.csv"
            with frozen_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(frozen_rows)

            labels_csv = temp_path / "labels.csv"
            label_fields = [
                "market_ticker",
                "y_yes_win",
                "settlement_ts_utc",
                "label_available_ts_utc",
                "settlement_price",
                "label_source",
            ]
            with labels_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=label_fields)
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "market_ticker": "KXBTC15M-26MAY111210-100000",
                            "y_yes_win": "1",
                            "settlement_ts_utc": "2026-05-11T12:10:30Z",
                            "label_available_ts_utc": "2026-05-11T12:10:45Z",
                            "settlement_price": "100125",
                            "label_source": "unit_test",
                        },
                        {
                            "market_ticker": "KXBTC15M-26MAY111210-100500",
                            "y_yes_win": "0",
                            "settlement_ts_utc": "2026-05-11T12:10:30Z",
                            "label_available_ts_utc": "2026-05-11T12:10:45Z",
                            "settlement_price": "100450",
                            "label_source": "unit_test",
                        },
                    ]
                )

            label_report, labeled_rows = build_sidecar_batch_label_join_handoff(
                frozen_csv=frozen_csv,
                label_csvs=[labels_csv],
            )

        summary = label_report["summary"]
        self.assertEqual(summary["batch_label_join_status"], "joined_batch_labels_available")
        expected_rows = expected_sidecar_packet_rows(markets=2)
        self.assertEqual(summary["frozen_rows"], expected_rows)
        self.assertEqual(summary["labeled_rows"], expected_rows)
        self.assertEqual(summary["joined_rows"], expected_rows)
        self.assertEqual(summary["joined_markets"], 2)
        self.assertFalse(summary["promotion_allowed"])
        self.assertTrue(summary["candidate_metrics"])
        self.assertTrue(all(row["label_join_status"] == "joined_post_resolution" for row in labeled_rows))

    def test_forward_label_join_requires_frozen_before_close_and_label_after_close(self) -> None:
        frozen = {
            "frozen_prediction_id": "fp1",
            "frozen_utc": "2026-05-11T12:09:00Z",
            "row_id": "row1",
            "market_ticker": "KXBTC15M-26MAY111210-100000",
            "market_close_ts_utc": "2026-05-11T12:10:00Z",
            "decision_ts_utc": "2026-05-11T12:00:00Z",
            "side": "yes",
            "candidate_id": "v28s_logistic_calibration_v001",
            "candidate_p_yes": "0.75",
            "candidate_fair_yes_cents": "75",
            "candidate_fair_no_cents": "25",
            "candidate_fair_side_cents": "75",
            "candidate_edge_cents": "20",
            "v28_p_yes": "0.60",
            "v28_fair_yes_cents": "60",
            "v28_fair_no_cents": "40",
            "ask_cents": "55",
        }
        labels = {
            "KXBTC15M-26MAY111210-100000": {
                "market_ticker": "KXBTC15M-26MAY111210-100000",
                "y_yes_win": 1.0,
                "settlement_ts_utc": "2026-05-11T12:10:30.000Z",
                "label_available_ts_utc": "2026-05-11T12:10:45.000Z",
                "settlement_price": 100123.0,
                "settlement_margin_dollars": 123.0,
                "settlement_side": "yes",
                "settlement_source": "unit_test",
            }
        }

        joined = join_forward_label_rows([frozen], labels)

        self.assertEqual(joined[0]["label_join_status"], "joined_post_resolution")
        self.assertEqual(joined[0]["label_join_blockers"], "")
        self.assertEqual(joined[0]["y_yes_win"], "1")
        self.assertLess(float(joined[0]["candidate_brier_yes"]), float(joined[0]["v28_brier_yes"]))

        early = dict(labels["KXBTC15M-26MAY111210-100000"])
        early["label_available_ts_utc"] = "2026-05-11T12:08:00.000Z"
        blocked = join_forward_label_rows([frozen], {"KXBTC15M-26MAY111210-100000": early})
        self.assertEqual(blocked[0]["label_join_status"], "blocked")
        self.assertIn("label_available_before_close", blocked[0]["label_join_blockers"])
        self.assertIn("label_available_not_after_freeze", blocked[0]["label_join_blockers"])

    def test_forward_evidence_scorer_compares_clean_joined_rows_to_v28(self) -> None:
        rows = [
            {
                "label_join_status": "joined_post_resolution",
                "label_join_blockers": "",
                "source_status": "frozen_pre_resolution_prediction",
                "row_id": "r1",
                "market_ticker": "M1",
                "side": "yes",
                "candidate_id": "cand",
                "model_hash": "h",
                "model_type": "regularized_logistic",
                "model_track": "pure_physics",
                "candidate_p_yes": "0.8",
                "v28_p_yes": "0.6",
                "y_yes_win": "1",
                "candidate_fair_side_cents": "80",
                "ask_cents": "55",
                "seconds_to_close": "120",
                "v28_d_sigma": "0.5",
                "book_implied_yes_from_side_ask": "0.54",
            },
            {
                "label_join_status": "joined_post_resolution",
                "label_join_blockers": "",
                "source_status": "frozen_pre_resolution_prediction",
                "row_id": "r2",
                "market_ticker": "M2",
                "side": "no",
                "candidate_id": "cand",
                "model_hash": "h",
                "model_type": "regularized_logistic",
                "model_track": "pure_physics",
                "candidate_p_yes": "0.2",
                "v28_p_yes": "0.4",
                "y_yes_win": "0",
                "candidate_fair_side_cents": "80",
                "ask_cents": "55",
                "seconds_to_close": "300",
                "v28_d_sigma": "-0.7",
                "book_implied_yes_from_side_ask": "0.45",
            },
            {
                "label_join_status": "blocked",
                "label_join_blockers": "missing_settlement_label",
                "source_status": "frozen_pre_resolution_prediction",
                "candidate_id": "cand",
                "candidate_p_yes": "0.99",
                "v28_p_yes": "0.01",
                "y_yes_win": "1",
            },
        ]

        metrics, bins, summary = score_forward_evidence_rows(rows)
        all_rows = [row for row in metrics if row["candidate_id"] == "cand" and row["slice"] == "all_rows"][0]
        near_rows = [row for row in metrics if row["candidate_id"] == "cand" and row["slice"] == "near_boundary_abs_d_lte_1"][0]

        self.assertEqual(summary["clean_forward_rows"], 2)
        self.assertEqual(summary["clean_forward_markets"], 2)
        self.assertEqual(summary["candidate_count"], 1)
        self.assertLess(float(all_rows["candidate_brier"]), float(all_rows["v28_brier"]))
        self.assertLess(float(near_rows["delta_brier_candidate_minus_v28"]), 0.0)
        gate = summary["candidate_gates"][0]
        self.assertEqual(gate["candidate_id"], "cand")
        self.assertEqual(gate["rows"], 2)
        self.assertEqual(gate["required_rows"], 200)
        self.assertEqual(gate["row_shortfall"], 198)
        self.assertEqual(gate["markets"], 2)
        self.assertEqual(gate["required_markets"], 40)
        self.assertEqual(gate["market_shortfall"], 38)
        self.assertEqual(gate["rows_per_market"], 1.0)
        self.assertEqual(gate["estimated_markets_to_row_floor"], 198)
        self.assertEqual(gate["estimated_additional_markets_needed"], 198)
        self.assertLess(float(gate["delta_brier_candidate_minus_v28"]), 0.0)
        self.assertLess(float(gate["near_boundary_delta_brier_candidate_minus_v28"]), 0.0)
        self.assertTrue(bins)

    def test_sidecar_batch_evidence_scorer_reuses_forward_metrics_without_promotion(self) -> None:
        rows = [
            {
                "label_join_status": "joined_post_resolution",
                "label_join_blockers": "",
                "source_status": "frozen_pre_resolution_prediction",
                "row_id": "r1",
                "market_ticker": "KXBTC15M-26MAY111210-100000",
                "side": "yes",
                "candidate_id": "cand",
                "model_hash": "h",
                "model_type": "regularized_logistic",
                "model_track": "pure_physics",
                "candidate_p_yes": "0.8",
                "v28_p_yes": "0.6",
                "y_yes_win": "1",
                "candidate_fair_side_cents": "80",
                "ask_cents": "55",
                "seconds_to_close": "120",
                "v28_d_sigma": "0.5",
                "book_implied_yes_from_side_ask": "0.54",
            }
        ]
        with TemporaryDirectory() as temp_dir:
            labeled_csv = Path(temp_dir) / "sidecar_labeled.csv"
            with labeled_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            metrics, bins, summary = build_sidecar_batch_evidence_score(labeled_csv=labeled_csv)

        self.assertEqual(summary["evidence_status"], "scored_sidecar_batch_evidence")
        self.assertEqual(summary["evidence_family"], "sidecar_batch")
        self.assertFalse(summary["canonical_promotion_ledger"])
        self.assertFalse(summary["promotion_status"]["allowed"])
        self.assertEqual(summary["clean_forward_rows"], 1)
        self.assertEqual(summary["clean_forward_markets"], 1)
        self.assertEqual(summary["promotable_candidate_count"], 0)
        self.assertTrue(metrics)
        self.assertTrue(bins)

    def test_sidecar_collection_cycle_status_keeps_below_floor_non_promoting(self) -> None:
        status, blockers, next_actions = sidecar_cycle_status(
            collect_status="skipped_existing_sidecar_bundles",
            handoff_summary={"freeze_handoff": {"frozen_prediction_rows": 24, "registry_markets": 3}},
            label_summary={"label_fetch_status": "settlement_labels_available"},
            join_summary={"joined_rows": 16, "joined_markets": 2},
            evidence_summary={
                "clean_forward_rows": 16,
                "clean_forward_markets": 2,
                "promotable_candidate_count": 0,
            },
            source_summary={"overall_verdict": "blocked"},
            goal_summary={"overall_status": "not_complete"},
        )

        self.assertEqual(status, "sidecar_evidence_below_coverage_floor")
        self.assertIn("sidecar_clean_rows_below_forward_floor", blockers)
        self.assertIn("sidecar_clean_markets_below_forward_floor", blockers)
        self.assertIn("source_contract_not_promotion_grade", blockers)
        self.assertIn("does not place orders", SIDECAR_CYCLE_GUARDRAILS)
        self.assertTrue(any("Keep collecting" in action for action in next_actions))

    def test_paired_sidecar_spot_alignment_uses_latest_non_future_tick(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundle_path = root / "research_particle" / "v28_successor" / "sidecar_input_bundles" / "bundle.json"
            bundle_path.parent.mkdir(parents=True, exist_ok=True)
            bundle_path.write_text(
                json.dumps({"registered_utc": "2026-05-11T12:00:01Z"}) + "\n",
                encoding="utf-8",
            )
            spot_path = root / "spot_ticks.ndjson"
            spot_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "local_recv_ts_utc": "2026-05-11T12:00:00.800000+00:00",
                                "exchange_ts_utc": "2026-05-11T12:00:00.750000+00:00",
                                "price": 81150.0,
                                "source": "coinbase_unit",
                            },
                            sort_keys=True,
                        ),
                        json.dumps(
                            {
                                "local_recv_ts_utc": "2026-05-11T12:00:01.100000+00:00",
                                "exchange_ts_utc": "2026-05-11T12:00:01.050000+00:00",
                                "price": 81151.0,
                                "source": "coinbase_unit",
                            },
                            sort_keys=True,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            batch_report = {
                "summary": {"generated_utc": "2026-05-11T12:00:01Z"},
                "markets": [
                    {
                        "market_ticker": "KXBTC15M-26MAY111200-00",
                        "output_bundle_json": "research_particle/v28_successor/sidecar_input_bundles/bundle.json",
                    }
                ],
            }

            rows = build_sidecar_spot_alignment(
                batch_report=batch_report,
                spot_path=spot_path,
                workspace=root,
                max_age_ms=500.0,
            )

        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].spot_ready_no_future)
        self.assertEqual(rows[0].latest_spot_before_ts_utc, "2026-05-11T12:00:00.800000+00:00")
        self.assertAlmostEqual(rows[0].latest_spot_before_age_ms or 0.0, 200.0)
        self.assertEqual(rows[0].first_spot_after_ts_utc, "2026-05-11T12:00:01.100000+00:00")

    def test_paired_sidecar_spot_manifest_is_research_only_and_non_promoting(self) -> None:
        spot_status = SpotTickerRecorderStatus(
            schema_version="spot-ticker-recorder-status-v1",
            source="coinbase_btcusd_matches",
            url="wss://unit.test",
            output="spot_ticks.ndjson",
            issues="spot_issues.ndjson",
            status="stopped",
            ticks_written=10,
            issue_count=0,
            started_at_utc="2026-05-11T12:00:00+00:00",
            ended_at_utc="2026-05-11T12:00:10+00:00",
            last_tick_ts_utc="2026-05-11T12:00:09+00:00",
            error="",
        )

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = build_paired_sidecar_spot_manifest(
                run_id="unit-sidecar-spot",
                artifact_root=root,
                collect_mode="fixture",
                sidecar_report={
                    "summary": {
                        "cycle_status": "sidecar_evidence_below_coverage_floor",
                        "sidecar_frozen_rows": 2,
                        "sidecar_frozen_markets": 1,
                    }
                },
                batch_report={"summary": {"markets_selected": 1, "packet_rows": 14}},
                spot_status=spot_status,
                spot_path=root / "spot_ticks.ndjson",
                spot_issue_path=root / "spot_issues.ndjson",
                spot_status_path=root / "spot_status.json",
                spot_max_age_ms=2_000.0,
                alignment_rows=[],
                manifest_json=root / "paired_sidecar_spot_manifest.json",
                manifest_md=root / "paired_sidecar_spot_manifest.md",
            )

        self.assertFalse(result.promotion_allowed)
        self.assertFalse(result.paired_capture_ready)
        self.assertEqual(result.sidecar_markets_selected, 1)
        self.assertIn("does not place orders", result.research_only_guardrails)
        self.assertIn("locked OOS probability", result.promotion_status["reason"])

    def test_paired_sidecar_spot_ignores_stale_batch_after_collection_error(self) -> None:
        report = paired_sidecar_batch_report_for_alignment(
            sidecar_report={"summary": {"blockers": ["blocked_collection_error"]}},
            loaded_batch_report={
                "summary": {"batch_status": "batch_bundles_ready_for_freeze", "markets_selected": 1},
                "markets": [{"market_ticker": "STALE"}],
            },
        )

        self.assertEqual(report["summary"]["batch_status"], "sidecar_collection_blocked_latest_batch_ignored")
        self.assertEqual(report["summary"]["markets_selected"], 0)
        self.assertEqual(report["markets"], [])
        self.assertFalse(report["summary"]["promotion_allowed"])

    def test_paired_sidecar_spot_ignores_batch_generated_outside_capture_window(self) -> None:
        report = paired_sidecar_batch_report_for_alignment(
            sidecar_report={"summary": {"blockers": [], "collect_mode": "public_rest"}},
            loaded_batch_report={
                "summary": {
                    "batch_status": "batch_bundles_ready_for_freeze",
                    "generated_utc": "2026-05-11T12:00:00Z",
                    "markets_selected": 1,
                },
                "markets": [{"market_ticker": "STALE"}],
            },
            capture_started_utc=datetime(2026, 5, 11, 12, 1, 0, tzinfo=timezone.utc),
            capture_finished_utc=datetime(2026, 5, 11, 12, 1, 10, tzinfo=timezone.utc),
        )

        self.assertEqual(report["summary"]["batch_status"], "sidecar_batch_outside_paired_capture_window_ignored")
        self.assertEqual(report["summary"]["markets_selected"], 0)
        self.assertEqual(report["markets"], [])
        self.assertFalse(report["summary"]["promotion_allowed"])

    def test_paired_sidecar_spot_accepts_batch_generated_inside_capture_window(self) -> None:
        loaded_report = {
            "summary": {
                "batch_status": "batch_bundles_ready_for_freeze",
                "generated_utc": "2026-05-11T12:01:04Z",
                "markets_selected": 1,
            },
            "markets": [{"market_ticker": "FRESH"}],
        }

        report = paired_sidecar_batch_report_for_alignment(
            sidecar_report={"summary": {"blockers": [], "collect_mode": "public_rest"}},
            loaded_batch_report=loaded_report,
            capture_started_utc=datetime(2026, 5, 11, 12, 1, 0, tzinfo=timezone.utc),
            capture_finished_utc=datetime(2026, 5, 11, 12, 1, 10, tzinfo=timezone.utc),
        )

        self.assertEqual(report, loaded_report)

    def test_paired_sidecar_spot_ignores_mode_mismatched_batch(self) -> None:
        report = paired_sidecar_batch_report_for_alignment(
            sidecar_report={"summary": {"blockers": [], "collect_mode": "public_rest"}},
            loaded_batch_report={
                "summary": {
                    "batch_status": "contract_demo_ready_not_evidence",
                    "generated_utc": "2026-05-11T12:01:04Z",
                    "markets_selected": 2,
                    "mode": "fixture",
                },
                "markets": [{"market_ticker": "FIXTURE"}],
            },
            capture_started_utc=datetime(2026, 5, 11, 12, 1, 0, tzinfo=timezone.utc),
            capture_finished_utc=datetime(2026, 5, 11, 12, 1, 10, tzinfo=timezone.utc),
        )

        self.assertEqual(report["summary"]["batch_status"], "sidecar_batch_mode_mismatch_ignored")
        self.assertEqual(report["summary"]["markets_selected"], 0)
        self.assertEqual(report["markets"], [])

    def test_paired_sidecar_spot_enrichment_attaches_no_future_tick_to_packet_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundle_rel = "research_particle/v28_successor/sidecar_input_bundles/unit_bundle.json"
            packet_csv = root / "packets.csv"
            with packet_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "row_id",
                        "market_ticker",
                        "decision_ts_utc",
                        "side",
                        "source_file",
                        "candidate_id",
                        "btc_spot",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "row_id": "row-1",
                        "market_ticker": "KXBTC15M-UNIT",
                        "decision_ts_utc": "2026-05-11T12:00:01.000Z",
                        "side": "yes",
                        "source_file": bundle_rel,
                        "candidate_id": "candidate-unit",
                        "btc_spot": "100.0",
                    }
                )
            spot_path = root / "spot_ticks.ndjson"
            spot_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "local_recv_ts_utc": "2026-05-11T12:00:00.900000+00:00",
                                "exchange_ts_utc": "2026-05-11T12:00:00.850000+00:00",
                                "price": 101.0,
                                "source": "coinbase_unit",
                            },
                            sort_keys=True,
                        ),
                        json.dumps(
                            {
                                "local_recv_ts_utc": "2026-05-11T12:00:01.050000+00:00",
                                "exchange_ts_utc": "2026-05-11T12:00:01.020000+00:00",
                                "price": 102.0,
                                "source": "coinbase_unit",
                            },
                            sort_keys=True,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manifest_path = root / "paired_sidecar_spot_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "unit-enrich",
                            "artifact_root": str(root),
                            "spot_output": str(spot_path),
                            "spot_max_age_ms": 500.0,
                        },
                        "alignment_rows": [
                            {
                                "bundle_path": str(root / bundle_rel),
                                "market_ticker": "KXBTC15M-UNIT",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            summary, rows = build_enriched_sidecar_spot_packets(
                manifest_path=manifest_path,
                packet_csv=packet_csv,
                workspace=root,
            )

        self.assertTrue(summary.enrichment_ready)
        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(summary.matching_packet_rows, 1)
        self.assertEqual(summary.enriched_packet_rows, 1)
        self.assertEqual(rows[0]["independent_spot_price"], "101.00000000")
        self.assertEqual(rows[0]["independent_spot_ready"], "True")
        self.assertEqual(rows[0]["independent_spot_age_ms"], "100.000")
        self.assertEqual(rows[0]["independent_spot_vs_candle_bps"], "100.000000")

    def test_paired_sidecar_spot_diagnostic_compares_tick_and_candle_probabilities(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            enriched_csv = root / "enriched.csv"
            labeled_csv = root / "labeled.csv"
            enriched_fields = [
                "row_id",
                "market_ticker",
                "candidate_id",
                "side",
                "decision_ts_utc",
                "seconds_to_close",
                "strike",
                "btc_spot",
                "independent_spot_price",
                "independent_spot_age_ms",
                "independent_spot_vs_candle_bps",
                "candidate_p_yes",
                "v28_p_yes",
                "ask_cents",
                "book_implied_yes_from_side_ask",
            ]
            with enriched_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=enriched_fields)
                writer.writeheader()
                writer.writerow(
                    {
                        "row_id": "row-1",
                        "market_ticker": "KXBTC15M-DIAG",
                        "candidate_id": "candidate-unit",
                        "side": "yes",
                        "decision_ts_utc": "2026-05-11T12:00:01Z",
                        "seconds_to_close": "300",
                        "strike": "100.5",
                        "btc_spot": "100.0",
                        "independent_spot_price": "101.0",
                        "independent_spot_age_ms": "100.0",
                        "independent_spot_vs_candle_bps": "100.0",
                        "candidate_p_yes": "0.55",
                        "v28_p_yes": "0.50",
                        "ask_cents": "45.0",
                        "book_implied_yes_from_side_ask": "0.45",
                    }
                )
            labeled_fields = ["row_id", "market_ticker", "candidate_id", "side", "label_join_status", "y_yes_win"]
            with labeled_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=labeled_fields)
                writer.writeheader()
                writer.writerow(
                    {
                        "row_id": "row-1",
                        "market_ticker": "KXBTC15M-DIAG",
                        "candidate_id": "candidate-unit",
                        "side": "yes",
                        "label_join_status": "joined_post_resolution",
                        "y_yes_win": "1",
                    }
                )

            summary, model_rows, diagnostic_rows = build_sidecar_spot_diagnostic(
                enriched_csv=enriched_csv,
                labeled_csv=labeled_csv,
                annualized_vol=0.65,
            )

        by_model = {row["model"]: row for row in model_rows}
        self.assertTrue(summary.diagnostic_ready)
        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(summary.joined_rows, 1)
        self.assertLess(by_model["tick_brownian"]["brier"], by_model["candle_brownian"]["brier"])
        self.assertLess(summary.tick_brownian_delta_brier_vs_candle or 0.0, 0.0)
        self.assertGreater(diagnostic_rows[0]["tick_brownian_p_yes"], diagnostic_rows[0]["candle_brownian_p_yes"])

    def test_paired_sidecar_spot_aggregate_rolls_up_live_shadow_diagnostics(self) -> None:
        def diagnostic_row(market: str, tick_brier: float, candle_brier: float) -> dict[str, object]:
            row: dict[str, object] = {
                "market_ticker": market,
                "row_id": f"{market}-row",
            }
            metrics = {
                "candidate": (0.20, 0.30, 10.0, 1.0),
                "v28": (0.01, 0.02, -1.0, 0.0),
                "candle_brownian": (candle_brier, 0.22, 8.0, -1.0),
                "tick_brownian": (tick_brier, 0.18, 7.0, -1.0),
                "market_side_ask": (0.02, 0.04, -0.5, 0.0),
            }
            for model, (brier, logloss, ev, pnl) in metrics.items():
                row[f"{model}_brier"] = brier
                row[f"{model}_logloss"] = logloss
                row[f"{model}_side_ev_cents"] = ev
                row[f"{model}_side_pnl_if_selected_cents"] = pnl
            return row

        def write_valid_manifest(capture_dir: Path, market: str) -> None:
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": capture_dir.name,
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                            "promotion_allowed": False,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {
                                "market_ticker": market,
                                "market_close_ts_utc": "2026-05-11T12:15:00Z",
                            }
                        ],
                        "alignment_rows": [
                            {
                                "market_ticker": market,
                                "decision_ts_utc": "2026-05-11T12:00:00Z",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            for idx, (tick_brier, candle_brier, delta) in enumerate(
                [(0.03, 0.04, -0.01), (0.07, 0.06, 0.01)],
                start=1,
            ):
                capture_dir = input_root / f"capture{idx}"
                capture_dir.mkdir(parents=True)
                write_valid_manifest(capture_dir, f"M{idx}")
                (capture_dir / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
                    json.dumps(
                        {
                            "summary": {
                                "diagnostic_ready": True,
                                "promotion_allowed": False,
                                "candidate_ready_for_predeclared_shadow": False,
                                "joined_rows": 1,
                                "joined_markets": 1,
                                "issue_count": 0,
                                "tick_brownian_delta_brier_vs_candle": delta,
                                "tick_brownian_delta_logloss_vs_candle": -0.02,
                            },
                            "diagnostic_rows": [
                                diagnostic_row(f"M{idx}", tick_brier, candle_brier)
                            ],
                        }
                    ),
                    encoding="utf-8",
                )

            summary, model_rows, diagnostic_rows = build_paired_sidecar_spot_aggregate(
                input_root=input_root,
                output_json=root / "aggregate.json",
                output_md=root / "aggregate.md",
                min_rows_for_shadow=200,
                min_markets_for_shadow=40,
            )

        by_model = {row["model"]: row for row in model_rows}
        self.assertTrue(summary.diagnostic_ready)
        self.assertFalse(summary.promotion_allowed)
        self.assertFalse(summary.candidate_ready_for_predeclared_shadow)
        self.assertEqual(summary.diagnostic_file_count, 2)
        self.assertEqual(summary.skipped_diagnostic_count, 0)
        self.assertEqual(summary.ready_diagnostic_count, 2)
        self.assertEqual(summary.joined_rows, 2)
        self.assertEqual(summary.joined_markets, 2)
        self.assertEqual(summary.rows_remaining_for_shadow, 198)
        self.assertEqual(summary.markets_remaining_for_shadow, 38)
        self.assertEqual(summary.tick_brownian_better_brier_capture_count, 1)
        self.assertEqual(summary.tick_brownian_better_logloss_capture_count, 2)
        self.assertEqual(summary.best_model_by_brier, "v28")
        self.assertIn("source_capture_id", diagnostic_rows[0])
        self.assertAlmostEqual(by_model["tick_brownian"]["brier"], 0.05)
        self.assertAlmostEqual(summary.tick_brownian_delta_brier_vs_candle or 0.0, 0.0)

    def test_paired_sidecar_spot_aggregate_skips_invalid_manifest_diagnostics(self) -> None:
        def diagnostic_row(market: str, brier: float) -> dict[str, object]:
            row: dict[str, object] = {"market_ticker": market, "row_id": f"{market}-row"}
            for model in ("candidate", "v28", "candle_brownian", "tick_brownian", "market_side_ask"):
                row[f"{model}_brier"] = brier
                row[f"{model}_logloss"] = brier
                row[f"{model}_side_ev_cents"] = 1.0
                row[f"{model}_side_pnl_if_selected_cents"] = 1.0
            return row

        def write_diagnostic(capture_dir: Path, market: str, brier: float) -> None:
            (capture_dir / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "diagnostic_ready": True,
                            "promotion_allowed": False,
                            "joined_rows": 1,
                            "joined_markets": 1,
                            "issue_count": 0,
                            "tick_brownian_delta_brier_vs_candle": -0.01,
                            "tick_brownian_delta_logloss_vs_candle": -0.01,
                        },
                        "diagnostic_rows": [diagnostic_row(market, brier)],
                    }
                ),
                encoding="utf-8",
            )

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            valid_dir = input_root / "valid"
            invalid_dir = input_root / "invalid"
            valid_dir.mkdir(parents=True)
            invalid_dir.mkdir(parents=True)
            (valid_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "valid",
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {"market_ticker": "VALID", "market_close_ts_utc": "2026-05-11T12:15:00Z"}
                        ],
                        "alignment_rows": [
                            {"market_ticker": "VALID", "decision_ts_utc": "2026-05-11T12:00:00Z"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (invalid_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "invalid",
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                        },
                        "sidecar_batch_summary": {"mode": "fixture"},
                        "sidecar_batch_markets": [],
                        "alignment_rows": [],
                    }
                ),
                encoding="utf-8",
            )
            write_diagnostic(valid_dir, "VALID", 0.01)
            write_diagnostic(invalid_dir, "INVALID", 0.99)

            summary, _model_rows, diagnostic_rows = build_paired_sidecar_spot_aggregate(
                input_root=input_root,
                output_json=root / "aggregate.json",
                output_md=root / "aggregate.md",
            )

        self.assertEqual(summary.diagnostic_file_count, 2)
        self.assertEqual(summary.skipped_diagnostic_count, 1)
        self.assertEqual(summary.ready_diagnostic_count, 1)
        self.assertEqual(summary.joined_rows, 1)
        self.assertEqual({row["market_ticker"] for row in diagnostic_rows}, {"VALID"})

    def test_paired_sidecar_spot_aggregate_reports_equal_market_best_model(self) -> None:
        def write_manifest(capture_dir: Path, market: str) -> None:
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": capture_dir.name,
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {"market_ticker": market, "market_close_ts_utc": "2026-05-11T12:15:00Z"}
                        ],
                        "alignment_rows": [
                            {"market_ticker": market, "decision_ts_utc": "2026-05-11T12:00:00Z"}
                        ],
                    }
                ),
                encoding="utf-8",
            )

        def row(market: str, row_id: str, candidate_brier: float, v28_brier: float) -> dict[str, object]:
            out: dict[str, object] = {"market_ticker": market, "row_id": row_id}
            for model in ("candidate", "v28", "candle_brownian", "tick_brownian", "market_side_ask"):
                brier = candidate_brier if model == "candidate" else v28_brier if model == "v28" else 0.8
                out[f"{model}_brier"] = brier
                out[f"{model}_logloss"] = brier
                out[f"{model}_side_ev_cents"] = 1.0
                out[f"{model}_side_pnl_if_selected_cents"] = 1.0
            return out

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            repeated_dir = input_root / "repeated_market"
            single_dir = input_root / "single_market"
            repeated_dir.mkdir(parents=True)
            single_dir.mkdir(parents=True)
            write_manifest(repeated_dir, "MANY_ROWS")
            write_manifest(single_dir, "ONE_ROW")
            (repeated_dir / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
                json.dumps(
                    {
                        "summary": {"diagnostic_ready": True, "joined_rows": 10, "joined_markets": 1},
                        "diagnostic_rows": [
                            row("MANY_ROWS", f"many-{idx}", candidate_brier=0.0, v28_brier=0.9)
                            for idx in range(10)
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (single_dir / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
                json.dumps(
                    {
                        "summary": {"diagnostic_ready": True, "joined_rows": 1, "joined_markets": 1},
                        "diagnostic_rows": [
                            row("ONE_ROW", "one-1", candidate_brier=1.0, v28_brier=0.0)
                        ],
                    }
                ),
                encoding="utf-8",
            )

            summary, _model_rows, _diagnostic_rows = build_paired_sidecar_spot_aggregate(
                input_root=input_root,
                output_json=root / "aggregate.json",
                output_md=root / "aggregate.md",
            )

        self.assertEqual(summary.best_model_by_brier, "candidate")
        self.assertEqual(summary.best_model_by_logloss, "candidate")
        self.assertEqual(summary.market_equal_best_model_by_brier, "v28")
        self.assertEqual(summary.market_equal_best_model_by_logloss, "v28")

    def test_paired_sidecar_online_calibration_is_label_gated_by_market_close(self) -> None:
        def write_manifest(capture_dir: Path, market: str, close_ts: str, decision_ts: str) -> None:
            capture_dir.mkdir(parents=True)
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": capture_dir.name,
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                            "promotion_allowed": False,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {"market_ticker": market, "market_close_ts_utc": close_ts}
                        ],
                        "alignment_rows": [
                            {"market_ticker": market, "decision_ts_utc": decision_ts}
                        ],
                    }
                ),
                encoding="utf-8",
            )

        def aggregate_row(capture_id: str, market: str, decision_ts: str) -> dict[str, object]:
            row: dict[str, object] = {
                "source_capture_id": capture_id,
                "row_id": f"{market}-row",
                "market_ticker": market,
                "decision_ts_utc": decision_ts,
                "side": "yes",
                "ask_cents": 50.0,
                "y_yes_win": 0,
                "candidate_p_yes": 0.99,
                "v28_p_yes": 0.5,
                "candle_brownian_p_yes": 0.5,
                "tick_brownian_p_yes": 0.5,
                "market_side_ask_p_yes": 0.5,
            }
            return row

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            write_manifest(
                input_root / "capture1",
                "M1",
                "2026-05-11T12:15:00Z",
                "2026-05-11T12:00:00Z",
            )
            write_manifest(
                input_root / "capture2",
                "M2",
                "2026-05-11T12:30:00Z",
                "2026-05-11T12:16:00Z",
            )
            aggregate_json = root / "aggregate.json"
            aggregate_json.write_text(
                json.dumps(
                    {
                        "diagnostic_rows": [
                            aggregate_row("capture1", "M1", "2026-05-11T12:00:00Z"),
                            aggregate_row("capture2", "M2", "2026-05-11T12:16:00Z"),
                        ]
                    }
                ),
                encoding="utf-8",
            )

            summary, model_rows, _market_equal_rows, calibrated_rows, market_model_rows = (
                build_paired_sidecar_online_calibration(
                input_root=input_root,
                input_aggregate_json=aggregate_json,
                output_json=root / "online.json",
                output_md=root / "online.md",
                )
            )

        by_model = {row["model"]: row for row in model_rows}
        by_market_model = {
            (row["market_ticker"], row["model"]): row for row in market_model_rows
        }
        first, second = calibrated_rows
        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(summary.prepared_rows, 2)
        self.assertEqual(summary.issue_count, 0)
        self.assertEqual(summary.market_count_for_stability, 2)
        self.assertTrue(summary.best_blend_model_by_market_equal_brier.startswith("blend_"))
        self.assertGreater(first["online_logit_candidate_lr030_market_mean_p_yes"], 0.98)
        self.assertLess(
            second["online_logit_candidate_lr030_market_mean_p_yes"],
            first["online_logit_candidate_lr030_market_mean_p_yes"],
        )
        self.assertLess(
            by_model["online_logit_candidate_lr030_market_mean"]["brier"],
            by_model["candidate_raw"]["brier"],
        )
        self.assertIn(("M1", "candidate_raw"), by_market_model)
        self.assertIn(("M1", summary.best_blend_model_by_market_equal_brier), by_market_model)

    def test_paired_sidecar_blend_failure_analysis_is_diagnostic_only(self) -> None:
        def write_manifest(capture_dir: Path, market: str, close_ts: str) -> None:
            capture_dir.mkdir(parents=True)
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": capture_dir.name,
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                            "promotion_allowed": False,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {"market_ticker": market, "market_close_ts_utc": close_ts}
                        ],
                    }
                ),
                encoding="utf-8",
            )

        def aggregate_row(
            capture_id: str,
            market: str,
            row_num: int,
            decision_ts: str,
            y_yes_win: int,
            candidate_p: float,
            v28_p: float,
            candle_p: float,
        ) -> dict[str, object]:
            return {
                "source_capture_id": capture_id,
                "row_id": f"{market}-row-{row_num}",
                "market_ticker": market,
                "decision_ts_utc": decision_ts,
                "side": "yes" if row_num % 2 == 0 else "no",
                "ask_cents": 50.0,
                "y_yes_win": y_yes_win,
                "candidate_p_yes": candidate_p,
                "v28_p_yes": v28_p,
                "candle_brownian_p_yes": candle_p,
                "tick_brownian_p_yes": candle_p,
                "market_side_ask_p_yes": 0.5,
                "independent_spot_age_ms": 250.0 + row_num,
                "spot_delta_bps": 0.5 + row_num,
            }

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            write_manifest(input_root / "capture1", "M1", "2026-05-11T12:15:00Z")
            write_manifest(input_root / "capture2", "M2", "2026-05-11T12:30:00Z")
            diagnostic_rows = [
                aggregate_row("capture1", "M1", 0, "2026-05-11T12:00:00Z", 1, 0.80, 0.65, 0.55),
                aggregate_row("capture1", "M1", 1, "2026-05-11T12:01:00Z", 1, 0.70, 0.60, 0.55),
                aggregate_row("capture2", "M2", 2, "2026-05-11T12:16:00Z", 0, 0.25, 0.35, 0.45),
                aggregate_row("capture2", "M2", 3, "2026-05-11T12:17:00Z", 0, 0.30, 0.40, 0.45),
            ]
            aggregate_json = root / "aggregate.json"
            aggregate_json.write_text(json.dumps({"diagnostic_rows": diagnostic_rows}), encoding="utf-8")
            online_summary, model_rows, market_equal_rows, calibrated_rows, market_model_rows = (
                build_paired_sidecar_online_calibration(
                    input_root=input_root,
                    input_aggregate_json=aggregate_json,
                    output_json=root / "online.json",
                    output_md=root / "online.md",
                )
            )
            online_json = root / "online.json"
            online_json.write_text(
                json.dumps(
                    {
                        "summary": asdict(online_summary),
                        "model_rows": model_rows,
                        "market_equal_model_rows": market_equal_rows,
                        "calibrated_rows": calibrated_rows,
                        "market_model_rows": market_model_rows,
                    }
                ),
                encoding="utf-8",
            )

            report = build_paired_sidecar_blend_failure_analysis(
                online_calibration_json=online_json,
                aggregate_json=aggregate_json,
                output_json=root / "failure.json",
                output_md=root / "failure.md",
            )

        self.assertFalse(report.promotion_allowed)
        self.assertFalse(report.promotion_safe)
        self.assertEqual(report.rows, 4)
        self.assertEqual(report.markets, 2)
        self.assertIn("blend_v28_online_lr010_w25", report.focus_models)
        self.assertTrue(
            any(
                row.model == "blend_v28_online_lr010_w25" and row.baseline == "candle_brownian"
                for row in report.comparisons
            )
        )
        self.assertTrue(any(row.slice_type == "spot_age_band" for row in report.slice_rows))
        self.assertIn("Post-hoc diagnostic only", report.conclusion)

    def test_paired_sidecar_slice_oos_excludes_rows_at_or_before_lock(self) -> None:
        def calibrated_row(
            row_id: str,
            market: str,
            decision_ts: str,
            label_ts: str,
            y_yes_win: int,
            model_p: float,
        ) -> dict[str, object]:
            row: dict[str, object] = {
                "row_id": row_id,
                "source_capture_id": "capture",
                "market_ticker": market,
                "decision_ts_utc": decision_ts,
                "label_available_ts_utc": label_ts,
                "side": "yes",
                "ask_cents": 50.0,
                "y_yes_win": y_yes_win,
                "blend_v28_online_lr010_w20_p_yes": model_p,
                "v28_p_yes": 0.60,
                "market_side_ask_p_yes": 0.55,
                "candle_brownian_p_yes": 0.50,
            }
            return row

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            online_json = root / "online.json"
            aggregate_json = root / "aggregate.json"
            plan_json = root / "plan.json"
            online_json.write_text(
                json.dumps(
                    {
                        "calibrated_rows": [
                            calibrated_row(
                                "old-row",
                                "OLD",
                                "2026-05-12T11:00:00Z",
                                "2026-05-12T11:15:00Z",
                                1,
                                0.99,
                            ),
                            calibrated_row(
                                "future-row-1",
                                "NEW1",
                                "2026-05-12T12:01:00Z",
                                "2026-05-12T12:15:00Z",
                                1,
                                0.90,
                            ),
                            calibrated_row(
                                "future-row-2",
                                "NEW2",
                                "2026-05-12T12:16:00Z",
                                "2026-05-12T12:30:00Z",
                                0,
                                0.20,
                            ),
                        ]
                    }
                ),
                encoding="utf-8",
            )
            aggregate_json.write_text(json.dumps({"diagnostic_rows": []}), encoding="utf-8")
            plan_json.write_text(
                json.dumps(
                    {
                        "hypothesis_id": "unit_slice",
                        "evaluation_scope": "locked_forward_shadow",
                        "model": "blend_v28_online_lr010_w20",
                        "slice_type": "time_to_close_band",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "fee_cents": 1.5,
                        "assumed_fill_probability": 1.0,
                        "no_fill_penalty_cents": 0.0,
                        "baseline_models": ["v28", "market_side_ask", "candle_brownian"],
                        "gate_config": asdict(
                            PairedSidecarSliceGateConfig(
                                min_fresh_candidate_rows=2,
                                min_fresh_markets=2,
                                min_slice_rows=2,
                                min_slice_markets=2,
                                min_selected_count=1,
                                require_positive_ev_rank=False,
                                require_beats_baseline_selected_pnl=False,
                            )
                        ),
                    }
                ),
                encoding="utf-8",
            )

            report = evaluate_paired_sidecar_slice_oos(
                online_calibration_json=online_json,
                aggregate_json=aggregate_json,
                output_dir=root,
                plan_json=plan_json,
            )

        self.assertFalse(report.promotion_allowed)
        self.assertEqual(report.total_input_rows, 3)
        self.assertEqual(report.fresh_candidate_rows, 2)
        self.assertEqual(report.slice_rows, 2)
        self.assertEqual(report.slice_markets, 2)
        self.assertEqual(report.selected_metrics.selected_count, 1)
        self.assertAlmostEqual(report.selected_metrics.selected_pnl_cents, 48.5)

    def test_paired_sidecar_slice_locked_plan_freezes_research_only_hypothesis(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "failure.json"
            source.write_text('{"schema_version":"unit"}', encoding="utf-8")
            plan = build_paired_sidecar_slice_locked_plan(
                run_id="UNITLOCK",
                locked_after_utc="2026-05-12T12:00:00Z",
                hypothesis_id="unit_hypothesis",
                model="blend_v28_online_lr010_w20",
                slice_type="time_to_close_band",
                bucket="600s_plus",
                fee_cents=1.5,
                assumed_fill_probability=1.0,
                no_fill_penalty_cents=0.0,
                baseline_models=("v28", "market_side_ask", "candle_brownian"),
                selection_source_json=source,
                gate_config=PairedSidecarSliceGateConfig(min_fresh_candidate_rows=2),
            )

        self.assertEqual(plan.evaluation_scope, "locked_forward_shadow")
        self.assertEqual(plan.run_id, "UNITLOCK")
        self.assertEqual(plan.model, "blend_v28_online_lr010_w20")
        self.assertEqual(plan.slice_type, "time_to_close_band")
        self.assertIn("--collect-mode public-rest", plan.capture_command_template)
        self.assertTrue(any("research-only" in note.lower() for note in plan.notes))
        self.assertTrue(plan.selection_source_sha256)

    def test_paired_sidecar_slice_refresh_does_not_collect_by_default(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "pairs"
            capture_dir = input_root / "capture"
            capture_dir.mkdir(parents=True)
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "capture",
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                            "promotion_allowed": False,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {
                                "market_ticker": "M1",
                                "market_close_ts_utc": "2026-05-12T12:15:00Z",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            aggregate_json = root / "aggregate.json"
            aggregate_json.write_text(
                json.dumps(
                    {
                        "diagnostic_rows": [
                            {
                                "source_capture_id": "capture",
                                "row_id": "row-1",
                                "market_ticker": "M1",
                                "decision_ts_utc": "2026-05-12T12:01:00Z",
                                "side": "yes",
                                "ask_cents": 50.0,
                                "y_yes_win": 1,
                                "candidate_p_yes": 0.80,
                                "v28_p_yes": 0.65,
                                "candle_brownian_p_yes": 0.55,
                                "tick_brownian_p_yes": 0.55,
                                "market_side_ask_p_yes": 0.50,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            plan_json = root / "plan.json"
            plan_json.write_text(
                json.dumps(
                    {
                        "hypothesis_id": "unit_slice",
                        "evaluation_scope": "locked_forward_shadow",
                        "model": "blend_v28_online_lr010_w20",
                        "slice_type": "time_to_close_band",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T13:00:00Z",
                        "fee_cents": 1.5,
                        "assumed_fill_probability": 1.0,
                        "no_fill_penalty_cents": 0.0,
                        "baseline_models": ["v28", "market_side_ask", "candle_brownian"],
                        "gate_config": asdict(PairedSidecarSliceGateConfig()),
                    }
                ),
                encoding="utf-8",
            )

            summary = refresh_paired_sidecar_slice_status(
                plan_json=plan_json,
                input_root=input_root,
                packet_csv=root / "packets.csv",
                labeled_csv=root / "labels.csv",
                refresh_json=root / "refresh.json",
                refresh_md=root / "refresh.md",
                aggregate_json=aggregate_json,
                online_json=root / "online.json",
                online_md=root / "online.md",
                failure_json=root / "failure.json",
                failure_md=root / "failure.md",
                slice_report_dir=root,
                output_json=root / "slice_refresh.json",
                output_md=root / "slice_refresh.md",
                write=False,
                fetch_labels=False,
                refresh_goal_audit=False,
            )

        self.assertFalse(summary.collect_requested)
        self.assertEqual(summary.collect_status, "not_requested")
        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(summary.online_prepared_rows, 1)
        self.assertEqual(summary.slice_fresh_candidate_rows, 0)
        self.assertFalse(summary.slice_promotion_safe)

    def test_paired_sidecar_slice_refresh_updates_multiple_locked_plans(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            aggregate_json = root / "aggregate.json"
            aggregate_json.write_text(
                json.dumps(
                    {
                        "diagnostic_rows": [
                            {
                                "source_capture_id": "capture",
                                "row_id": "row-1",
                                "market_ticker": "M1",
                                "decision_ts_utc": "2026-05-12T12:01:00Z",
                                "label_available_ts_utc": "2026-05-12T12:15:00Z",
                                "seconds_to_close": 700.0,
                                "side": "yes",
                                "ask_cents": 50.0,
                                "y_yes_win": 1,
                                "candidate_p_yes": 0.80,
                                "v28_p_yes": 0.65,
                                "candle_brownian_p_yes": 0.55,
                                "tick_brownian_p_yes": 0.55,
                                "market_side_ask_p_yes": 0.50,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            gate_config = asdict(
                PairedSidecarSliceGateConfig(
                    min_fresh_candidate_rows=1,
                    min_fresh_markets=1,
                    min_slice_rows=1,
                    min_slice_markets=1,
                    min_selected_count=1,
                )
            )
            plan_one = root / "paired_sidecar_slice_PSLICELOCKA_locked_plan.json"
            plan_one.write_text(
                json.dumps(
                    {
                        "run_id": "PSLICELOCKA",
                        "hypothesis_id": "unit_v28",
                        "evaluation_scope": "locked_forward_shadow",
                        "model": "v28",
                        "slice_type": "time_to_close_band",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "fee_cents": 1.5,
                        "assumed_fill_probability": 1.0,
                        "no_fill_penalty_cents": 0.0,
                        "baseline_models": ["market_side_ask", "candle_brownian"],
                        "gate_config": gate_config,
                    }
                ),
                encoding="utf-8",
            )
            plan_two = root / "paired_sidecar_slice_PSLICELOCKB_locked_plan.json"
            plan_two.write_text(
                json.dumps(
                    {
                        "run_id": "PSLICELOCKB",
                        "hypothesis_id": "unit_market",
                        "evaluation_scope": "locked_forward_shadow",
                        "model": "market_side_ask",
                        "slice_type": "time_to_close_band",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "fee_cents": 1.5,
                        "assumed_fill_probability": 1.0,
                        "no_fill_penalty_cents": 0.0,
                        "baseline_models": ["v28", "candle_brownian"],
                        "gate_config": gate_config,
                    }
                ),
                encoding="utf-8",
            )

            summary = refresh_paired_sidecar_slice_status(
                plan_json=plan_one,
                plan_jsons=[plan_two],
                input_root=root / "pairs",
                packet_csv=root / "packets.csv",
                labeled_csv=root / "labels.csv",
                refresh_json=root / "refresh.json",
                refresh_md=root / "refresh.md",
                aggregate_json=aggregate_json,
                online_json=root / "online.json",
                online_md=root / "online.md",
                failure_json=root / "failure.json",
                failure_md=root / "failure.md",
                slice_report_dir=root,
                output_json=root / "slice_refresh.json",
                output_md=root / "slice_refresh.md",
                write=True,
                fetch_labels=False,
                refresh_goal_audit=False,
            )

            self.assertEqual(summary.slice_report_count, 2)
            self.assertEqual(
                [item["hypothesis_id"] for item in summary.slice_reports],
                ["unit_v28", "unit_market"],
            )
            self.assertTrue((root / "paired_sidecar_slice_oos_PSLICELOCKA_latest.json").exists())
            self.assertTrue((root / "paired_sidecar_slice_oos_PSLICELOCKB_latest.json").exists())
            self.assertFalse(summary.collect_requested)
            self.assertFalse(summary.promotion_allowed)

    def test_paired_sidecar_slice_pending_preview_counts_outcome_free_slice_matches(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = root / "pairs" / "pending_run"
            run_dir.mkdir(parents=True)
            (run_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "paired_capture_ready": True,
                        "run_id": "pending_run",
                        "sidecar_batch_markets": [
                            {"market_close_ts_utc": "2026-05-12T19:15:00Z"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "sidecar_packets_independent_spot_enriched.json").write_text(
                json.dumps(
                    {
                        "enrichment_ready": True,
                        "enriched_packet_rows": 2,
                        "rows": [
                            {
                                "market_ticker": "M1",
                                "decision_ts_utc": "2026-05-12T19:05:00Z",
                                "seconds_to_close": 700.0,
                                "candidate_p_yes": 0.60,
                                "v28_p_yes": 0.52,
                            },
                            {
                                "market_ticker": "M2",
                                "decision_ts_utc": "2026-05-12T19:06:00Z",
                                "seconds_to_close": 500.0,
                                "candidate_p_yes": 0.53,
                                "v28_p_yes": 0.51,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            status = _pending_manifest_status(
                input_root=root / "pairs",
                plan_payloads=[
                    {
                        "hypothesis_id": "time_lock",
                        "model": "v28",
                        "slice_type": "time_to_close_band",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T19:00:00Z",
                    },
                    {
                        "hypothesis_id": "gap_lock",
                        "model": "blend_v28_online_lr010_w15",
                        "slice_type": "candidate_v28_disagreement_band",
                        "bucket": "05_15pp",
                        "locked_after_utc": "2026-05-12T19:00:00Z",
                    },
                ],
            )

            previews = {item["hypothesis_id"]: item for item in status["pending_slice_previews"]}
            self.assertEqual(status["pending_manifest_count"], 1)
            self.assertEqual(status["pending_enriched_rows"], 2)
            self.assertEqual(previews["time_lock"]["pending_slice_rows"], 1)
            self.assertEqual(previews["time_lock"]["pending_slice_markets"], 1)
            self.assertEqual(previews["gap_lock"]["pending_slice_rows"], 1)
            self.assertEqual(previews["gap_lock"]["pending_slice_markets"], 1)
            self.assertTrue(previews["gap_lock"]["outcome_free"])

    def test_paired_sidecar_slice_lock_comparison_blocks_positive_pnl_without_v28_edge(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "reports"
            report_dir.mkdir()
            selected = {
                "avg_pnl_per_selected_cents": 10.0,
                "brier": 0.040,
                "ev_rank_correlation": 0.8,
                "logloss": 0.200,
                "markets": 1,
                "mean_ev_cents": 2.0,
                "model": "blend_v28_online_lr010_w05",
                "positive_selected_market_count": 1,
                "positive_top_ev_market_count": 1,
                "rows": 18,
                "selected_count": 9,
                "selected_pnl_cents": 90.0,
                "top_ev_bucket_count": 4,
                "top_ev_bucket_pnl_cents": 20.0,
            }
            v28 = {
                **selected,
                "model": "v28",
                "brier": 0.030,
                "logloss": 0.180,
                "selected_pnl_cents": 90.0,
                "top_ev_bucket_pnl_cents": 25.0,
            }
            payload = {
                "hypothesis_id": "unit_blend",
                "model": "blend_v28_online_lr010_w05",
                "bucket": "600s_plus",
                "locked_after_utc": "2026-05-12T12:00:00Z",
                "promotion_allowed": False,
                "promotion_safe": False,
                "fresh_candidate_rows": 18,
                "fresh_markets": 1,
                "slice_rows": 18,
                "slice_markets": 1,
                "selected_metrics": selected,
                "baseline_metrics": [v28],
            }
            (report_dir / "paired_sidecar_slice_oos_PSLICELOCKU_latest.json").write_text(
                json.dumps(payload),
                encoding="utf-8",
            )

            comparison = build_slice_lock_comparison(
                report_dir=report_dir,
                output_json=root / "comparison.json",
                output_md=root / "comparison.md",
            )
            write_slice_lock_comparison(comparison)

            self.assertEqual(comparison.report_count, 1)
            self.assertEqual(comparison.particle_like_count, 1)
            self.assertEqual(comparison.particle_edge_candidate_count, 0)
            self.assertEqual(comparison.best_selected_pnl_hypothesis_id, "unit_blend")
            row = comparison.rows[0]
            self.assertGreater(row.selected_pnl_cents, 0)
            self.assertFalse(row.beats_v28_brier)
            self.assertFalse(row.beats_v28_logloss)
            self.assertFalse(row.particle_edge_candidate)
            self.assertTrue((root / "comparison.json").exists())
            self.assertTrue((root / "comparison.md").exists())

    def test_paired_sidecar_slice_lock_comparison_ignores_empty_locks_for_best_pnl(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "reports"
            report_dir.mkdir()
            nonempty_selected = {
                "avg_pnl_per_selected_cents": -10.0,
                "brier": 0.040,
                "ev_rank_correlation": -0.2,
                "logloss": 0.200,
                "markets": 1,
                "mean_ev_cents": -2.0,
                "model": "blend_v28_online_lr010_w15",
                "positive_selected_market_count": 0,
                "positive_top_ev_market_count": 0,
                "rows": 18,
                "selected_count": 4,
                "selected_pnl_cents": -40.0,
                "top_ev_bucket_count": 4,
                "top_ev_bucket_pnl_cents": -20.0,
            }
            empty_selected = {
                **nonempty_selected,
                "model": "blend_v28_online_lr010_w20",
                "markets": 0,
                "rows": 0,
                "selected_count": 0,
                "selected_pnl_cents": 0.0,
                "top_ev_bucket_count": 0,
                "top_ev_bucket_pnl_cents": 0.0,
            }
            for stem, payload in {
                "paired_sidecar_slice_oos_PSLICELOCKA_latest.json": {
                    "hypothesis_id": "nonempty_negative",
                    "model": "blend_v28_online_lr010_w15",
                    "bucket": "05_15pp",
                    "locked_after_utc": "2026-05-12T12:00:00Z",
                    "promotion_allowed": False,
                    "promotion_safe": False,
                    "fresh_candidate_rows": 18,
                    "fresh_markets": 1,
                    "slice_rows": 18,
                    "slice_markets": 1,
                    "selected_metrics": nonempty_selected,
                    "baseline_metrics": [],
                },
                "paired_sidecar_slice_oos_PSLICELOCKB_latest.json": {
                    "hypothesis_id": "empty_zero",
                    "model": "blend_v28_online_lr010_w20",
                    "bucket": "05_15pp",
                    "locked_after_utc": "2026-05-12T12:05:00Z",
                    "promotion_allowed": False,
                    "promotion_safe": False,
                    "fresh_candidate_rows": 0,
                    "fresh_markets": 0,
                    "slice_rows": 0,
                    "slice_markets": 0,
                    "selected_metrics": empty_selected,
                    "baseline_metrics": [],
                },
            }.items():
                (report_dir / stem).write_text(json.dumps(payload), encoding="utf-8")

            comparison = build_slice_lock_comparison(
                report_dir=report_dir,
                output_json=root / "comparison.json",
                output_md=root / "comparison.md",
            )

            self.assertEqual(comparison.report_count, 2)
            self.assertEqual(comparison.best_selected_pnl_hypothesis_id, "nonempty_negative")
            self.assertEqual(comparison.best_selected_pnl_cents, -40.0)

    def test_paired_sidecar_slice_market_breakdown_finds_worst_particle_market(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan_dir = root / "plans"
            plan_dir.mkdir()
            online_json = root / "online.json"
            online_json.write_text(
                json.dumps(
                    {
                        "calibrated_rows": [
                            {
                                "source_capture_id": "cap",
                                "row_id": "r1",
                                "market_ticker": "M1",
                                "decision_ts_utc": "2026-05-12T12:01:00Z",
                                "label_available_ts_utc": "2026-05-12T12:12:40Z",
                                "side": "yes",
                                "ask_cents": 50.0,
                                "y_yes_win": 0,
                                "blend_v28_online_lr010_w05_p_yes": 0.90,
                                "v28_p_yes": 0.80,
                            },
                            {
                                "source_capture_id": "cap",
                                "row_id": "r2",
                                "market_ticker": "M2",
                                "decision_ts_utc": "2026-05-12T12:02:00Z",
                                "label_available_ts_utc": "2026-05-12T12:13:40Z",
                                "side": "yes",
                                "ask_cents": 50.0,
                                "y_yes_win": 1,
                                "blend_v28_online_lr010_w05_p_yes": 0.90,
                                "v28_p_yes": 0.80,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            aggregate_json = root / "aggregate.json"
            aggregate_json.write_text(
                json.dumps(
                    {
                        "diagnostic_rows": [
                            {
                                "source_capture_id": "cap",
                                "row_id": "r1",
                                "independent_spot_age_ms": 100.0,
                                "spot_delta_bps": 1.0,
                            },
                            {
                                "source_capture_id": "cap",
                                "row_id": "r2",
                                "independent_spot_age_ms": 100.0,
                                "spot_delta_bps": 1.0,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            plan_json = plan_dir / "paired_sidecar_slice_PSLICELOCKU_locked_plan.json"
            plan_json.write_text(
                json.dumps(
                    {
                        "hypothesis_id": "unit_blend",
                        "evaluation_scope": "locked_forward_shadow",
                        "model": "blend_v28_online_lr010_w05",
                        "slice_type": "time_to_close_band",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "fee_cents": 1.5,
                        "assumed_fill_probability": 1.0,
                        "no_fill_penalty_cents": 0.0,
                        "gate_config": asdict(PairedSidecarSliceGateConfig()),
                    }
                ),
                encoding="utf-8",
            )

            report = build_slice_market_breakdown(
                plan_dir=plan_dir,
                online_calibration_json=online_json,
                aggregate_json=aggregate_json,
                output_json=root / "market_breakdown.json",
                output_md=root / "market_breakdown.md",
            )
            write_slice_market_breakdown(report)

            self.assertEqual(report.plan_count, 1)
            self.assertEqual(report.row_count, 2)
            self.assertEqual(report.particle_like_negative_market_count, 1)
            self.assertEqual(report.worst_particle_market_ticker, "M1")
            self.assertLess(report.worst_particle_selected_pnl_cents, 0)
            self.assertTrue((root / "market_breakdown.json").exists())
            self.assertTrue((root / "market_breakdown.md").exists())

    def test_paired_sidecar_slice_stability_blocks_concentrated_positive_pnl(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            market_breakdown_json = root / "market_breakdown.json"
            market_breakdown_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_blend",
                                "model": "blend_v28_online_lr010_w05",
                                "bucket": "600s_plus",
                                "market_ticker": "M1",
                                "selected_pnl_cents": 300.0,
                                "top_ev_bucket_pnl_cents": 50.0,
                                "selected_pnl_delta_vs_v28_cents": 10.0,
                                "top_ev_pnl_delta_vs_v28_cents": -5.0,
                                "brier_delta_vs_v28": 0.010,
                                "logloss_delta_vs_v28": 0.020,
                            },
                            {
                                "hypothesis_id": "unit_blend",
                                "model": "blend_v28_online_lr010_w05",
                                "bucket": "600s_plus",
                                "market_ticker": "M2",
                                "selected_pnl_cents": -20.0,
                                "top_ev_bucket_pnl_cents": -10.0,
                                "selected_pnl_delta_vs_v28_cents": 0.0,
                                "top_ev_pnl_delta_vs_v28_cents": -5.0,
                                "brier_delta_vs_v28": 0.005,
                                "logloss_delta_vs_v28": 0.010,
                            },
                            {
                                "hypothesis_id": "v28_control",
                                "model": "v28",
                                "bucket": "600s_plus",
                                "market_ticker": "M1",
                                "selected_pnl_cents": 290.0,
                                "top_ev_bucket_pnl_cents": 55.0,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = build_slice_stability_report(
                market_breakdown_json=market_breakdown_json,
                output_json=root / "stability.json",
                output_md=root / "stability.md",
                min_markets=2,
                max_abs_market_pnl_share=0.40,
            )
            write_slice_stability_report(report)
            rows_by_id = {row.hypothesis_id: row for row in report.rows}
            blend = rows_by_id["unit_blend"]

            self.assertEqual(report.particle_like_count, 1)
            self.assertEqual(report.particle_like_stability_screen_pass_count, 0)
            self.assertEqual(blend.selected_pnl_cents, 280.0)
            self.assertIn("concentrated_market_pnl", blend.stability_warnings)
            self.assertIn("worse_or_equal_top_ev_vs_v28", blend.stability_warnings)
            self.assertIn("worse_or_equal_brier_vs_v28", blend.stability_warnings)
            self.assertFalse(blend.stability_screen_pass)
            self.assertTrue((root / "stability.json").exists())
            self.assertTrue((root / "stability.md").exists())

    def test_paired_sidecar_slice_trajectory_blocks_stale_recent_underperformance(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            market_breakdown_json = root / "market_breakdown.json"
            rows = []
            for ticker, pnl, delta in [
                ("KXBTC15M-26MAY121200-00", 300.0, 250.0),
                ("KXBTC15M-26MAY121215-15", 200.0, 100.0),
                ("KXBTC15M-26MAY121230-30", -50.0, -80.0),
                ("KXBTC15M-26MAY121245-45", -75.0, -90.0),
            ]:
                rows.append(
                    {
                        "hypothesis_id": "unit_blend",
                        "model": "blend_v28_online_lr010_w05",
                        "bucket": "600s_plus",
                        "market_ticker": ticker,
                        "selected_pnl_cents": pnl,
                        "selected_pnl_delta_vs_v28_cents": delta,
                    }
                )
            market_breakdown_json.write_text(json.dumps({"rows": rows}), encoding="utf-8")

            report = build_slice_trajectory_report(
                market_breakdown_json=market_breakdown_json,
                output_json=root / "trajectory.json",
                output_md=root / "trajectory.md",
                min_markets=4,
                recent_market_count=2,
            )
            write_slice_trajectory_report(report)
            row = report.rows[0]

            self.assertEqual(report.particle_like_trajectory_screen_pass_count, 0)
            self.assertEqual(row.selected_pnl_cents, 375.0)
            self.assertEqual(row.last_n_selected_pnl_cents, -125.0)
            self.assertEqual(row.last_n_selected_pnl_delta_vs_v28_cents, -170.0)
            self.assertIn("nonpositive_recent_pnl", row.trajectory_warnings)
            self.assertIn("nonpositive_recent_delta_vs_v28", row.trajectory_warnings)
            self.assertFalse(row.trajectory_screen_pass)
            self.assertTrue((root / "trajectory.json").exists())
            self.assertTrue((root / "trajectory.md").exists())

    def test_paired_sidecar_slice_promotion_readiness_combines_all_vetoes(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            comparison_json = root / "comparison.json"
            stability_json = root / "stability.json"
            trajectory_json = root / "trajectory.json"
            retirement_json = root / "retirement.json"
            comparison_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_positive_but_blocked",
                                "model": "blend_v28_online_lr010_w05",
                                "bucket": "600s_plus",
                                "particle_like_model": True,
                                "selected_pnl_cents": 100.0,
                                "top_ev_bucket_pnl_cents": 50.0,
                                "v28_brier_delta": -0.01,
                                "v28_logloss_delta": -0.02,
                                "v28_selected_pnl_delta_cents": 5.0,
                                "v28_top_ev_pnl_delta_cents": 2.0,
                                "promotion_safe": True,
                                "particle_edge_candidate": True,
                            },
                            {
                                "hypothesis_id": "unit_control",
                                "model": "v28",
                                "bucket": "600s_plus",
                                "particle_like_model": False,
                                "selected_pnl_cents": 90.0,
                                "top_ev_bucket_pnl_cents": 45.0,
                                "promotion_safe": False,
                                "particle_edge_candidate": False,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            stability_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_positive_but_blocked",
                                "stability_screen_pass": False,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            trajectory_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_positive_but_blocked",
                                "trajectory_screen_pass": False,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            retirement_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_positive_but_blocked",
                                "recommendation": "trajectory_blocked_shadow_only",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = build_slice_promotion_readiness_report(
                comparison_json=comparison_json,
                stability_json=stability_json,
                trajectory_json=trajectory_json,
                retirement_json=retirement_json,
                output_json=root / "readiness.json",
                output_md=root / "readiness.md",
            )
            write_slice_promotion_readiness_report(report)
            rows_by_id = {row.hypothesis_id: row for row in report.rows}
            blocked = rows_by_id["unit_positive_but_blocked"]

            self.assertFalse(report.promotion_allowed)
            self.assertEqual(report.readiness_candidate_count, 0)
            self.assertIn("stability_screen_not_passed", blocked.blockers)
            self.assertIn("trajectory_screen_not_passed", blocked.blockers)
            self.assertIn("retirement_trajectory_blocked_shadow_only", blocked.blockers)
            self.assertIn("control_not_particle_like", rows_by_id["unit_control"].blockers)
            self.assertTrue((root / "readiness.json").exists())
            self.assertTrue((root / "readiness.md").exists())

    def test_paired_sidecar_slice_promotion_readiness_can_flag_broader_audit_candidate(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            comparison_json = root / "comparison.json"
            stability_json = root / "stability.json"
            trajectory_json = root / "trajectory.json"
            retirement_json = root / "retirement.json"
            comparison_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_ready",
                                "model": "blend_v28_online_lr010_w05",
                                "bucket": "600s_plus",
                                "particle_like_model": True,
                                "selected_pnl_cents": 100.0,
                                "top_ev_bucket_pnl_cents": 50.0,
                                "v28_brier_delta": -0.01,
                                "v28_logloss_delta": -0.02,
                                "v28_selected_pnl_delta_cents": 5.0,
                                "v28_top_ev_pnl_delta_cents": 2.0,
                                "promotion_safe": True,
                                "particle_edge_candidate": True,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            stability_json.write_text(
                json.dumps({"rows": [{"hypothesis_id": "unit_ready", "stability_screen_pass": True}]}),
                encoding="utf-8",
            )
            trajectory_json.write_text(
                json.dumps({"rows": [{"hypothesis_id": "unit_ready", "trajectory_screen_pass": True}]}),
                encoding="utf-8",
            )
            retirement_json.write_text(
                json.dumps({"rows": [{"hypothesis_id": "unit_ready", "recommendation": "candidate_for_broader_audit"}]}),
                encoding="utf-8",
            )

            report = build_slice_promotion_readiness_report(
                comparison_json=comparison_json,
                stability_json=stability_json,
                trajectory_json=trajectory_json,
                retirement_json=retirement_json,
                output_json=root / "readiness.json",
                output_md=root / "readiness.md",
            )

            self.assertFalse(report.promotion_allowed)
            self.assertEqual(report.readiness_candidate_count, 1)
            self.assertTrue(report.rows[0].readiness_candidate)
            self.assertEqual(report.rows[0].blockers, ())

    def test_paired_sidecar_slice_retirement_vetoes_negative_forward_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "reports"
            report_dir.mkdir()
            selected = {
                "avg_pnl_per_selected_cents": -20.0,
                "brier": 0.060,
                "ev_rank_correlation": -0.4,
                "logloss": 0.300,
                "markets": 5,
                "mean_ev_cents": -1.0,
                "model": "blend_v28_online_lr010_w15",
                "positive_selected_market_count": 0,
                "positive_top_ev_market_count": 0,
                "rows": 100,
                "selected_count": 10,
                "selected_pnl_cents": -200.0,
                "top_ev_bucket_count": 5,
                "top_ev_bucket_pnl_cents": -100.0,
            }
            v28 = {
                **selected,
                "model": "v28",
                "brier": 0.050,
                "logloss": 0.250,
                "selected_pnl_cents": -50.0,
                "top_ev_bucket_pnl_cents": -40.0,
            }
            (report_dir / "paired_sidecar_slice_oos_PSLICELOCKU_latest.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "unit_negative",
                        "model": "blend_v28_online_lr010_w15",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "promotion_allowed": False,
                        "promotion_safe": False,
                        "fresh_candidate_rows": 100,
                        "fresh_markets": 5,
                        "slice_rows": 100,
                        "slice_markets": 5,
                        "selected_metrics": selected,
                        "baseline_metrics": [v28],
                    }
                ),
                encoding="utf-8",
            )

            report = build_slice_retirement_report(
                report_dir=report_dir,
                output_json=root / "retirement.json",
                output_md=root / "retirement.md",
                min_retire_markets=5,
            )
            write_slice_retirement_report(report)

            self.assertFalse(report.promotion_allowed)
            self.assertEqual(report.retire_count, 1)
            self.assertEqual(report.rows[0].recommendation, "retire_negative_forward_evidence")
            self.assertTrue((root / "retirement.json").exists())
            self.assertTrue((root / "retirement.md").exists())

    def test_paired_sidecar_slice_retirement_uses_stability_block(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "reports"
            report_dir.mkdir()
            selected = {
                "avg_pnl_per_selected_cents": 20.0,
                "brier": 0.060,
                "ev_rank_correlation": 0.1,
                "logloss": 0.300,
                "markets": 6,
                "mean_ev_cents": 1.0,
                "model": "blend_v28_online_lr010_w05",
                "positive_selected_market_count": 3,
                "positive_top_ev_market_count": 2,
                "rows": 100,
                "selected_count": 10,
                "selected_pnl_cents": 200.0,
                "top_ev_bucket_count": 5,
                "top_ev_bucket_pnl_cents": 50.0,
            }
            v28 = {
                **selected,
                "model": "v28",
                "brier": 0.050,
                "logloss": 0.250,
                "selected_pnl_cents": 150.0,
                "top_ev_bucket_pnl_cents": 75.0,
            }
            (report_dir / "paired_sidecar_slice_oos_PSLICELOCKU_latest.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "unit_positive_unstable",
                        "model": "blend_v28_online_lr010_w05",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "promotion_allowed": False,
                        "promotion_safe": False,
                        "fresh_candidate_rows": 100,
                        "fresh_markets": 6,
                        "slice_rows": 100,
                        "slice_markets": 6,
                        "selected_metrics": selected,
                        "baseline_metrics": [v28],
                    }
                ),
                encoding="utf-8",
            )
            stability_json = root / "stability.json"
            stability_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_positive_unstable",
                                "stability_screen_pass": False,
                                "market_count": 6,
                                "positive_market_fraction": 0.50,
                                "max_abs_market_pnl_share": 0.45,
                                "stability_warnings": [
                                    "underpowered_markets",
                                    "concentrated_market_pnl",
                                    "worse_or_equal_top_ev_vs_v28",
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = build_slice_retirement_report(
                report_dir=report_dir,
                output_json=root / "retirement.json",
                output_md=root / "retirement.md",
                stability_json=stability_json,
                min_retire_markets=5,
            )
            row = report.rows[0]

            self.assertEqual(report.stability_blocked_count, 1)
            self.assertEqual(report.continue_shadow_count, 0)
            self.assertEqual(row.recommendation, "stability_blocked_shadow_only")
            self.assertFalse(row.stability_screen_pass)
            self.assertIn("concentrated_market_pnl", row.stability_warnings)

    def test_paired_sidecar_slice_retirement_uses_trajectory_block(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "reports"
            report_dir.mkdir()
            selected = {
                "avg_pnl_per_selected_cents": 20.0,
                "brier": 0.040,
                "ev_rank_correlation": 0.2,
                "logloss": 0.200,
                "markets": 8,
                "mean_ev_cents": 1.0,
                "model": "blend_v28_online_lr010_w05",
                "positive_selected_market_count": 5,
                "positive_top_ev_market_count": 4,
                "rows": 120,
                "selected_count": 12,
                "selected_pnl_cents": 240.0,
                "top_ev_bucket_count": 6,
                "top_ev_bucket_pnl_cents": 120.0,
            }
            v28 = {
                **selected,
                "model": "v28",
                "selected_pnl_cents": 220.0,
                "top_ev_bucket_pnl_cents": 100.0,
            }
            (report_dir / "paired_sidecar_slice_oos_PSLICELOCKU_latest.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "unit_positive_decaying",
                        "model": "blend_v28_online_lr010_w05",
                        "bucket": "600s_plus",
                        "locked_after_utc": "2026-05-12T12:00:00Z",
                        "promotion_allowed": False,
                        "promotion_safe": False,
                        "fresh_candidate_rows": 120,
                        "fresh_markets": 8,
                        "slice_rows": 120,
                        "slice_markets": 8,
                        "selected_metrics": selected,
                        "baseline_metrics": [v28],
                    }
                ),
                encoding="utf-8",
            )
            trajectory_json = root / "trajectory.json"
            trajectory_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "hypothesis_id": "unit_positive_decaying",
                                "trajectory_screen_pass": False,
                                "market_count": 8,
                                "last_n_selected_pnl_cents": -50.0,
                                "last_n_selected_pnl_delta_vs_v28_cents": -75.0,
                                "trajectory_warnings": [
                                    "nonpositive_recent_pnl",
                                    "nonpositive_recent_delta_vs_v28",
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = build_slice_retirement_report(
                report_dir=report_dir,
                output_json=root / "retirement.json",
                output_md=root / "retirement.md",
                trajectory_json=trajectory_json,
                min_retire_markets=5,
            )
            row = report.rows[0]

            self.assertEqual(report.trajectory_blocked_count, 1)
            self.assertEqual(report.continue_shadow_count, 0)
            self.assertEqual(row.recommendation, "trajectory_blocked_shadow_only")
            self.assertFalse(row.trajectory_screen_pass)
            self.assertEqual(row.trajectory_last_n_selected_pnl_cents, -50.0)
            self.assertIn("nonpositive_recent_pnl", row.trajectory_warnings)

    def test_paired_sidecar_spot_refresh_is_research_only_on_empty_input(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            summary, rows = refresh_paired_sidecar_spot_evidence(
                input_root=root / "sidecar_spot_pairs",
                packet_csv=root / "packets.csv",
                labeled_csv=root / "labels.csv",
                output_json=root / "refresh.json",
                output_md=root / "refresh.md",
                write=False,
                refresh_goal_audit=False,
            )

        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(summary.manifest_count, 0)
        self.assertEqual(summary.skipped_manifest_count, 0)
        self.assertEqual(summary.enrichment_ready_count, 0)
        self.assertEqual(summary.diagnostic_ready_count, 0)
        self.assertEqual(summary.pending_diagnostic_count, 0)
        self.assertFalse(summary.aggregate_ready)
        self.assertTrue(summary.aggregate_fresh)
        self.assertEqual(summary.aggregate_rows_remaining_for_shadow, 200)
        self.assertEqual(summary.aggregate_markets_remaining_for_shadow, 40)
        self.assertFalse(summary.label_refresh_requested)
        self.assertEqual(summary.label_refresh_status, "not_requested")
        self.assertFalse(summary.label_refresh_written)
        self.assertFalse(summary.goal_audit_refreshed)
        self.assertFalse(summary.goal_complete)
        self.assertEqual(rows, [])

    def test_paired_sidecar_spot_refresh_writes_current_summary_before_goal_audit(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            def audit_side_effect(_root: Path) -> dict[str, object]:
                refresh_payload = json.loads((root / "refresh.json").read_text(encoding="utf-8"))
                refresh_summary = refresh_payload["summary"]
                self.assertEqual(refresh_summary["manifest_count"], 0)
                self.assertFalse(refresh_summary["goal_audit_refreshed"])
                return {"complete": False}

            with patch(
                "research_particle.paired_sidecar_spot_refresh.particle_goal_audit",
                side_effect=audit_side_effect,
            ) as goal_audit, patch(
                "research_particle.paired_sidecar_spot_refresh.write_particle_goal_audit"
            ) as write_goal_audit:
                summary, rows = refresh_paired_sidecar_spot_evidence(
                    input_root=root / "sidecar_spot_pairs",
                    packet_csv=root / "packets.csv",
                    labeled_csv=root / "labels.csv",
                    output_json=root / "refresh.json",
                    output_md=root / "refresh.md",
                    write=True,
                    refresh_goal_audit=True,
                )

            final_payload = json.loads((root / "refresh.json").read_text(encoding="utf-8"))

        goal_audit.assert_called_once()
        write_goal_audit.assert_called_once_with({"complete": False})
        self.assertTrue(summary.goal_audit_refreshed)
        self.assertFalse(summary.goal_complete)
        self.assertEqual(rows, [])
        self.assertTrue(final_payload["summary"]["goal_audit_refreshed"])
        self.assertFalse(final_payload["summary"]["goal_complete"])

    def test_paired_sidecar_spot_refresh_can_run_research_only_label_refresh(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with patch(
                "research_particle.paired_sidecar_spot_refresh.run_sidecar_cycle"
            ) as run_cycle, patch(
                "research_particle.paired_sidecar_spot_refresh.write_sidecar_cycle_outputs"
            ) as write_cycle_outputs:
                run_cycle.return_value = {
                    "summary": {
                        "cycle_status": "frozen_sidecar_rows_waiting_for_settlement",
                    }
                }

                summary, rows = refresh_paired_sidecar_spot_evidence(
                    input_root=root / "sidecar_spot_pairs",
                    packet_csv=root / "packets.csv",
                    labeled_csv=root / "labels.csv",
                    output_json=root / "refresh.json",
                    output_md=root / "refresh.md",
                    write=True,
                    refresh_goal_audit=False,
                    fetch_labels=True,
                    label_timeout_seconds=1.5,
                )

            aggregate_written = (root / "paired_sidecar_spot_aggregate_latest.json").exists()

        run_cycle.assert_called_once_with(
            collect_mode="none",
            timeout_seconds=1.5,
            max_markets=80,
            nearest_close_only=True,
            write=True,
            skip_label_fetch=False,
            refresh_downstream_audits=False,
        )
        write_cycle_outputs.assert_called_once()
        self.assertTrue(summary.label_refresh_requested)
        self.assertEqual(summary.label_refresh_status, "frozen_sidecar_rows_waiting_for_settlement")
        self.assertTrue(summary.label_refresh_written)
        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(rows, [])
        self.assertTrue(aggregate_written)

    def test_paired_sidecar_spot_refresh_skips_mode_mismatched_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            capture_dir = input_root / "mode_mismatch"
            capture_dir.mkdir(parents=True)
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "mode_mismatch",
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                            "promotion_allowed": False,
                        },
                        "sidecar_batch_summary": {"mode": "fixture"},
                        "sidecar_batch_markets": [],
                        "alignment_rows": [],
                    }
                ),
                encoding="utf-8",
            )

            summary, rows = refresh_paired_sidecar_spot_evidence(
                input_root=input_root,
                packet_csv=root / "packets.csv",
                labeled_csv=root / "labels.csv",
                output_json=root / "refresh.json",
                output_md=root / "refresh.md",
                write=False,
                refresh_goal_audit=False,
            )

        self.assertEqual(summary.manifest_count, 1)
        self.assertEqual(summary.skipped_manifest_count, 1)
        self.assertEqual(rows[0]["skipped_reason"], "sidecar_batch_mode_mismatch")
        self.assertFalse(rows[0]["diagnostic_ready"])

    def test_paired_sidecar_spot_refresh_skips_non_preclose_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            capture_dir = input_root / "expired_capture"
            capture_dir.mkdir(parents=True)
            (capture_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "expired_capture",
                            "collect_mode": "public-rest",
                            "paired_capture_ready": True,
                            "promotion_allowed": False,
                        },
                        "sidecar_batch_summary": {"mode": "public_rest"},
                        "sidecar_batch_markets": [
                            {
                                "market_ticker": "KXBTC15M-UNIT",
                                "market_close_ts_utc": "2026-05-11T12:10:00Z",
                            }
                        ],
                        "alignment_rows": [
                            {
                                "market_ticker": "KXBTC15M-UNIT",
                                "decision_ts_utc": "2026-05-11T12:11:00Z",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            summary, rows = refresh_paired_sidecar_spot_evidence(
                input_root=input_root,
                packet_csv=root / "packets.csv",
                labeled_csv=root / "labels.csv",
                output_json=root / "refresh.json",
                output_md=root / "refresh.md",
                write=False,
                refresh_goal_audit=False,
            )

        self.assertEqual(summary.skipped_manifest_count, 1)
        self.assertEqual(rows[0]["skipped_reason"], "sidecar_market_not_preclose_at_decision")
        self.assertFalse(rows[0]["diagnostic_ready"])

    def test_paired_sidecar_spot_refresh_skips_not_ready_manifests(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_root = root / "sidecar_spot_pairs"
            failed_dir = input_root / "failed_capture"
            failed_dir.mkdir(parents=True)
            (failed_dir / "paired_sidecar_spot_manifest.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "run_id": "failed_capture",
                            "paired_capture_ready": False,
                            "alignment_issue_count": 1,
                            "promotion_allowed": False,
                        }
                    }
                ),
                encoding="utf-8",
            )

            summary, rows = refresh_paired_sidecar_spot_evidence(
                input_root=input_root,
                packet_csv=root / "packets.csv",
                labeled_csv=root / "labels.csv",
                output_json=root / "refresh.json",
                output_md=root / "refresh.md",
                write=False,
                refresh_goal_audit=False,
            )

        self.assertFalse(summary.promotion_allowed)
        self.assertEqual(summary.manifest_count, 1)
        self.assertEqual(summary.skipped_manifest_count, 1)
        self.assertEqual(summary.enrichment_ready_count, 0)
        self.assertEqual(summary.diagnostic_ready_count, 0)
        self.assertEqual(summary.pending_diagnostic_count, 0)
        self.assertEqual(rows[0]["skipped_reason"], "paired_capture_not_ready")
        self.assertEqual(rows[0]["enrichment_issue_count"], 1)

    def test_sidecar_forward_stage_keeps_only_preclose_frozen_rows(self) -> None:
        valid = {
            "frozen_prediction_id": "fp-valid",
            "frozen_utc": "2026-05-11T12:01:00Z",
            "row_id": "row-valid",
            "market_ticker": "KXBTC15M-26MAY111210-100000",
            "market_close_ts_utc": "2026-05-11T12:10:00Z",
            "decision_ts_utc": "2026-05-11T12:00:00Z",
            "side": "yes",
            "strike": "100000",
            "seconds_to_close": "600",
            "candidate_id": "cand",
            "model_hash": "hash",
            "model_type": "regularized_logistic",
            "model_track": "pure_physics",
            "candidate_p_yes": "0.6",
            "candidate_fair_yes_cents": "60",
            "candidate_fair_no_cents": "40",
            "candidate_fair_side_cents": "60",
            "v28_p_yes": "0.5",
            "v28_fair_yes_cents": "50",
            "v28_fair_no_cents": "50",
            "v28_d_sigma": "0.1",
            "v28_sigma_t_dollars": "25",
            "ask_cents": "52",
            "book_implied_yes_from_side_ask": "0.52",
            "candidate_edge_cents": "8",
            "source_status": "frozen_pre_resolution_prediction",
        }
        invalid = dict(valid)
        invalid["frozen_prediction_id"] = "fp-invalid"
        invalid["row_id"] = "row-invalid"
        invalid["frozen_utc"] = "2026-05-11T12:11:00Z"
        invalid["y_yes_win"] = "1"

        with TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "sidecar_frozen.csv"
            fieldnames = list(dict.fromkeys(FROZEN_FIELDS + ["y_yes_win"]))
            with source_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows([valid, invalid])

            staged, summary = build_sidecar_forward_stage(source_csv=source_csv)

        self.assertEqual(summary["stage_status"], "sidecar_forward_staged_below_coverage_floor")
        self.assertEqual(summary["source_frozen_rows"], 2)
        self.assertEqual(summary["frozen_prediction_rows"], 1)
        self.assertEqual(summary["frozen_prediction_markets"], 1)
        self.assertFalse(summary["coverage_ready"])
        self.assertFalse(summary["promotion_status"]["allowed_for_promotion_scoring"])
        self.assertEqual(staged[0]["frozen_prediction_id"], "fp-valid")
        self.assertIn("frozen_not_before_close", summary["blocker_counts"])
        self.assertIn("label_field_present_in_frozen_row", summary["blocker_counts"])

    def test_forward_collection_spec_names_required_fields_and_candidates(self) -> None:
        spec, summary = build_forward_collection_spec()

        self.assertEqual(summary["status"], "ready_for_future_collection_not_promotion")
        self.assertEqual(summary["field_group_count"], 6)
        self.assertGreater(summary["field_count"], 70)
        self.assertEqual(summary["recommended_candidate_count"], 9)
        self.assertEqual(summary["passive_packet_ready_rows"], 0)
        self.assertEqual(summary["shadow_packet_ready_rows"], 0)
        self.assertIn("btc_and_feed", spec["field_groups"])
        self.assertIn("v28_baseline", spec["field_groups"])
        self.assertIn("candidate_prediction", spec["field_groups"])
        self.assertEqual(spec["sidecar_adapter"]["script"], "build_v28_successor_forward_packet_adapter.py")
        self.assertEqual(spec["public_rest_sidecar_bundle"]["script"], "build_v28_successor_public_rest_sidecar_bundle.py")
        self.assertFalse(spec["public_rest_sidecar_bundle"]["promotion_allowed"])
        self.assertEqual(spec["public_rest_sidecar_batch"]["script"], "build_v28_successor_public_rest_sidecar_batch.py")
        self.assertFalse(spec["public_rest_sidecar_batch"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_input_bundle_contract"]["script"], "validate_v28_successor_sidecar_input_bundle.py")
        self.assertFalse(spec["sidecar_input_bundle_contract"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_packet_collector"]["script"], "collect_v28_successor_forward_packets.py")
        self.assertFalse(spec["sidecar_packet_collector"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_bundle_freeze_handoff"]["script"], "run_v28_successor_sidecar_bundle_freeze_handoff.py")
        self.assertFalse(spec["sidecar_bundle_freeze_handoff"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_bundle_batch_handoff"]["script"], "run_v28_successor_sidecar_bundle_batch_handoff.py")
        self.assertFalse(spec["sidecar_bundle_batch_handoff"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_bundle_batch_settlement_labels"]["script"], "fetch_v28_successor_sidecar_batch_settlement_labels.py")
        self.assertFalse(spec["sidecar_bundle_batch_settlement_labels"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_bundle_batch_label_join"]["script"], "run_v28_successor_sidecar_batch_label_join_handoff.py")
        self.assertFalse(spec["sidecar_bundle_batch_label_join"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_batch_evidence_score"]["script"], "score_v28_successor_sidecar_batch_evidence.py")
        self.assertFalse(spec["sidecar_batch_evidence_score"]["promotion_allowed"])
        self.assertEqual(spec["sidecar_collection_cycle"]["script"], "run_v28_successor_sidecar_collection_cycle.py")
        self.assertFalse(spec["sidecar_collection_cycle"]["promotion_allowed"])
        self.assertEqual(spec["forward_packet_freeze_handoff"]["script"], "run_v28_successor_forward_packet_freeze.py")
        self.assertFalse(spec["forward_packet_freeze_handoff"]["promotion_allowed"])
        self.assertEqual(spec["post_resolution_label_join"]["script"], "join_v28_successor_forward_labels.py")
        self.assertEqual(spec["forward_evidence_score"]["script"], "score_v28_successor_forward_evidence.py")
        self.assertTrue(spec["collection_candidates"]["recommended_candidates"])
        self.assertTrue(all(not row["allowed_for_forward_registry"] for row in spec["collection_candidates"]["recommended_candidates"]))
        self.assertIn("settlement fields are absent before freeze", spec["freeze_acceptance_gates"])

    def test_forward_source_readiness_explains_missing_freeze_ready_rows(self) -> None:
        report, summary = build_forward_source_readiness()

        self.assertEqual(summary["overall_status"], "blocked_missing_freeze_ready_sources")
        self.assertFalse(summary["promotion_allowed"])
        self.assertGreater(summary["passive_rows"], 0)
        self.assertGreater(summary["passive_markets"], 0)
        self.assertGreater(summary["live_v28_base_field_rows"], 0)
        self.assertGreater(summary["forward_packet_prediction_rows"], 0)
        self.assertEqual(summary["freeze_eligible_packet_prediction_rows"], 0)
        self.assertEqual(summary["sidecar_collector_status"], "contract_demo_ready_not_evidence")
        self.assertGreater(summary["sidecar_collector_demo_packet_ready_rows"], 0)
        self.assertFalse(summary["sidecar_collector_promotion_allowed"])
        self.assertIn("sidecar_batch_joined_rows", summary)
        self.assertIn("sidecar_batch_evidence_status", summary)
        self.assertGreaterEqual(summary["frozen_forward_rows"], 0)
        self.assertGreaterEqual(summary["forward_registry_rows"], 0)
        self.assertGreaterEqual(summary["forward_labeled_rows"], 0)
        self.assertIn("passive_rows_missing_btc_state", summary["blockers"])
        self.assertIn("passive_rows_missing_v28_baseline", summary["blockers"])
        self.assertIn("no_freeze_eligible_forward_packet_candidate_predictions", summary["blockers"])
        self.assertIn("sidecar_packet_collector_rows_are_demo_not_forward_evidence", summary["blockers"])
        if summary["frozen_forward_rows"] == 0:
            self.assertIn("no_frozen_forward_predictions", summary["blockers"])
        else:
            self.assertNotIn("no_frozen_forward_predictions", summary["blockers"])
        if summary["forward_labeled_rows"] == 0:
            self.assertIn("no_forward_labeled_predictions", summary["blockers"])
        self.assertTrue(report["caches"]["btc_cache"]["exists"])
        self.assertTrue(report["caches"]["market_result_cache"]["exists"])
        self.assertIn("forward_packet_candidate_predictions", report)
        self.assertIn("sidecar_packet_collector", report)
        self.assertIn("sidecar_batch_evidence", report)

    def test_research_pipeline_runner_orders_refresh_without_live_paths(self) -> None:
        plan = build_plan()
        step_ids = [row["step_id"] for row in plan]
        by_id = {step_id: index for index, step_id in enumerate(step_ids)}

        self.assertEqual(len(step_ids), len(set(step_ids)))
        self.assertEqual(len(step_ids), len(PIPELINE_STEPS))
        self.assertEqual(step_ids[-1], "unit_tests")
        self.assertLess(by_id["seed_dataset"], by_id["seed_features"])
        self.assertLess(by_id["seed_features"], by_id["seed_candidates"])
        self.assertLess(by_id["logged_event_dataset"], by_id["logged_event_features"])
        self.assertLess(by_id["logged_event_features"], by_id["logged_event_candidates"])
        self.assertLess(by_id["forward_packet_adapter"], by_id["forward_freeze_preflight"])
        self.assertLess(by_id["forward_packet_adapter"], by_id["public_rest_sidecar_bundle"])
        self.assertLess(by_id["public_rest_sidecar_bundle"], by_id["sidecar_input_bundle_contract"])
        self.assertLess(by_id["public_rest_sidecar_bundle"], by_id["public_rest_sidecar_batch"])
        self.assertLess(by_id["public_rest_sidecar_batch"], by_id["sidecar_input_bundle_contract"])
        self.assertLess(by_id["forward_packet_adapter"], by_id["sidecar_input_bundle_contract"])
        self.assertLess(by_id["sidecar_input_bundle_contract"], by_id["sidecar_packet_collector"])
        self.assertLess(by_id["sidecar_packet_collector"], by_id["forward_packet_freeze_handoff"])
        self.assertLess(by_id["sidecar_packet_collector"], by_id["sidecar_bundle_freeze_handoff"])
        self.assertLess(by_id["sidecar_bundle_freeze_handoff"], by_id["forward_packet_freeze_handoff"])
        self.assertLess(by_id["sidecar_bundle_freeze_handoff"], by_id["sidecar_bundle_batch_handoff"])
        self.assertLess(by_id["sidecar_bundle_batch_handoff"], by_id["forward_packet_freeze_handoff"])
        self.assertLess(by_id["sidecar_bundle_batch_handoff"], by_id["sidecar_bundle_batch_settlement_labels"])
        self.assertLess(by_id["sidecar_bundle_batch_settlement_labels"], by_id["sidecar_bundle_batch_label_join"])
        self.assertLess(by_id["sidecar_bundle_batch_handoff"], by_id["sidecar_bundle_batch_label_join"])
        self.assertLess(by_id["sidecar_bundle_batch_label_join"], by_id["sidecar_batch_evidence_score"])
        self.assertLess(by_id["sidecar_batch_evidence_score"], by_id["sidecar_collection_cycle"])
        self.assertLess(by_id["sidecar_collection_cycle"], by_id["forward_packet_freeze_handoff"])
        self.assertLess(by_id["forward_packet_freeze_handoff"], by_id["forward_collection_spec"])
        self.assertLess(by_id["sidecar_packet_collector"], by_id["forward_collection_spec"])
        self.assertLess(by_id["forward_freeze_preflight"], by_id["freeze_forward_candidates"])
        self.assertLess(by_id["freeze_forward_candidates"], by_id["stage_sidecar_forward_evidence"])
        self.assertLess(by_id["stage_sidecar_forward_evidence"], by_id["forward_label_join"])
        self.assertLess(by_id["stage_sidecar_forward_evidence"], by_id["forward_registry"])
        self.assertLess(by_id["forward_registry"], by_id["forward_label_join"])
        self.assertLess(by_id["forward_label_join"], by_id["forward_evidence_score"])
        self.assertLess(by_id["source_contract"], by_id["goal_completion_audit"])
        self.assertLess(by_id["source_contract"], by_id["forward_source_readiness"])
        self.assertLess(by_id["forward_source_readiness"], by_id["promotion_verifier"])
        self.assertLess(by_id["source_contract"], by_id["promotion_verifier"])
        self.assertLess(by_id["forward_evidence_score"], by_id["promotion_verifier"])
        self.assertLess(by_id["sidecar_batch_evidence_score"], by_id["promotion_verifier"])
        self.assertLess(by_id["sidecar_collection_cycle"], by_id["promotion_verifier"])

        command_text = "\n".join(" ".join(map(str, row["command"])) for row in plan).lower()
        for blocked in [
            "kalshi_btc15m_bot_ws.py",
            "run_probability_lab_bot_live_size2.ps1",
            "ensure_probability_lab_bot_live_size2.ps1",
            "live_trading.lock",
        ]:
            self.assertNotIn(blocked, command_text)
        self.assertIn("does not place orders", RESEARCH_ONLY_GUARDRAILS)

    def test_research_pipeline_dry_run_manifest_is_planned_and_hashes_key_outputs(self) -> None:
        manifest = run_pipeline(dry_run=True)
        artifact_paths = {str(path).replace("\\", "/") for path in KEY_ARTIFACTS}
        manifest_artifacts = {row["path"] for row in manifest["key_artifacts"]}

        self.assertEqual(manifest["pipeline_status"], "planned")
        self.assertEqual(manifest["steps_run"], manifest["step_count"])
        self.assertTrue(all(row["status"] == "planned" for row in manifest["steps"]))
        self.assertIn("logs/edge_research/v28_successor_goal_completion_audit_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_forward_evidence_score_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_forward_label_join_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_forward_packet_adapter_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_public_rest_sidecar_bundle_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_public_rest_sidecar_batch_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_input_bundle_contract_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_packet_collector_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_bundle_freeze_handoff_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_bundle_batch_handoff_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_bundle_batch_settlement_labels_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_bundle_batch_label_join_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_batch_evidence_score_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_sidecar_collection_cycle_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_market_coverage_loop_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_forward_packet_freeze_handoff_latest.json", manifest_artifacts)
        self.assertIn("logs/edge_research/v28_successor_forward_source_readiness_latest.json", manifest_artifacts)
        self.assertIn("research_particle/v28_successor/frozen_forward_predictions_latest.csv", manifest_artifacts)
        self.assertTrue(any(path.endswith("v28_successor_forward_registry_latest.json") for path in artifact_paths))

    def test_market_coverage_loop_dry_run_is_planned_and_non_promoting(self) -> None:
        report = run_market_coverage_loop(
            collect_mode="none",
            nearest_close_only=True,
            iterations=3,
            sleep_seconds=0.0,
            timeout_seconds=1.0,
            max_markets=1,
            target_clean_rows=200,
            target_clean_markets=40,
            stop_when_target_met=True,
            write=False,
            dry_run=True,
            run_full_pipeline_at_end=False,
        )

        self.assertEqual(report["loop_status"], "planned")
        self.assertTrue(report["nearest_close_only"])
        self.assertEqual(report["collection_scope"], "nearest_close")
        self.assertEqual(report["iterations_run"], 0)
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["target_met"])
        self.assertIn("does not place orders", MARKET_COVERAGE_LOOP_GUARDRAILS)
        self.assertEqual(report["outputs"]["json"], "logs/edge_research/v28_successor_market_coverage_loop_latest.json")

    def test_market_coverage_loop_can_plan_all_open_closes_without_promotion(self) -> None:
        report = run_market_coverage_loop(
            collect_mode="public_rest",
            nearest_close_only=False,
            iterations=1,
            sleep_seconds=0.0,
            timeout_seconds=1.0,
            max_markets=80,
            target_clean_rows=200,
            target_clean_markets=40,
            stop_when_target_met=False,
            write=False,
            dry_run=True,
            run_full_pipeline_at_end=False,
        )

        self.assertEqual(report["loop_status"], "planned")
        self.assertFalse(report["nearest_close_only"])
        self.assertEqual(report["collection_scope"], "all_open_closes")
        self.assertFalse(report["promotion_allowed"])

    def test_market_coverage_loop_target_requires_rows_and_markets(self) -> None:
        self.assertFalse(
            market_coverage_target_met(
                {"clean_forward_rows": 240, "clean_forward_markets": 11},
                target_clean_rows=200,
                target_clean_markets=40,
            )
        )
        self.assertTrue(
            market_coverage_target_met(
                {"clean_forward_rows": 240, "clean_forward_markets": 40},
                target_clean_rows=200,
                target_clean_markets=40,
            )
        )

    def test_market_coverage_loop_reports_candidate_specific_forward_shortfall(self) -> None:
        summary = summarize_market_coverage_candidate_gates(
            {
                "candidate_gates": [
                    {
                        "candidate_id": "weak",
                        "rows": 300,
                        "markets": 20,
                        "row_shortfall": 0,
                        "market_shortfall": 20,
                        "estimated_additional_markets_needed": 20,
                        "forward_evidence_promotable": False,
                        "fail_reasons": ["insufficient_forward_rows", "insufficient_forward_markets"],
                    },
                    {
                        "candidate_id": "near",
                        "rows": 180,
                        "markets": 35,
                        "row_shortfall": 20,
                        "market_shortfall": 5,
                        "estimated_additional_markets_needed": 10,
                        "forward_evidence_promotable": False,
                        "fail_reasons": ["insufficient_forward_rows", "insufficient_forward_markets"],
                    },
                    {
                        "candidate_id": "sampled_but_bad",
                        "rows": 400,
                        "markets": 50,
                        "row_shortfall": 0,
                        "market_shortfall": 0,
                        "estimated_additional_markets_needed": 0,
                        "forward_evidence_promotable": False,
                        "fail_reasons": ["forward_brier_not_better_than_v28"],
                    },
                ]
            }
        )

        self.assertEqual(summary["candidate_gate_count"], 3)
        self.assertTrue(summary["candidate_forward_sample_floor_met"])
        self.assertFalse(summary["candidate_forward_promotable"])
        self.assertEqual(summary["best_candidate_id_by_sample_shortfall"], "sampled_but_bad")
        self.assertEqual(summary["sample_only_candidate_count"], 2)
        self.assertEqual(summary["best_sample_only_candidate_id"], "near")
        self.assertEqual(summary["best_sample_only_candidate_rows"], 180)
        self.assertEqual(summary["best_sample_only_candidate_markets"], 35)
        self.assertEqual(summary["best_sample_only_candidate_row_shortfall"], 20)
        self.assertEqual(summary["best_sample_only_candidate_market_shortfall"], 5)
        self.assertEqual(summary["best_sample_only_candidate_estimated_additional_markets_needed"], 10)

    def test_market_coverage_loop_reports_candidate_sample_floor_met_separately(self) -> None:
        summary = summarize_market_coverage_candidate_gates(
            {
                "candidate_gates": [
                    {
                        "candidate_id": "enough_sample_not_promotable",
                        "rows": 240,
                        "markets": 42,
                        "row_shortfall": 0,
                        "market_shortfall": 0,
                        "estimated_additional_markets_needed": 0,
                        "forward_evidence_promotable": False,
                        "fail_reasons": ["forward_brier_not_better_than_v28"],
                    }
                ]
            }
        )

        self.assertTrue(summary["candidate_forward_sample_floor_met"])
        self.assertFalse(summary["candidate_forward_promotable"])
        self.assertEqual(summary["best_candidate_id_by_sample_shortfall"], "enough_sample_not_promotable")
        self.assertEqual(summary["sample_only_candidate_count"], 0)
        self.assertIsNone(summary["best_sample_only_candidate_id"])

    def test_forward_freezer_writes_no_rows_without_complete_forward_inputs(self) -> None:
        rows, summary = build_forward_freezer()

        self.assertEqual(summary["freeze_status"], "blocked_no_frozen_predictions")
        self.assertGreater(summary["passive_input_rows"], 0)
        self.assertEqual(summary["freeze_ready_input_rows"], 0)
        self.assertEqual(summary["frozen_prediction_rows"], 0)
        self.assertGreater(summary["forward_collection_candidate_count"], 0)
        self.assertGreater(summary["forward_allowed_candidate_count"], 0)
        self.assertEqual(rows, [])
        self.assertIn("missing_btc_state", summary["blocker_counts"])
        self.assertIn("missing_v28_baseline", summary["blocker_counts"])
        self.assertIn("missing_candidate_prediction", summary["blocker_counts"])
        self.assertNotIn("no_forward_collection_candidate_manifest", summary["blocker_counts"])

    def test_forward_freezer_accepts_complete_row_level_candidate_packet(self) -> None:
        adapter_rows, _adapter_summary = build_forward_packet_adapter_demo()
        row = dict(adapter_rows[0])
        candidate_id = str(row["candidate_id"])
        row["is_simulated"] = "False"
        row["is_diagnostic_only"] = "False"
        row["allowed_for_forward_promotion"] = "False"
        row["exclusion_reason"] = ""
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)

        blockers = row_freeze_blockers(row, now_before_close, [{"candidate_id": candidate_id}])
        self.assertEqual(blockers, [])

        with TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "packet_rows.csv"
            with source_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
                writer.writeheader()
                writer.writerow(row)

            frozen_rows, summary = build_forward_freezer(now_utc=now_before_close, source_csv=source_csv)

        self.assertEqual(summary["freeze_status"], "frozen_predictions_written")
        self.assertEqual(summary["freeze_ready_input_rows"], 1)
        self.assertEqual(summary["frozen_prediction_rows"], 1)
        self.assertEqual(summary["frozen_prediction_markets"], 1)
        self.assertEqual(len(frozen_rows), 1)
        self.assertEqual(frozen_rows[0]["candidate_id"], candidate_id)
        self.assertEqual(frozen_rows[0]["source_status"], "frozen_pre_resolution_prediction")
        self.assertAlmostEqual(float(frozen_rows[0]["candidate_p_yes"]), float(row["candidate_p_yes"]))
        self.assertAlmostEqual(float(frozen_rows[0]["v28_p_anchor"]), float(row["v28_p_anchor"]))
        self.assertAlmostEqual(float(frozen_rows[0]["v28_p_recent_transport"]), float(row["v28_p_recent_transport"]))
        self.assertAlmostEqual(float(frozen_rows[0]["v28_transport_recent_n"]), float(row["v28_transport_recent_n"]))
        self.assertAlmostEqual(
            float(frozen_rows[0]["candidate_fair_yes_cents"]) + float(frozen_rows[0]["candidate_fair_no_cents"]),
            100.0,
            places=6,
        )

    def test_forward_registry_registers_frozen_prediction_ledger_rows(self) -> None:
        adapter_rows, _adapter_summary = build_forward_packet_adapter_demo()
        packet_row = dict(adapter_rows[0])
        packet_row["is_simulated"] = "False"
        packet_row["is_diagnostic_only"] = "False"
        packet_row["exclusion_reason"] = ""
        now_before_close = datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)

        with TemporaryDirectory() as temp_dir:
            packet_csv = Path(temp_dir) / "packet_rows.csv"
            frozen_csv = Path(temp_dir) / "frozen_rows.csv"
            with packet_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(packet_row.keys()))
                writer.writeheader()
                writer.writerow(packet_row)
            frozen_rows, _freeze_summary = build_forward_freezer(now_utc=now_before_close, source_csv=packet_csv)
            with frozen_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(frozen_rows[0].keys()))
                writer.writeheader()
                writer.writerows(frozen_rows)

            registry_rows, summary = build_registry_rows(frozen_csv=frozen_csv)

        self.assertEqual(summary["registry_status"], "active")
        self.assertEqual(summary["row_count"], 1)
        self.assertEqual(summary["market_count"], 1)
        self.assertFalse(summary["promotion_ready"])
        self.assertEqual(registry_rows[0]["source_status"], "frozen_pre_resolution_prediction")
        self.assertEqual(registry_rows[0]["frozen_prediction_id"], frozen_rows[0]["frozen_prediction_id"])

    def test_source_contract_blocks_diagnostic_rows_and_empty_forward_registry(self) -> None:
        evaluations, summary = build_source_contract()
        by_id = {row["dataset_id"]: row for row in evaluations}

        self.assertIn(summary["overall_verdict"], {"blocked", "promotion_grade"})
        self.assertEqual(summary["promotion_contract_ready"], summary["overall_verdict"] == "promotion_grade")
        expected_missing_required = [
            dataset_id
            for dataset_id in ("forward_registry", "forward_labeled_predictions")
            if "artifact_exists" in by_id[dataset_id]["hard_failed_gates"]
        ]
        expected_non_promotion_ready = [
            dataset_id
            for dataset_id in ("forward_registry", "forward_labeled_predictions")
            if summary["required_forward_dataset_status"][dataset_id] != "promotion_grade"
        ]
        self.assertEqual(summary["missing_required_forward_datasets"], expected_missing_required)
        self.assertEqual(
            summary["non_promotion_ready_required_forward_datasets"],
            expected_non_promotion_ready,
        )
        self.assertIn(summary["required_forward_dataset_status"]["forward_registry"], {"blocked", "promotion_grade"})
        self.assertIn(summary["required_forward_dataset_status"]["forward_labeled_predictions"], {"blocked", "promotion_grade"})
        if summary["required_forward_dataset_status"]["forward_registry"] == "promotion_grade":
            self.assertIn("forward_registry", summary["promotion_grade_datasets"])
            self.assertNotIn("forward_registry_promotion_ready", summary["required_forward_hard_blockers"])
        else:
            self.assertNotIn("forward_registry", summary["promotion_grade_datasets"])
            self.assertIn("forward_registry_promotion_ready", summary["required_forward_hard_blockers"])
        if summary["required_forward_dataset_status"]["forward_labeled_predictions"] == "promotion_grade":
            self.assertIn("forward_labeled_predictions", summary["promotion_grade_datasets"])
            self.assertNotIn("forward_labeled_min_markets", summary["required_forward_hard_blockers"])
        else:
            self.assertNotIn("forward_labeled_predictions", summary["promotion_grade_datasets"])
            self.assertIn("forward_labeled_min_markets", summary["required_forward_hard_blockers"])
        self.assertIn("forward_promotion_rows_present", summary["hard_blockers"])
        if by_id["forward_labeled_predictions"]["row_count"] < summary["minimum_forward_rows"]:
            self.assertIn("forward_labeled_min_rows", summary["required_forward_hard_blockers"])
        else:
            self.assertNotIn("forward_labeled_min_rows", summary["required_forward_hard_blockers"])
        self.assertIn("forward_promotion_rows_present", summary["auxiliary_hard_blockers"])
        if "forward_registry_not_empty" not in summary["hard_blockers"]:
            if by_id["forward_registry"]["row_count"] < summary["minimum_forward_rows"]:
                self.assertIn("forward_registry_min_rows", summary["hard_blockers"])
            else:
                self.assertNotIn("forward_registry_min_rows", summary["hard_blockers"])
            if summary["required_forward_dataset_status"]["forward_registry"] == "promotion_grade":
                self.assertNotIn("forward_registry_min_markets", summary["hard_blockers"])
                self.assertNotIn("forward_registry_promotion_ready", summary["hard_blockers"])
            else:
                self.assertIn("forward_registry_min_markets", summary["hard_blockers"])
                self.assertIn("forward_registry_promotion_ready", summary["hard_blockers"])

        seed = by_id["seed_causal_rows"]
        self.assertEqual(seed["status"], "blocked")
        self.assertIn("strike_fields_complete", seed["hard_failed_gates"])
        self.assertIn("boundary_geometry_complete", seed["hard_failed_gates"])
        self.assertIn("forward_promotion_rows_present", seed["hard_failed_gates"])
        self.assertIn("pre_resolution_clock_valid", seed["passed_gates"])

        logged = by_id["logged_event_causal_rows"]
        self.assertEqual(logged["status"], "blocked")
        self.assertIn("strike_fields_complete", logged["passed_gates"])
        self.assertIn("boundary_geometry_complete", logged["passed_gates"])
        self.assertIn("forward_promotion_rows_present", logged["hard_failed_gates"])
        self.assertEqual(logged["diagnostic_counts"]["is_recomputed_after_resolution"], 0)

        logged_features = by_id["logged_event_feature_table"]
        self.assertIn("feature_manifest_no_leaky_names", logged_features["passed_gates"])
        self.assertIn("feature_manifest_no_leaky_source_columns", logged_features["passed_gates"])
        self.assertIn("boundary_geometry_complete", logged_features["passed_gates"])
        self.assertIn("forward_promotion_rows_present", logged_features["hard_failed_gates"])

        passive = by_id["passive_forward_snapshots"]
        self.assertEqual(passive["status"], "blocked")
        self.assertIn("identifier_fields_complete", passive["passed_gates"])
        self.assertIn("strike_fields_complete", passive["passed_gates"])
        self.assertIn("book_price_or_implied_price_available", passive["passed_gates"])
        self.assertIn("forward_promotion_rows_present", passive["hard_failed_gates"])
        self.assertIn("broad_market_coverage_floor", passive["hard_failed_gates"])

        shadow = by_id["shadow_forward_labeled_rows"]
        self.assertEqual(shadow["status"], "blocked")
        self.assertIn("target_label_present", shadow["passed_gates"])
        self.assertIn("probability_fields_complete_and_bounded", shadow["passed_gates"])
        self.assertIn("fair_yes_no_cents_complete_and_sum_to_100", shadow["passed_gates"])
        self.assertIn("forward_promotion_rows_present", shadow["hard_failed_gates"])
        self.assertIn("broad_market_coverage_floor", shadow["hard_failed_gates"])

        forward = by_id["forward_registry"]
        self.assertIn(forward["status"], {"blocked", "promotion_grade"})
        if forward["status"] == "promotion_grade":
            self.assertIn("forward_registry_promotion_ready", forward["passed_gates"])
        else:
            self.assertIn("forward_registry_promotion_ready", forward["hard_failed_gates"])
        if forward["row_count"] == 0:
            self.assertIn("forward_registry_not_empty", forward["hard_failed_gates"])
            self.assertIn("forward_registry_from_frozen_predictions", forward["hard_failed_gates"])
            self.assertIn("forward_registry_frozen_before_close", forward["hard_failed_gates"])
            self.assertIn("forward_registry_unique_frozen_predictions", forward["hard_failed_gates"])
        else:
            self.assertIn("forward_registry_not_empty", forward["passed_gates"])
            self.assertIn("forward_registry_from_frozen_predictions", forward["passed_gates"])
            self.assertIn("forward_registry_frozen_before_close", forward["passed_gates"])
            self.assertIn("forward_registry_unique_frozen_predictions", forward["passed_gates"])
            if forward["row_count"] < summary["minimum_forward_rows"]:
                self.assertIn("forward_registry_min_rows", forward["hard_failed_gates"])
            else:
                self.assertIn("forward_registry_min_rows", forward["passed_gates"])
            if forward["status"] == "promotion_grade":
                self.assertIn("forward_registry_min_markets", forward["passed_gates"])
            else:
                self.assertIn("forward_registry_min_markets", forward["hard_failed_gates"])

        forward_labeled = by_id["forward_labeled_predictions"]
        self.assertIn(forward_labeled["status"], {"blocked", "promotion_grade"})
        if forward_labeled["row_count"] == 0:
            self.assertIn("forward_labeled_rows_present", forward_labeled["hard_failed_gates"])
            self.assertIn("forward_labels_from_frozen_predictions", forward_labeled["hard_failed_gates"])
            self.assertIn("forward_labels_frozen_before_close", forward_labeled["hard_failed_gates"])
        else:
            self.assertIn("forward_labeled_rows_present", forward_labeled["passed_gates"])
            self.assertIn("forward_labels_from_frozen_predictions", forward_labeled["passed_gates"])
            self.assertIn("forward_labels_frozen_before_close", forward_labeled["passed_gates"])
            if forward_labeled["row_count"] < summary["minimum_forward_rows"]:
                self.assertIn("forward_labeled_min_rows", forward_labeled["hard_failed_gates"])
            else:
                self.assertIn("forward_labeled_min_rows", forward_labeled["passed_gates"])
            if forward_labeled["status"] == "promotion_grade":
                self.assertIn("forward_labeled_min_markets", forward_labeled["passed_gates"])
            else:
                self.assertIn("forward_labeled_min_markets", forward_labeled["hard_failed_gates"])

        sidecar_labeled = by_id["sidecar_batch_labeled_predictions"]
        self.assertIn(sidecar_labeled["status"], {"blocked", "promotion_grade"})
        self.assertIn("forward_labeled_rows_present", sidecar_labeled["passed_gates"])
        self.assertIn("forward_labels_from_frozen_predictions", sidecar_labeled["passed_gates"])
        self.assertIn("forward_labels_frozen_before_close", sidecar_labeled["passed_gates"])
        if sidecar_labeled["status"] == "promotion_grade":
            self.assertIn("broad_market_coverage_floor", sidecar_labeled["passed_gates"])
            self.assertIn("forward_labeled_min_markets", sidecar_labeled["passed_gates"])
            self.assertIn("target_label_present", sidecar_labeled["passed_gates"])
            self.assertIn("forward_labels_joined_after_resolution", sidecar_labeled["passed_gates"])
        else:
            self.assertTrue(
                {
                    "broad_market_coverage_floor",
                    "forward_labeled_min_markets",
                    "target_label_present",
                    "forward_labels_joined_after_resolution",
                }
                & set(sidecar_labeled["hard_failed_gates"])
            )

    def test_source_contract_registry_gates_reject_non_frozen_or_late_rows(self) -> None:
        rows = [
            {
                "registry_id": "r1",
                "frozen_prediction_id": "fp1",
                "market_ticker": "M1",
                "frozen_utc": "2026-05-11T12:11:00Z",
                "market_close_ts_utc": "2026-05-11T12:10:00Z",
                "source_status": "diagnostic_prediction",
            },
            {
                "registry_id": "r1",
                "frozen_prediction_id": "fp1",
                "market_ticker": "M2",
                "frozen_utc": "2026-05-11T12:08:00Z",
                "market_close_ts_utc": "2026-05-11T12:10:00Z",
                "source_status": "frozen_pre_resolution_prediction",
            },
        ]

        gates, details = evaluate_forward_cleanliness(rows, "forward_registry")
        by_gate = {gate["gate"]: gate for gate in gates}

        self.assertFalse(by_gate["forward_registry_from_frozen_predictions"]["passed"])
        self.assertFalse(by_gate["forward_registry_frozen_before_close"]["passed"])
        self.assertFalse(by_gate["forward_registry_unique_frozen_predictions"]["passed"])
        self.assertEqual(details["non_frozen_source_rows"], 1)
        self.assertEqual(details["freeze_after_close_rows"], 1)
        self.assertEqual(details["duplicate_registry_ids"], 1)
        self.assertEqual(details["duplicate_frozen_prediction_ids"], 1)

    def test_goal_completion_audit_tracks_source_contract_verifier_gate(self) -> None:
        checks, summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Promotion verifier consumes source-contract readiness as a hard gate"]

        expected_status = "complete" if all(row["status"] == "pass" for row in checks) else "not_complete"
        self.assertEqual(summary["overall_status"], expected_status)
        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_contract_ready=", check["evidence"])
        self.assertIn("hard_blockers=", check["evidence"])

    def test_goal_completion_audit_tracks_forward_source_readiness(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Audit forward source readiness and joinability before promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("blocked_missing_freeze_ready_sources", check["evidence"])
        self.assertIn("promotion_allowed=False", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_input_bundle_contract(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Validate sidecar input bundle contract before packet collection"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("bundle_ready=True", check["evidence"])
        self.assertIn("promotion_allowed=False", check["evidence"])

    def test_goal_completion_audit_tracks_public_rest_sidecar_bundle_builder(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Provide public REST sidecar bundle builder without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("packet_rows", check["evidence"])
        self.assertIn("promotion_allowed=False", check["evidence"])

    def test_goal_completion_audit_tracks_public_rest_sidecar_batch_builder(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Provide public REST sidecar batch builder for active boundary coverage without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("packet_rows", check["evidence"])
        self.assertIn("promotion_allowed=False", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_packet_collector_bridge(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Implement sidecar collector bridge for future real pre-resolution packet rows"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("contract_demo_ready_not_evidence", check["evidence"])
        self.assertIn("input_bundle_json", check["evidence"])
        self.assertIn("promotion_allowed=False", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_bundle_freeze_handoff(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Provide one-command sidecar bundle freeze handoff without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("packet_rows", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_bundle_batch_handoff(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Provide batch sidecar bundle handoff for broad market collection without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("input_files", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_batch_settlement_label_fetcher(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Fetch sidecar batch settlement labels only after market close without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("label_rows", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_batch_label_join_handoff(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Provide batch sidecar label join handoff without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("joined_rows", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_batch_evidence_score(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Score sidecar batch settled evidence without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("canonical_promotion_ledger=False", check["evidence"])

    def test_goal_completion_audit_tracks_sidecar_collection_cycle(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Run one repeatable sidecar collection cycle without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("clean_rows", check["evidence"])

    def test_goal_completion_audit_tracks_packet_freeze_handoff(self) -> None:
        checks, _summary = build_goal_completion_checklist()
        by_requirement = {row["requirement"]: row for row in checks}
        check = by_requirement["Provide reproducible packet freeze handoff without granting promotion"]

        self.assertEqual(check["status"], "pass")
        self.assertIn("promotion_allowed=False", check["evidence"])
        self.assertIn("packet_ready_rows", check["evidence"])


if __name__ == "__main__":
    unittest.main()
