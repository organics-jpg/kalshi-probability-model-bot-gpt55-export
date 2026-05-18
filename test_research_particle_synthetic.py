from __future__ import annotations

import math
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone

from research_particle.calibrators import LabelGatedACICalibrator, OnlineLogitCalibrator
from research_particle.anchor_regime_profile import (
    build_anchor_regime_profile,
    main as anchor_regime_profile_main,
)
from research_particle.artifact_leakage_audit import (
    build_artifact_leakage_audit,
    main as artifact_leakage_audit_main,
)
from research_particle.candidate_contexts import (
    CandidateContextError,
    build_candidate_context,
    main as candidate_contexts_main,
    normalize_candidate_contexts,
)
from research_particle.denominator_integrity_audit import (
    build_denominator_integrity_audit,
    main as denominator_integrity_audit_main,
)
from research_particle.dynamic_particle_replay import (
    RollingVolEstimator,
    DynamicParticleSpec,
    main as dynamic_particle_replay_main,
)
from research_particle.ev_rank_calibration_diagnostic import (
    build_ev_rank_calibration_diagnostic,
    main as ev_rank_calibration_diagnostic_main,
)
from research_particle.empirical_next_second_particle_diagnostic import (
    EmpiricalSecondParticleSpec,
    build_empirical_next_second_particle_diagnostic,
    empirical_second_particle_probability,
    main as empirical_next_second_particle_diagnostic_main,
)
from research_particle.empirical_current_anchor_diagnostic import (
    EmpiricalCurrentAnchorSpec,
    build_empirical_current_anchor_diagnostic,
    main as empirical_current_anchor_diagnostic_main,
    materialize_empirical_current_anchor_rows,
)
from research_particle.empirical_market_opportunity_diagnostic import (
    build_empirical_market_opportunity_diagnostic,
    main as empirical_market_opportunity_diagnostic_main,
    write_empirical_market_opportunity_diagnostic,
)
from research_particle.empirical_market_opportunity_loro import (
    build_market_opportunity_loro_report,
    main as empirical_market_opportunity_loro_main,
)
from research_particle.dynamic_particle_locked_oos_plan import (
    main as dynamic_particle_locked_oos_plan_main,
)
from research_particle.dynamic_particle_oos import main as dynamic_particle_oos_main
from research_particle.ensemble_particle_replay import main as ensemble_particle_replay_main
from research_particle.ev_decision import (
    FillStats,
    break_even_probability,
    expected_pnl_cents,
    realized_trade_pnl_cents,
)
from research_particle.fat_tail_particle_diagnostic import (
    build_fat_tail_particle_diagnostic,
    main as fat_tail_particle_diagnostic_main,
    terminal_jump_mixture_probability,
)
from research_particle.fixed_terminal_oos import (
    evaluate_fixed_terminal_oos,
    main as fixed_terminal_oos_main,
)
from research_particle.fixed_terminal_locked_oos_plan import main as fixed_terminal_locked_oos_plan_main
from research_particle.labeler import LabelUnavailableError, label_candidate
import research_particle.kalshi_market_results as kalshi_market_results
from research_particle.kalshi_market_results import _market_from_payload, market_result_row_from_market
from research_particle.market_result_labels import (
    build_label_contexts_from_market_results,
    main as market_result_labels_main,
)
from research_particle.market_cluster_diagnostic import (
    build_market_cluster_diagnostic,
    main as market_cluster_diagnostic_main,
)
from research_particle.meta_probability_loro import (
    build_meta_probability_loro_report,
    main as meta_probability_loro_main,
)
from research_particle.oos_stability_report import main as oos_stability_report_main
from research_particle.online_logit_particle_replay import (
    evaluate_online_logit_particle_variants,
    main as online_logit_particle_replay_main,
)
from research_particle.online_anchor_calibration_diagnostic import (
    build_online_anchor_calibration_diagnostic,
    main as online_anchor_calibration_diagnostic_main,
)
from research_particle.anchor_switch_loro import (
    build_anchor_switch_loro_report,
    main as anchor_switch_loro_main,
)
from research_particle.locked_oos_run_plan import main as locked_oos_run_plan_main
from research_particle.materialized_variant_replay import (
    main as materialized_variant_replay_main,
    materialize_variant_rows,
)
from research_particle.materialized_variant_selection_sweep import (
    main as materialized_variant_selection_sweep_main,
)
from research_particle.particle_engine import NextSecondParticleEngine, ParticleEngineConfig
from research_particle.passive_checkpoint_source import (
    PassiveCheckpointContext,
    build_observation_from_passive_checkpoint,
    convert_passive_checkpoints,
    main as passive_checkpoint_source_main,
)
from research_particle.paired_passive_shadow_run import build_parser as paired_passive_parser
from research_particle.pasc_loro_threshold_diagnostic import (
    build_pasc_threshold_loro_report,
    main as pasc_loro_threshold_diagnostic_main,
)
from research_particle.probability_variants import (
    evaluate_probability_variants,
    main as probability_variants_main,
)
from research_particle.residual_blend_locked_oos_plan import (
    main as residual_blend_locked_oos_plan_main,
)
from research_particle.residual_blend_oos import main as residual_blend_oos_main
from research_particle.residual_blend_loro import main as residual_blend_loro_main
from research_particle.read_only_candidate_source import (
    TopOfBookObservation,
    build_raw_candidate_observation,
    convert_observations,
    main as read_only_candidate_source_main,
)
from research_particle.recorders import CandidateSnapshotRecorder, SettlementLabelRecorder
from research_particle.replay_runner import (
    ReplayConfig,
    ReplayInput,
    evaluate_online_calibrated_replay,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
    write_online_replay_report,
    write_replay_report,
)
from research_particle.rv600_variation_test import (
    RV600VariantRunRow,
    build_rv600_variation_report,
    evaluate_variant_specs,
    first_candidate_specs,
    main as rv600_variation_test_main,
    materialize_rv600_metrics,
    write_rv600_variation_report,
    _summarize,
)
from probe_rv600_sidecar_shadow_root import (
    build_sidecar_shadow_root,
    write_sidecar_shadow_root,
)
from probe_rv600_native_offline_v28_contexts import (
    MarketMeta,
    build_offline_context_rows,
)
from research_particle.replay_diagnostics import (
    build_diagnostics,
    main as replay_diagnostics_main,
)
from research_particle.side_regime_diagnostic import (
    build_side_regime_diagnostic,
    main as side_regime_diagnostic_main,
)
from research_particle.state_feature_loro import (
    build_state_feature_loro_report,
    main as state_feature_loro_main,
)
from research_particle.side_consensus_locked_oos_plan import (
    main as side_consensus_locked_oos_plan_main,
)
from research_particle.side_consensus_oos import main as side_consensus_oos_main
from research_particle.spot_context_merge import (
    SpotTickRow,
    load_spot_ticks,
    merge_contexts_with_spot,
    main as spot_context_merge_main,
)
from research_particle.spot_micro_loro import (
    build_spot_micro_loro_report,
    main as spot_micro_loro_main,
)
from research_particle.spot_drift_terminal_diagnostic import (
    build_spot_drift_terminal_diagnostic,
    main as spot_drift_terminal_diagnostic_main,
    recent_spot_drift_per_second,
)
from research_particle.spot_drift_regime_diagnostic import (
    build_spot_drift_regime_diagnostic,
    main as spot_drift_regime_diagnostic_main,
)
from research_particle.spot_rv_anchor_switch_loro import (
    build_spot_rv_anchor_switch_loro_report,
    main as spot_rv_anchor_switch_loro_main,
)
from research_particle.spot_rv_current_residual_loro import (
    build_spot_rv_current_residual_loro_report,
    main as spot_rv_current_residual_loro_main,
)
from research_particle.spot_realized_vol_terminal_diagnostic import (
    build_spot_realized_vol_terminal_diagnostic,
    main as spot_realized_vol_terminal_diagnostic_main,
    realized_annualized_vol_at_decision,
)
from research_particle.spot_realized_vol_terminal_oos import (
    evaluate_spot_realized_vol_terminal_oos,
    main as spot_realized_vol_terminal_oos_main,
    materialize_spot_realized_vol_terminal_rows,
)
from research_particle.spot_realized_vol_terminal_locked_oos_plan import (
    main as spot_realized_vol_terminal_locked_oos_plan_main,
)
from research_particle.spot_ticker_recorder import (
    parse_binance_trade_message,
    parse_coinbase_match_message,
)
from research_particle.schemas import CandidateSnapshot, SettlementLabel
from research_particle.shadow_adapter import (
    MissingShadowFieldError,
    ShadowCandidateAdapter,
    snapshot_from_shadow_context,
)
from research_particle.shadow_collect import main as shadow_collect_main
from research_particle.shadow_pipeline import main as shadow_pipeline_main
from research_particle.reports import main as particle_reports_main
from research_particle.replay import FutureDataLeakageError, assert_records_available_at_decision
from research_particle.selection_sweep import (
    evaluate_selection_sweep,
    main as selection_sweep_main,
)
from research_particle.variant_loro_selection_diagnostic import (
    build_variant_loro_selection_diagnostic,
    main as variant_loro_selection_diagnostic_main,
)
from research_particle.side_failure_analysis import main as side_failure_analysis_main
from research_particle.side_safety_oos import main as side_safety_oos_main
from research_particle.schemas import TimedRecord
from research_particle.terminal_projection import (
    WeightedTerminalSample,
    brownian_terminal_probability,
    shared_terminal_probabilities,
    simulate_terminal_samples,
    systematic_resample,
    terminal_label_yes,
    weighted_probability_yes,
)
from research_particle.validation import (
    brier_score,
    log_loss,
    pairwise_rank_correlation_sign,
    top_bucket_mean_pnl,
)
from research_particle.v28_event_adapter import AdaptedEvent, AdapterIssue, adapt_v28_event, adapt_v28_events_file
from research_particle.v28_context_source import (
    context_from_v28_event,
    convert_v28_events_to_passive_contexts,
    main as v28_context_source_main,
)
from research_particle.v28_context_tailer import (
    main as v28_context_tailer_main,
    run_v28_context_tailer,
)
from research_particle.v28_rolling_vol_transfer_diagnostic import (
    build_v28_rolling_vol_transfer_diagnostic,
    evaluate_transfer_rows,
    main as v28_rolling_vol_transfer_diagnostic_main,
    write_v28_rolling_vol_transfer_diagnostic,
)
from probe_particle_goal_completion_audit import (
    audit as particle_goal_audit,
    _real_report_clears_promotion,
    _synthetic_report_passes,
)
from probe_particle_shadow_run_preflight import build_preflight, write_preflight
from probe_particle_v28_event_contexts import main as v28_event_context_main


class ResearchParticleSyntheticTests(unittest.TestCase):
    def test_brownian_terminal_probability_matches_manual_normal_cdf(self) -> None:
        spot = 100_000.0
        strike = 100_200.0
        seconds = 15 * 60
        vol = 0.65
        seconds_per_year = 365 * 24 * 60 * 60
        sigma = vol / math.sqrt(seconds_per_year)
        z = math.log(spot / strike) / (sigma * math.sqrt(seconds))
        manual = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

        got = brownian_terminal_probability(spot, strike, seconds, vol)

        self.assertAlmostEqual(got, manual, places=12)

    def test_weighted_and_resampled_probabilities_are_close(self) -> None:
        samples = [
            WeightedTerminalSample(99.0, 1.0),
            WeightedTerminalSample(101.0, 2.0),
            WeightedTerminalSample(102.0, 3.0),
            WeightedTerminalSample(98.0, 2.0),
        ]
        weighted = weighted_probability_yes(samples, 100.0)
        resampled = systematic_resample(samples, seed=7)
        empirical = weighted_probability_yes(resampled, 100.0)

        self.assertAlmostEqual(weighted, 0.625)
        self.assertLess(abs(weighted - empirical), 0.13)

    def test_jump_hazard_increases_right_tail_probability(self) -> None:
        base = simulate_terminal_samples(
            spot=100.0,
            seconds_to_close=120,
            annualized_vol=0.2,
            sample_count=2500,
            seed=11,
        )
        jumpy = simulate_terminal_samples(
            spot=100.0,
            seconds_to_close=120,
            annualized_vol=0.2,
            sample_count=2500,
            seed=11,
            jump_intensity_per_second=0.02,
            jump_mean_log_return=0.002,
            jump_std_log_return=0.001,
        )

        self.assertGreater(
            weighted_probability_yes(jumpy, 100.2),
            weighted_probability_yes(base, 100.2),
        )

    def test_calibrator_does_not_update_until_label_arrives(self) -> None:
        calibrator = LabelGatedACICalibrator(q=0.1, step_size=0.05)
        before = calibrator.q

        calibrator.predict(0.8)
        after_predict = calibrator.q
        calibrator.update_with_label(0.8, 0)

        self.assertEqual(after_predict, before)
        self.assertNotEqual(calibrator.q, before)

    def test_online_logit_calibrator_predict_is_read_only_and_label_gated(self) -> None:
        calibrator = OnlineLogitCalibrator(learning_rate=0.2, l2=0.0)
        before_bias = calibrator.bias
        before_slope = calibrator.slope
        before_prediction = calibrator.predict(0.7)

        after_prediction = calibrator.predict(0.7)
        calibrator.update_with_label(0.7, 1)
        updated_prediction = calibrator.predict(0.7)

        self.assertGreaterEqual(calibrator.predict(0.0), calibrator.min_probability)
        self.assertLessEqual(calibrator.predict(1.0), 1.0 - calibrator.min_probability)
        self.assertEqual(before_prediction, after_prediction)
        self.assertNotEqual(calibrator.bias, before_bias)
        self.assertNotEqual(calibrator.slope, before_slope)
        self.assertGreater(updated_prediction, before_prediction)

    def test_replay_refuses_future_records(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        rows = [
            TimedRecord("known", decision - timedelta(seconds=2), decision, 1.0),
            TimedRecord("future", decision, decision + timedelta(milliseconds=1), 2.0),
        ]

        with self.assertRaises(FutureDataLeakageError):
            assert_records_available_at_decision(rows, decision)

    def test_terminal_label_uses_settlement_not_path_touch(self) -> None:
        strike = 100.0
        path_touched = True
        settlement_price = 99.9

        self.assertTrue(path_touched)
        self.assertFalse(terminal_label_yes(settlement_price, strike))

    def test_ev_formula_and_break_even_probability_match_hand_calculation(self) -> None:
        ev = expected_pnl_cents(
            p_win=0.6,
            ask_cents=55.0,
            fee_if_win_cents=1.0,
            fee_if_loss_cents=0.5,
            fill_prob=0.8,
            no_fill_penalty_cents=0.25,
        )
        # Filled EV = .6 * 44 - .4 * 55.5 = 4.2c. Fill adjusted = 3.36 - .05.
        self.assertAlmostEqual(ev, 3.31)

        breakeven = break_even_probability(55.0, fee_if_win_cents=1.0, fee_if_loss_cents=0.5)
        self.assertAlmostEqual(breakeven, 55.5 / 99.5)

    def test_no_fill_zero_realized_pnl_but_updates_fill_stats(self) -> None:
        stats = FillStats()
        stats.update(filled=False)

        self.assertEqual(realized_trade_pnl_cents(False, True, 40.0), 0.0)
        self.assertEqual(stats.attempts, 1)
        self.assertEqual(stats.no_fills, 1)
        self.assertEqual(stats.fills, 0)

    def test_shared_terminal_samples_match_per_strike_probabilities(self) -> None:
        samples = simulate_terminal_samples(
            spot=100.0,
            seconds_to_close=30,
            annualized_vol=0.4,
            sample_count=500,
            seed=123,
        )
        strikes = [99.5, 100.0, 100.5]

        shared = shared_terminal_probabilities(samples, strikes)

        for strike in strikes:
            self.assertAlmostEqual(shared[strike], weighted_probability_yes(samples, strike))

    def test_recorders_write_candidate_and_label_jsonl(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-TEST",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=101.0,
            yes_ask_cents=60.0,
            no_ask_cents=42.0,
            fee_cents=1.0,
            fill_prob=0.7,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-TEST",
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.5,
            strike=100.0,
        )

        CandidateSnapshotRecorder(root).record(snapshot, decision_shadow="skip", reason="synthetic")
        SettlementLabelRecorder(root).record(label, source="unit_test")

        candidate_lines = (root / "candidate_snapshots" / "candidate_snapshots.ndjson").read_text(
            encoding="utf-8"
        ).splitlines()
        label_lines = (root / "settlement_labels" / "settlement_labels.ndjson").read_text(
            encoding="utf-8"
        ).splitlines()

        self.assertEqual(len(candidate_lines), 1)
        self.assertEqual(len(label_lines), 1)
        self.assertEqual(json.loads(candidate_lines[0])["record_type"], "candidate_snapshot")
        self.assertEqual(json.loads(label_lines[0])["result_yes"], True)

    def test_labeler_refuses_label_before_available_time(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-TEST",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=100.1,
            yes_ask_cents=55.0,
            no_ask_cents=47.0,
            fee_cents=1.0,
            fill_prob=0.6,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-TEST",
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.0,
            strike=100.0,
        )

        with self.assertRaises(LabelUnavailableError):
            label_candidate(snapshot, label, side="yes", filled=True, as_of_ts_utc=decision)

        labeled = label_candidate(
            snapshot,
            label,
            side="yes",
            filled=True,
            as_of_ts_utc=decision + timedelta(minutes=16),
        )
        self.assertTrue(labeled.won)
        self.assertAlmostEqual(labeled.counterfactual_pnl_cents, 44.0)

    def test_validation_metrics_cover_probability_and_ev_ranking(self) -> None:
        probabilities = [0.8, 0.7, 0.2, 0.1]
        labels = [1, 1, 0, 0]
        predicted_ev = [8.0, 6.0, -1.0, -4.0]
        realized = [10.0, 4.0, -2.0, -5.0]

        self.assertLess(brier_score(probabilities, labels), 0.07)
        self.assertLess(log_loss(probabilities, labels), 0.4)
        self.assertGreater(pairwise_rank_correlation_sign(predicted_ev, realized), 0.0)
        self.assertGreater(top_bucket_mean_pnl(predicted_ev, realized, top_fraction=0.25), 0.0)

    def test_end_to_end_synthetic_replay_from_recorded_jsonl(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        rows = [
            ("KXBTC15M-SYN1", 100.0, 101.0, 60.0, 42.0, 0.85, 0.60, 0.55, 0.65, 101.2),
            ("KXBTC15M-SYN2", 100.0, 100.7, 65.0, 37.0, 0.75, 0.55, 0.52, 0.60, 100.4),
            ("KXBTC15M-SYN3", 100.0, 99.4, 38.0, 60.0, 0.25, 0.45, 0.48, 0.40, 99.0),
            ("KXBTC15M-SYN4", 100.0, 98.9, 30.0, 70.0, 0.15, 0.40, 0.45, 0.35, 99.6),
        ]
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        for idx, (
            ticker,
            strike,
            spot,
            yes_ask,
            no_ask,
            particle_p,
            brownian_p,
            market_p,
            current_p,
            settlement,
        ) in enumerate(rows):
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=decision + timedelta(seconds=idx),
                recv_ts_utc=decision + timedelta(seconds=idx),
                strike=strike,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=strike,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="synthetic_end_to_end",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        replay_rows = load_replay_inputs_from_jsonl(
            root / "candidate_snapshots" / "candidate_snapshots.ndjson",
            root / "settlement_labels" / "settlement_labels.ndjson",
        )
        report = evaluate_replay(
            replay_rows,
            ReplayConfig(
                min_ev_cents=1.0,
                min_fill_prob=0.5,
                counterfactual_fill_policy="threshold",
                counterfactual_fill_threshold=0.5,
            ),
        )
        json_path, md_path = write_replay_report(report, root / "reports", "synthetic_replay")

        self.assertEqual(report.candidate_count, 4)
        self.assertTrue(report.all_candidate_denominator)
        self.assertEqual(report.selected_count, 4)
        self.assertTrue(report.particle_beats_brownian)
        self.assertTrue(report.particle_beats_market)
        self.assertTrue(report.particle_beats_current_calibrated)
        self.assertGreater(report.ev_rank_correlation_sign, 0.0)
        self.assertGreater(report.top_ev_bucket_pnl_cents, 0.0)
        self.assertTrue(report.shadow_counterfactual_positive)
        self.assertTrue(json_path.exists())
        self.assertIn("particle_beats_brownian", md_path.read_text(encoding="utf-8"))

    def test_probability_variants_cli_writes_fixed_anchor_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-VARIANT1", 101.0, 40.0, 65.0, 0.55, 0.50, 0.90, 0.60, 101.0),
            ("KXBTC15M-VARIANT2", 99.0, 65.0, 40.0, 0.45, 0.50, 0.10, 0.40, 99.0),
        ]
        for idx, (
            ticker,
            spot,
            yes_ask,
            no_ask,
            particle_p,
            brownian_p,
            market_p,
            current_p,
            settlement,
        ) in enumerate(rows):
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=decision + timedelta(seconds=idx),
                recv_ts_utc=decision + timedelta(seconds=idx),
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="variant_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = probability_variants_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "variants",
                    "--min-fill-prob",
                    "0.5",
                    "--counterfactual-fill-threshold",
                    "0.5",
                ]
            )

        payload = json.loads((root / "reports" / "variants.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["candidate_count"], 2)
        self.assertEqual(payload["source_candidate_count"], 2)
        self.assertEqual(payload["skipped_unlabeled_count"], 0)
        self.assertFalse(payload["promotion_safe"])
        self.assertEqual(payload["best_by_brier"]["name"], "market")
        self.assertIn("best_by_pnl", stdout.getvalue())
        self.assertIn("same-sample", (root / "reports" / "variants.md").read_text(encoding="utf-8"))

    def test_rolling_vol_estimator_uses_only_distinct_chronological_spots(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        estimator = RollingVolEstimator(
            DynamicParticleSpec(
                name="unit",
                lookback_seconds=120.0,
                fallback_annualized_vol=0.65,
                min_annualized_vol=0.2,
                max_annualized_vol=2.5,
                min_distinct_observations=3,
            )
        )

        first = estimator.observe_and_estimate(decision, 100.0)
        duplicate = estimator.observe_and_estimate(decision + timedelta(seconds=1), 100.0)
        moved_once = estimator.observe_and_estimate(decision + timedelta(seconds=2), 100.1)
        moved_twice = estimator.observe_and_estimate(decision + timedelta(seconds=3), 100.2)

        self.assertEqual(first, 0.65)
        self.assertEqual(duplicate, 0.65)
        self.assertEqual(moved_once, 0.65)
        self.assertNotEqual(moved_twice, 0.65)
        self.assertTrue(0.2 <= moved_twice <= 2.5)

    def test_dynamic_particle_replay_cli_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-DYN1", decision, 100.0, 50.0, 52.0, 0.50, 0.50, 0.50, 0.52, 101.0),
            ("KXBTC15M-DYN2", decision + timedelta(seconds=1), 100.3, 48.0, 54.0, 0.55, 0.50, 0.52, 0.54, 101.0),
            ("KXBTC15M-DYN3", decision + timedelta(seconds=2), 99.7, 54.0, 48.0, 0.45, 0.50, 0.48, 0.46, 99.0),
        ]
        for ticker, ts, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="dynamic_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = dynamic_particle_replay_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "dynamic",
                ]
            )

        payload = json.loads((root / "reports" / "dynamic.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["candidate_count"], 3)
        self.assertEqual(payload["source_candidate_count"], 3)
        self.assertFalse(payload["promotion_safe"])
        self.assertGreaterEqual(len(payload["rows"]), 4)
        self.assertIn("best_by_brier", stdout.getvalue())
        self.assertIn("same-sample", (root / "reports" / "dynamic.md").read_text(encoding="utf-8"))

    def test_dynamic_particle_oos_cli_blocks_same_sample_promotion(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-DYNOOS1", decision, 100.0, 50.0, 52.0, 0.50, 0.50, 0.50, 0.52, 101.0),
            ("KXBTC15M-DYNOOS2", decision + timedelta(seconds=1), 100.3, 48.0, 54.0, 0.55, 0.50, 0.52, 0.54, 101.0),
            ("KXBTC15M-DYNOOS3", decision + timedelta(seconds=2), 99.7, 54.0, 48.0, 0.45, 0.50, 0.48, 0.46, 99.0),
        ]
        for ticker, ts, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="dynamic_oos_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = dynamic_particle_oos_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "dynamic_oos",
                    "--hypothesis-id",
                    "rolling_vol_300s_v1",
                    "--evaluation-scope",
                    "same_sample_diagnostic",
                    "--gate-min-candidates",
                    "1",
                    "--gate-min-markets",
                    "1",
                    "--gate-min-selected",
                    "1",
                ]
            )

        payload = json.loads((root / "reports" / "dynamic_oos.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "rolling_vol_300s_v1")
        self.assertEqual(payload["variant_name"], "rolling_vol_300s")
        self.assertEqual(payload["evaluation_scope"], "same_sample_diagnostic")
        self.assertFalse(payload["gate_results"]["locked_oos_scope"])
        self.assertFalse(payload["gate_results"]["all_passed"])
        self.assertFalse(payload["promotion_safe"])
        self.assertIn("promotion_safe=False", stdout.getvalue())
        self.assertIn("Same-sample", (root / "reports" / "dynamic_oos.md").read_text(encoding="utf-8"))

    def test_ensemble_particle_replay_cli_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-ENS1", decision, 100.0, 50.0, 52.0, 0.50, 0.50, 0.50, 0.52, 101.0),
            ("KXBTC15M-ENS2", decision + timedelta(seconds=1), 100.3, 48.0, 54.0, 0.55, 0.50, 0.52, 0.54, 101.0),
            ("KXBTC15M-ENS3", decision + timedelta(seconds=2), 99.7, 54.0, 48.0, 0.45, 0.50, 0.48, 0.46, 99.0),
        ]
        for ticker, ts, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="ensemble_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = ensemble_particle_replay_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "ensemble",
                ]
            )

        payload = json.loads((root / "reports" / "ensemble.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["candidate_count"], 3)
        self.assertEqual(payload["source_candidate_count"], 3)
        self.assertFalse(payload["promotion_safe"])
        self.assertGreaterEqual(len(payload["rows"]), 4)
        self.assertIn("best_by_brier", stdout.getvalue())
        self.assertIn("Ensemble Particle Replay", (root / "reports" / "ensemble.md").read_text(encoding="utf-8"))

    def test_residual_blend_loro_cli_writes_research_only_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        for run_index in range(2):
            run_root = root / f"run{run_index + 1}"
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            rows = [
                (0, 100.4, 47.0, 55.0, 0.72, 0.58, 0.62, 0.68, 101.0),
                (1, 99.6, 56.0, 46.0, 0.30, 0.42, 0.38, 0.34, 99.0),
                (2, 100.2, 49.0, 53.0, 0.65, 0.54, 0.56, 0.61, 101.0),
                (3, 99.8, 53.0, 49.0, 0.36, 0.46, 0.44, 0.39, 99.0),
            ]
            for offset, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
                ticker = f"KXBTC15M-RESID{run_index}-{offset}"
                ts = decision + timedelta(seconds=run_index * 30 + offset)
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=spot,
                    yes_ask_cents=yes_ask,
                    no_ask_cents=no_ask,
                    fee_cents=1.0,
                    fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=decision + timedelta(minutes=15),
                    label_available_ts_utc=decision + timedelta(minutes=16),
                    settlement_price=settlement,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="residual_loro_unit",
                    extra={
                        "particle_p_yes": particle_p,
                        "brownian_p_yes": brownian_p,
                        "market_p_yes": market_p,
                        "current_calibrated_p_yes": current_p,
                    },
                )
                label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = residual_blend_loro_main(
                [
                    "--report-root",
                    str(root / "run1"),
                    "--report-root",
                    str(root / "run2"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "residual",
                    "--max-exact-global",
                    "2",
                ]
            )

        payload = json.loads((root / "reports" / "residual.json").read_text(encoding="utf-8"))
        markdown = (root / "reports" / "residual.md").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["run_count"], 2)
        self.assertGreater(payload["coefficient_count"], 1)
        self.assertEqual(len(payload["loro_picks"]), 2)
        self.assertFalse(payload["promotion_safe"])
        self.assertIn("current + a*(market-current)", payload["formula"])
        self.assertIn("requires a fresh predeclared locked OOS", payload["note"])
        self.assertIn("best_global_exact=", stdout.getvalue())
        self.assertIn("Residual Blend LORO Report", markdown)

    def test_residual_blend_oos_blocks_same_sample_and_passes_locked_scope(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-RBOOS1", 0, 100.0, 60.0, 60.0, 0.20, 0.50, 0.50, 0.70, 101.0),
            ("KXBTC15M-RBOOS2", 1, 100.0, 59.0, 59.0, 0.90, 0.50, 0.50, 0.31, 99.0),
            ("KXBTC15M-RBOOS3", 2, 100.0, 58.0, 58.0, 0.00, 0.50, 0.50, 0.68, 101.0),
            ("KXBTC15M-RBOOS4", 3, 100.0, 57.0, 57.0, 1.00, 0.50, 0.50, 0.33, 99.0),
        ]
        for ticker, offset, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
            ts = decision + timedelta(seconds=offset)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="residual_oos_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        common_args = [
            "--candidates",
            str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
            "--labels",
            str(root / "settlement_labels" / "settlement_labels.ndjson"),
            "--min-ev-cents",
            "10",
            "--gate-min-candidates",
            "1",
            "--gate-min-markets",
            "1",
            "--gate-min-selected",
            "1",
        ]
        with contextlib.redirect_stdout(io.StringIO()) as stdout_same:
            same_exit = residual_blend_oos_main(
                [
                    *common_args,
                    "--output-dir",
                    str(root / "reports_same"),
                    "--stem",
                    "residual_oos",
                    "--evaluation-scope",
                    "same_sample_diagnostic",
                ]
            )
        with contextlib.redirect_stdout(io.StringIO()) as stdout_locked:
            locked_exit = residual_blend_oos_main(
                [
                    *common_args,
                    "--output-dir",
                    str(root / "reports_locked"),
                    "--stem",
                    "residual_oos",
                    "--evaluation-scope",
                    "locked_oos_shadow",
                ]
            )

        same_payload = json.loads((root / "reports_same" / "residual_oos.json").read_text(encoding="utf-8"))
        locked_payload = json.loads((root / "reports_locked" / "residual_oos.json").read_text(encoding="utf-8"))
        self.assertEqual(same_exit, 0)
        self.assertEqual(locked_exit, 0)
        self.assertFalse(same_payload["gate_results"]["locked_oos_scope"])
        self.assertFalse(same_payload["promotion_safe"])
        self.assertTrue(locked_payload["gate_results"]["locked_oos_scope"])
        self.assertTrue(locked_payload["promotion_safe"])
        self.assertGreater(locked_payload["selected_variant"]["total_counterfactual_pnl_cents"], 0.0)
        self.assertTrue(locked_payload["gate_results"]["beats_current_calibrated_pnl"])
        self.assertIn("promotion_safe=True", stdout_locked.getvalue())
        self.assertIn("promotion_safe=False", stdout_same.getvalue())
        self.assertIn(
            "Residual Blend OOS Report",
            (root / "reports_locked" / "residual_oos.md").read_text(encoding="utf-8"),
        )

    def test_online_logit_particle_replay_cli_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-LOGIT1", 0, 120, 100.2, 52.0, 50.0, 0.60, 0.55, 0.53, 0.58, 101.0),
            ("KXBTC15M-LOGIT2", 60, 180, 100.4, 54.0, 48.0, 0.62, 0.56, 0.54, 0.59, 101.0),
            ("KXBTC15M-LOGIT3", 150, 240, 99.6, 45.0, 57.0, 0.40, 0.44, 0.46, 0.42, 99.0),
        ]
        replay_rows: list[ReplayInput] = []
        for ticker, decision_offset, label_offset, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
            ts = decision + timedelta(seconds=decision_offset)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(seconds=label_offset),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="online_logit_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")
            replay_rows.append(
                ReplayInput(
                    snapshot=snapshot,
                    label=label,
                    particle_p_yes=particle_p,
                    brownian_p_yes=brownian_p,
                    market_p_yes=market_p,
                    current_calibrated_p_yes=current_p,
                )
            )

        report = evaluate_online_logit_particle_variants(replay_rows, learning_rate=0.1, l2=0.0)
        self.assertEqual(report.candidate_count, 3)
        self.assertFalse(report.promotion_safe)
        self.assertEqual(report.update_mode, "candidate")
        self.assertEqual(report.rows[0].update_count, 3)
        self.assertNotEqual(report.rows[0].final_bias, 0.0)
        clustered = evaluate_online_logit_particle_variants(
            replay_rows,
            learning_rate=0.1,
            l2=0.0,
            update_mode="market_mean",
        )
        self.assertEqual(clustered.update_mode, "market_mean")
        self.assertTrue(clustered.rows[0].name.startswith("online_logit_market_mean_"))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = online_logit_particle_replay_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "online_logit",
                    "--learning-rate",
                    "0.1",
                    "--l2",
                    "0",
                ]
            )

        payload = json.loads((root / "reports" / "online_logit.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["candidate_count"], 3)
        self.assertEqual(payload["source_candidate_count"], 3)
        self.assertEqual(payload["update_mode"], "candidate")
        self.assertFalse(payload["promotion_safe"])
        self.assertGreaterEqual(len(payload["rows"]), 4)
        self.assertIn("best_by_brier", stdout.getvalue())
        self.assertIn("Online Logit Particle Replay", (root / "reports" / "online_logit.md").read_text(encoding="utf-8"))

    def test_online_anchor_calibration_diagnostic_is_label_gated(self) -> None:
        root = Path(tempfile.mkdtemp())
        run_roots = [root / "run1", root / "run2"]
        base_ts = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        for run_idx, run_root in enumerate(run_roots):
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            rows = [
                ("KXBTC15M-ANCHOR1", 0, True, 100.4, 56.0, 46.0, 0.62, 0.58, 0.57, 0.60),
                ("KXBTC15M-ANCHOR1", 30, True, 100.5, 57.0, 45.0, 0.63, 0.59, 0.58, 0.61),
                ("KXBTC15M-ANCHOR2", 1200, False, 99.4, 43.0, 59.0, 0.38, 0.42, 0.44, 0.40),
                ("KXBTC15M-ANCHOR2", 1230, False, 99.5, 44.0, 58.0, 0.39, 0.43, 0.45, 0.41),
            ]
            for ticker, offset, result_yes, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p in rows:
                decision_ts = base_ts + timedelta(seconds=offset + run_idx * 10)
                snapshot = CandidateSnapshot(
                    market_ticker=f"{ticker}-R{run_idx}",
                    decision_ts_utc=decision_ts,
                    recv_ts_utc=decision_ts,
                    strike=100.0,
                    spot=spot,
                    yes_ask_cents=yes_ask,
                    no_ask_cents=no_ask,
                    fee_cents=1.0,
                    fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=f"{ticker}-R{run_idx}",
                    settlement_ts_utc=decision_ts + timedelta(minutes=15),
                    label_available_ts_utc=decision_ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="online_anchor_unit",
                    extra={
                        "particle_p_yes": particle_p,
                        "brownian_p_yes": brownian_p,
                        "market_p_yes": market_p,
                        "current_calibrated_p_yes": current_p,
                    },
                )
                label_recorder.record(label, source="online_anchor_unit")

        report = build_online_anchor_calibration_diagnostic(run_roots)
        self.assertEqual(len(report.run_inputs), 2)
        self.assertFalse(report.promotion_safe)
        self.assertTrue(any(row.update_mode == "market_last" for row in report.summary_rows))
        self.assertTrue(
            any(
                row.spec == "online_logit_brownian_lr003_row"
                and row.run_count == 2
                for row in report.summary_rows
            )
        )

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = online_anchor_calibration_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "online_anchor",
                ]
            )
        payload = json.loads((root / "reports" / "online_anchor.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["spec_count"], 12)
        self.assertIn("best_by_brier", stdout.getvalue())
        self.assertIn("Online Anchor Calibration Diagnostic", (root / "reports" / "online_anchor.md").read_text(encoding="utf-8"))

    def test_anchor_regime_profile_reports_anchor_winners_by_scope(self) -> None:
        root = Path(tempfile.mkdtemp())
        run_roots = [root / "run1", root / "run2"]
        base_ts = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        for run_idx, run_root in enumerate(run_roots):
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            rows = [
                ("KXBTC15M-PROFILE1", 0, True, 100.5, 55.0, 47.0, 0.62, 0.58, 0.56, 0.90),
                ("KXBTC15M-PROFILE1", 30, True, 100.4, 56.0, 46.0, 0.61, 0.57, 0.55, 0.88),
                ("KXBTC15M-PROFILE2", 1200, False, 99.5, 45.0, 57.0, 0.38, 0.42, 0.44, 0.10),
                ("KXBTC15M-PROFILE2", 1230, False, 99.4, 44.0, 58.0, 0.39, 0.43, 0.45, 0.12),
            ]
            for ticker, offset, result_yes, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p in rows:
                decision_ts = base_ts + timedelta(seconds=offset + run_idx * 5)
                market_ticker = f"{ticker}-R{run_idx}"
                snapshot = CandidateSnapshot(
                    market_ticker=market_ticker,
                    decision_ts_utc=decision_ts,
                    recv_ts_utc=decision_ts,
                    strike=100.0,
                    spot=spot,
                    yes_ask_cents=yes_ask,
                    no_ask_cents=no_ask,
                    fee_cents=1.0,
                    fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=market_ticker,
                    settlement_ts_utc=decision_ts + timedelta(minutes=15),
                    label_available_ts_utc=decision_ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="anchor_profile_unit",
                    extra={
                        "particle_p_yes": particle_p,
                        "brownian_p_yes": brownian_p,
                        "market_p_yes": market_p,
                        "current_calibrated_p_yes": current_p,
                    },
                )
                label_recorder.record(label, source="anchor_profile_unit")

        report = build_anchor_regime_profile(run_roots)
        self.assertFalse(report.promotion_safe)
        self.assertEqual(report.run_best_counts_by_brier["current_calibrated"], 2)
        self.assertTrue(any(row.scope == "state_bucket" for row in report.winner_rows))
        self.assertTrue(any(row.scope == "market" for row in report.winner_rows))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = anchor_regime_profile_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "anchor_profile",
                ]
            )
        payload = json.loads((root / "reports" / "anchor_profile.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["run_best_counts_by_brier"]["current_calibrated"], 2)
        self.assertIn("market_best_counts_by_brier", stdout.getvalue())
        self.assertIn("Anchor Regime Profile", (root / "reports" / "anchor_profile.md").read_text(encoding="utf-8"))

    def test_materialized_variant_replay_cli_writes_full_decision_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        replay_rows: list[ReplayInput] = []
        rows = [
            ("KXBTC15M-MAT1", 0, 120, 100.2, 52.0, 50.0, 0.60, 0.55, 0.53, 0.58, 101.0),
            ("KXBTC15M-MAT2", 60, 180, 99.6, 45.0, 57.0, 0.40, 0.44, 0.46, 0.42, 99.0),
        ]
        for ticker, decision_offset, label_offset, spot, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement in rows:
            ts = decision + timedelta(seconds=decision_offset)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(seconds=label_offset),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="materialized_variant_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")
            replay_rows.append(
                ReplayInput(
                    snapshot=snapshot,
                    label=label,
                    particle_p_yes=particle_p,
                    brownian_p_yes=brownian_p,
                    market_p_yes=market_p,
                    current_calibrated_p_yes=current_p,
                )
            )

        materialized = materialize_variant_rows(
            replay_rows,
            "online_logit_market_mean_rolling_vol_600s",
        )
        self.assertEqual(len(materialized), 2)
        self.assertTrue(0.0 <= materialized[0].particle_p_yes <= 1.0)
        late_blended = materialize_variant_rows(
            replay_rows,
            "late300_mc75_online_logit_rv600",
        )
        self.assertEqual(len(late_blended), 2)
        self.assertTrue(0.0 <= late_blended[0].particle_p_yes <= 1.0)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = materialized_variant_replay_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--variant",
                    "online_logit_market_mean_rolling_vol_600s",
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "materialized",
                ]
            )

        payload = json.loads((root / "reports" / "materialized.json").read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertEqual(payload["candidate_count"], 2)
        self.assertEqual(payload["source_candidate_count"], 2)
        self.assertEqual(len(payload["decisions"]), 2)
        self.assertIn("variant=online_logit_market_mean_rolling_vol_600s", stdout.getvalue())

        with contextlib.redirect_stdout(io.StringIO()) as sweep_stdout:
            sweep_result = materialized_variant_selection_sweep_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--variant",
                    "online_logit_market_mean_rolling_vol_600s",
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "materialized_sweep",
                    "--min-ev-grid",
                    "0,5",
                    "--min-fill-grid",
                    "0",
                ]
            )
        sweep_payload = json.loads((root / "reports" / "materialized_sweep.json").read_text(encoding="utf-8"))
        self.assertEqual(sweep_result, 0)
        self.assertEqual(len(sweep_payload["rows"]), 2)
        self.assertIn("variant=online_logit_market_mean_rolling_vol_600s", sweep_stdout.getvalue())

    def test_side_failure_analysis_cli_reports_forced_side_counterfactuals(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-SIDE1", 40.0, 65.0, 0.80, 0.50, 0.50, 0.50, 99.0),
            ("KXBTC15M-SIDE2", 65.0, 40.0, 0.20, 0.50, 0.50, 0.50, 101.0),
        ]
        for idx, (ticker, yes_ask, no_ask, particle_p, brownian_p, market_p, current_p, settlement) in enumerate(rows):
            ts = decision + timedelta(seconds=idx)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=100.0,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="side_failure_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": brownian_p,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = side_failure_analysis_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "side_failure",
                ]
            )

        payload = json.loads((root / "reports" / "side_failure.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["candidate_count"], 2)
        self.assertFalse(payload["promotion_safe"])
        self.assertEqual(payload["selected_yes"]["total_counterfactual_pnl_cents"], -40.0)
        self.assertEqual(payload["selected_no"]["total_counterfactual_pnl_cents"], -40.0)
        self.assertLess(payload["selected_yes"]["selected_minus_opposite_pnl_cents"], 0.0)
        self.assertLess(payload["selected_no"]["selected_minus_opposite_pnl_cents"], 0.0)
        self.assertIn("forced_yes_total_counterfactual_pnl_cents", stdout.getvalue())
        self.assertIn("Forced Side Summary", (root / "reports" / "side_failure.md").read_text(encoding="utf-8"))

    def test_side_safety_oos_cli_blocks_same_sample_promotion(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-SAFETY1", 40.0, 65.0, 0.80, 99.0),
            ("KXBTC15M-SAFETY2", 65.0, 40.0, 0.80, 101.0),
            ("KXBTC15M-SAFETY3", 45.0, 60.0, 0.75, 101.0),
            ("KXBTC15M-SAFETY4", 60.0, 45.0, 0.25, 99.0),
        ]
        for idx, (ticker, yes_ask, no_ask, particle_p, settlement) in enumerate(rows):
            ts = decision + timedelta(seconds=idx)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=100.0,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="side_safety_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": 0.5,
                    "market_p_yes": 0.5,
                    "current_calibrated_p_yes": 0.5,
                },
            )
            label_recorder.record(label, source="synthetic")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = side_safety_oos_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "side_safety",
                    "--evaluation-scope",
                    "same_sample_diagnostic",
                    "--gate-min-candidates",
                    "1",
                    "--gate-min-markets",
                    "1",
                    "--gate-min-selected",
                    "1",
                ]
            )

        payload = json.loads((root / "reports" / "side_safety.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "side_safe_yes_only_v1")
        self.assertEqual(payload["evaluation_scope"], "same_sample_diagnostic")
        self.assertFalse(payload["gate_results"]["locked_oos_scope"])
        self.assertFalse(payload["gate_results"]["all_passed"])
        self.assertFalse(payload["promotion_safe"])
        self.assertGreater(payload["side_safe_selected_count"], 0)
        self.assertIn("promotion_safe=False", stdout.getvalue())
        self.assertIn("same-sample", (root / "reports" / "side_safety.md").read_text(encoding="utf-8"))

    def test_side_consensus_oos_blocks_same_sample_and_passes_locked_scope(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        rows = [
            ("KXBTC15M-CONSENSUS1", 70.0, 30.0, 0.20, 0.70, 0.65, 101.0),
            ("KXBTC15M-CONSENSUS2", 30.0, 70.0, 0.80, 0.70, 0.65, 101.0),
            ("KXBTC15M-CONSENSUS3", 80.0, 20.0, 0.10, 0.30, 0.35, 99.0),
        ]
        for idx, (ticker, yes_ask, no_ask, particle_p, market_p, current_p, settlement) in enumerate(rows):
            ts = decision + timedelta(seconds=idx)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=100.0,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=settlement,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="side_consensus_unit",
                extra={
                    "particle_p_yes": particle_p,
                    "brownian_p_yes": 0.5,
                    "market_p_yes": market_p,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="synthetic")

        common_args = [
            "--candidates",
            str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
            "--labels",
            str(root / "settlement_labels" / "settlement_labels.ndjson"),
            "--gate-min-candidates",
            "1",
            "--gate-min-markets",
            "1",
            "--gate-min-selected",
            "1",
        ]
        with contextlib.redirect_stdout(io.StringIO()) as stdout_same:
            same_exit = side_consensus_oos_main(
                [
                    *common_args,
                    "--output-dir",
                    str(root / "reports_same"),
                    "--stem",
                    "side_consensus",
                    "--evaluation-scope",
                    "same_sample_diagnostic",
                ]
            )
        with contextlib.redirect_stdout(io.StringIO()) as stdout_locked:
            locked_exit = side_consensus_oos_main(
                [
                    *common_args,
                    "--output-dir",
                    str(root / "reports_locked"),
                    "--stem",
                    "side_consensus",
                    "--evaluation-scope",
                    "locked_oos_shadow",
                ]
            )

        same_payload = json.loads((root / "reports_same" / "side_consensus.json").read_text(encoding="utf-8"))
        locked_payload = json.loads((root / "reports_locked" / "side_consensus.json").read_text(encoding="utf-8"))
        self.assertEqual(same_exit, 0)
        self.assertEqual(locked_exit, 0)
        self.assertEqual(same_payload["hypothesis_id"], "skip_against_market_current_consensus_10_v1")
        self.assertFalse(same_payload["gate_results"]["locked_oos_scope"])
        self.assertFalse(same_payload["promotion_safe"])
        self.assertEqual(locked_payload["blocked_against_consensus_count"], 1)
        self.assertEqual(locked_payload["consensus_selected_count"], 2)
        self.assertGreater(locked_payload["consensus_total_counterfactual_pnl_cents"], 0.0)
        self.assertGreater(
            locked_payload["consensus_total_counterfactual_pnl_cents"],
            locked_payload["base_total_counterfactual_pnl_cents"],
        )
        self.assertTrue(locked_payload["gate_results"]["all_candidate_denominator"])
        self.assertTrue(locked_payload["promotion_safe"])
        self.assertIn("promotion_safe=False", stdout_same.getvalue())
        self.assertIn("promotion_safe=True", stdout_locked.getvalue())
        self.assertIn(
            "Same-sample reports are not promotion evidence",
            (root / "reports_locked" / "side_consensus.md").read_text(encoding="utf-8"),
        )

    def test_locked_oos_run_plan_writes_predeclared_command_manifest(self) -> None:
        root = Path(tempfile.mkdtemp())

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = locked_oos_run_plan_main(
                [
                    "--run-id",
                    "UNITLOCK",
                    "--dataset",
                    "particle_side_safety_oos_unit",
                    "--artifact-root",
                    str(root / "artifacts"),
                    "--output-dir",
                    str(root / "plans"),
                    "--stem",
                    "locked_plan",
                    "--run-seconds",
                    "3900",
                    "--gate-min-candidates",
                    "500",
                    "--gate-min-markets",
                    "4",
                    "--gate-min-selected",
                    "100",
                ]
            )

        payload = json.loads((root / "plans" / "locked_plan.json").read_text(encoding="utf-8"))
        md = (root / "plans" / "locked_plan.md").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "side_safe_yes_only_v1")
        self.assertEqual(payload["evaluation_scope"], "locked_oos_shadow")
        self.assertEqual(payload["gate_config"]["min_market_count"], 4)
        self.assertIn("--evaluation-scope locked_oos_shadow", payload["side_safety_oos_command"])
        self.assertIn("paired_passive_shadow_run", payload["paired_capture_command"])
        self.assertIn("research_particle.side_safety_oos", md)
        self.assertIn("json_plan=", stdout.getvalue())

    def test_side_consensus_locked_oos_plan_uses_independent_spot_and_locked_command(self) -> None:
        root = Path(tempfile.mkdtemp())

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = side_consensus_locked_oos_plan_main(
                [
                    "--run-id",
                    "UNITCONSLOCK",
                    "--dataset",
                    "particle_side_consensus_oos_unit",
                    "--artifact-root",
                    str(root / "artifacts"),
                    "--output-dir",
                    str(root / "plans"),
                    "--stem",
                    "side_consensus_locked_plan",
                    "--run-seconds",
                    "3900",
                    "--gate-min-candidates",
                    "1000",
                    "--gate-min-markets",
                    "5",
                    "--gate-min-selected",
                    "100",
                ]
            )

        payload = json.loads((root / "plans" / "side_consensus_locked_plan.json").read_text(encoding="utf-8"))
        md = (root / "plans" / "side_consensus_locked_plan.md").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "skip_against_market_current_consensus_10_v1")
        self.assertEqual(payload["evaluation_scope"], "locked_oos_shadow")
        self.assertEqual(payload["independent_spot_feed"], "coinbase")
        self.assertIn("--record-independent-spot", payload["paired_capture_command"])
        self.assertIn("--require-independent-spot", payload["paired_capture_command"])
        self.assertIn("passive_contexts_independent_spot.ndjson", payload["pipeline_command"])
        self.assertIn("research_particle.side_consensus_oos", payload["side_consensus_oos_command"])
        self.assertIn("--evaluation-scope locked_oos_shadow", payload["side_consensus_oos_command"])
        self.assertIn("research_particle.side_regime_diagnostic", md)
        self.assertIn("json_plan=", stdout.getvalue())

    def test_residual_blend_locked_oos_plan_uses_independent_spot_and_locked_command(self) -> None:
        root = Path(tempfile.mkdtemp())

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = residual_blend_locked_oos_plan_main(
                [
                    "--run-id",
                    "UNITRESIDLOCK",
                    "--dataset",
                    "particle_residual_blend_oos_unit",
                    "--artifact-root",
                    str(root / "artifacts"),
                    "--output-dir",
                    str(root / "plans"),
                    "--stem",
                    "residual_locked_plan",
                    "--run-seconds",
                    "3900",
                    "--gate-min-candidates",
                    "1000",
                    "--gate-min-markets",
                    "5",
                    "--gate-min-selected",
                    "250",
                ]
            )

        payload = json.loads((root / "plans" / "residual_locked_plan.json").read_text(encoding="utf-8"))
        md = (root / "plans" / "residual_locked_plan.md").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "resid_current_rv300n20_rv600p20_particle_n10_v1")
        self.assertEqual(payload["evaluation_scope"], "locked_oos_shadow")
        self.assertEqual(payload["independent_spot_feed"], "coinbase")
        self.assertEqual(payload["gate_config"]["min_market_count"], 5)
        self.assertIn("--record-independent-spot", payload["paired_capture_command"])
        self.assertIn("--require-independent-spot", payload["paired_capture_command"])
        self.assertIn("passive_contexts_independent_spot.ndjson", payload["pipeline_command"])
        self.assertIn("research_particle.residual_blend_oos", payload["residual_blend_oos_command"])
        self.assertIn("--evaluation-scope locked_oos_shadow", payload["residual_blend_oos_command"])
        self.assertIn("residual coefficient", md.lower())
        self.assertIn("json_plan=", stdout.getvalue())

    def test_dynamic_particle_locked_oos_plan_writes_predeclared_command_manifest(self) -> None:
        root = Path(tempfile.mkdtemp())

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = dynamic_particle_locked_oos_plan_main(
                [
                    "--hypothesis-id",
                    "rolling_vol_300s_v1",
                    "--run-id",
                    "UNITDYNLOCK",
                    "--dataset",
                    "particle_dynamic_oos_unit",
                    "--artifact-root",
                    str(root / "artifacts"),
                    "--output-dir",
                    str(root / "plans"),
                    "--stem",
                    "dynamic_locked_plan",
                    "--run-seconds",
                    "3900",
                    "--gate-min-candidates",
                    "1000",
                    "--gate-min-markets",
                    "5",
                    "--gate-min-selected",
                    "250",
                ]
            )

        payload = json.loads((root / "plans" / "dynamic_locked_plan.json").read_text(encoding="utf-8"))
        md = (root / "plans" / "dynamic_locked_plan.md").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "rolling_vol_300s_v1")
        self.assertEqual(payload["evaluation_scope"], "locked_oos_shadow")
        self.assertEqual(payload["gate_config"]["min_market_count"], 5)
        self.assertIn("--hypothesis-id rolling_vol_300s_v1", payload["dynamic_particle_oos_command"])
        self.assertIn("--evaluation-scope locked_oos_shadow", payload["dynamic_particle_oos_command"])
        self.assertIn("research_particle.dynamic_particle_oos", md)
        self.assertIn("json_plan=", stdout.getvalue())

    def test_oos_stability_report_summarizes_locked_report_roots(self) -> None:
        root = Path(tempfile.mkdtemp())
        run1 = root / "run1" / "reports"
        run2 = root / "run2" / "reports"
        for report_dir, pnl in ((run1, 10.0), (run2, 20.0)):
            report_dir.mkdir(parents=True)
            (report_dir / "probability_variants_locked_oos.json").write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "name": "unit_variant",
                                "candidate_count": 2,
                                "selected_count": 2,
                                "total_counterfactual_pnl_cents": pnl,
                                "avg_counterfactual_pnl_cents_per_candidate": pnl / 2,
                                "avg_counterfactual_pnl_cents_per_selected": pnl / 2,
                                "brier": 0.1,
                                "log_loss": 0.2,
                                "beats_brownian": True,
                                "beats_market": True,
                                "beats_current_calibrated": True,
                                "ev_rank_correlation_sign": 0.5,
                                "top_ev_bucket_pnl_cents": 1.0,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "ensemble_particle_locked_oos_diagnostic.json").write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "name": "ensemble_unit",
                                "candidate_count": 2,
                                "selected_count": 2,
                                "total_counterfactual_pnl_cents": pnl + 1,
                                "avg_counterfactual_pnl_cents_per_candidate": (pnl + 1) / 2,
                                "avg_counterfactual_pnl_cents_per_selected": (pnl + 1) / 2,
                                "brier": 0.09,
                                "log_loss": 0.19,
                                "beats_brownian": True,
                                "beats_market": True,
                                "beats_current_calibrated": True,
                                "ev_rank_correlation_sign": 0.6,
                                "top_ev_bucket_pnl_cents": 1.0,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "online_logit_particle_locked_oos_diagnostic.json").write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "name": "online_logit_unit",
                                "candidate_count": 2,
                                "selected_count": 2,
                                "total_counterfactual_pnl_cents": pnl + 2,
                                "avg_counterfactual_pnl_cents_per_candidate": (pnl + 2) / 2,
                                "avg_counterfactual_pnl_cents_per_selected": (pnl + 2) / 2,
                                "brier": 0.095,
                                "log_loss": 0.195,
                                "beats_brownian": True,
                                "beats_market": True,
                                "beats_current_calibrated": True,
                                "ev_rank_correlation_sign": 0.7,
                                "top_ev_bucket_pnl_cents": 1.0,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "materialized_late300_mc75_online_logit_rv600.json").write_text(
                json.dumps(
                    {
                        "candidate_count": 2,
                        "selected_count": 2,
                        "total_counterfactual_pnl_cents": pnl + 3,
                        "avg_counterfactual_pnl_cents_per_candidate": (pnl + 3) / 2,
                        "avg_counterfactual_pnl_cents_per_selected": (pnl + 3) / 2,
                        "particle": {"brier": 0.11, "log_loss": 0.21},
                        "particle_beats_brownian": True,
                        "particle_beats_market": True,
                        "particle_beats_current_calibrated": True,
                        "ev_rank_correlation_sign": 0.8,
                        "top_ev_bucket_pnl_cents": 1.0,
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "side_consensus_oos_locked.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "skip_against_market_current_consensus_10_v1",
                        "candidate_count": 2,
                        "consensus_selected_count": 2,
                        "consensus_total_counterfactual_pnl_cents": pnl + 4,
                        "consensus_avg_counterfactual_pnl_cents_per_selected": (pnl + 4) / 2,
                        "consensus_ev_rank_correlation_sign": 0.9,
                        "consensus_top_ev_bucket_pnl_cents": -1.0,
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "residual_blend_oos_locked.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "resid_current_rv300n20_rv600p20_particle_n10_v1",
                        "selected_variant": {
                            "candidate_count": 2,
                            "selected_count": 2,
                            "total_counterfactual_pnl_cents": pnl + 5,
                            "avg_counterfactual_pnl_cents_per_candidate": (pnl + 5) / 2,
                            "avg_counterfactual_pnl_cents_per_selected": (pnl + 5) / 2,
                            "brier": 0.12,
                            "log_loss": 0.22,
                            "beats_brownian": True,
                            "beats_market": True,
                            "beats_current_calibrated": True,
                            "ev_rank_correlation_sign": 0.95,
                            "top_ev_bucket_pnl_cents": -1.0,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "fixed_terminal_oos_locked.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "gaussian_vol45_terminal_v1",
                        "candidate_count": 2,
                        "selected_variant": {
                            "name": "gaussian_vol45",
                            "candidate_count": 2,
                            "selected_count": 2,
                            "total_counterfactual_pnl_cents": pnl + 6,
                            "avg_counterfactual_pnl_cents_per_selected": (pnl + 6) / 2,
                            "brier": 0.13,
                            "log_loss": 0.23,
                            "beats_brownian": False,
                            "beats_market": True,
                            "beats_current_calibrated": True,
                            "ev_rank_correlation_sign": 0.96,
                            "top_ev_bucket_pnl_cents": 1.0,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "spot_realized_vol_terminal_oos_locked.json").write_text(
                json.dumps(
                    {
                        "hypothesis_id": "rv233_blend50_fixed65_terminal_v1",
                        "candidate_count": 2,
                        "selected_variant": {
                            "name": "rv233_blend50_fixed65",
                            "candidate_count": 2,
                            "selected_count": 2,
                            "total_counterfactual_pnl_cents": pnl + 7,
                            "avg_counterfactual_pnl_cents_per_selected": (pnl + 7) / 2,
                            "brier": 0.125,
                            "log_loss": 0.225,
                            "beats_brownian": False,
                            "beats_market": True,
                            "beats_current_calibrated": True,
                            "ev_rank_correlation_sign": 0.97,
                            "top_ev_bucket_pnl_cents": 1.0,
                        },
                    }
                ),
                encoding="utf-8",
            )

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = oos_stability_report_main(
                [
                    "--report-root",
                    str(root / "run1"),
                    "--report-root",
                    str(root / "run2"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "stability",
                    "--min-runs-for-stability",
                    "2",
                ]
            )

        payload = json.loads((root / "reports" / "stability.json").read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertEqual(payload["run_count"], 2)
        self.assertEqual(payload["stable_candidate_count"], 4)
        self.assertEqual(payload["best_by_mean_brier"]["name"], "ensemble_unit")
        self.assertFalse(payload["promotion_safe"])
        self.assertIn("stable_candidate_count=4", stdout.getvalue())
        self.assertTrue(
            any(
                row["source"] == "materialized"
                and row["name"] == "late300_mc75_online_logit_rv600"
                for row in payload["stability_rows"]
            )
        )
        self.assertTrue(
            any(
                row["source"] == "side_consensus"
                and row["name"] == "skip_against_market_current_consensus_10_v1"
                and row["positive_top_bucket_run_count"] == 0
                for row in payload["stability_rows"]
            )
        )
        self.assertTrue(
            any(
                row["source"] == "residual_blend"
                and row["name"] == "resid_current_rv300n20_rv600p20_particle_n10_v1"
                and row["positive_top_bucket_run_count"] == 0
                for row in payload["stability_rows"]
            )
        )
        self.assertTrue(
            any(
                row["source"] == "fixed_terminal"
                and row["name"] == "gaussian_vol45_terminal_v1"
                and row["run_count"] == 2
                and row["beats_brownian_run_count"] == 0
                for row in payload["stability_rows"]
            )
        )
        self.assertTrue(
            any(
                row["source"] == "spot_realized_vol_terminal"
                and row["name"] == "rv233_blend50_fixed65_terminal_v1"
                and row["run_count"] == 2
                and row["beats_brownian_run_count"] == 0
                for row in payload["stability_rows"]
            )
        )
        self.assertIn("OOS Stability Report", (root / "reports" / "stability.md").read_text(encoding="utf-8"))

    def test_variant_loro_selection_diagnostic_uses_held_out_runs(self) -> None:
        root = Path(tempfile.mkdtemp())
        stability_path = root / "stability.json"
        stability_path.write_text(
            json.dumps(
                {
                    "variant_rows": [
                        {
                            "run_name": "run1",
                            "source": "probability",
                            "name": "unit_variant",
                            "candidate_count": 2,
                            "selected_count": 2,
                            "total_counterfactual_pnl_cents": 10.0,
                            "brier": 0.1,
                            "log_loss": 0.2,
                            "beats_brownian": True,
                            "beats_market": True,
                            "beats_current_calibrated": True,
                            "ev_rank_correlation_sign": 0.1,
                            "top_ev_bucket_pnl_cents": 1.0,
                        },
                        {
                            "run_name": "run2",
                            "source": "probability",
                            "name": "unit_variant",
                            "candidate_count": 2,
                            "selected_count": 2,
                            "total_counterfactual_pnl_cents": 12.0,
                            "brier": 0.1,
                            "log_loss": 0.2,
                            "beats_brownian": True,
                            "beats_market": True,
                            "beats_current_calibrated": False,
                            "ev_rank_correlation_sign": 0.1,
                            "top_ev_bucket_pnl_cents": 1.0,
                        },
                        {
                            "run_name": "run3",
                            "source": "probability",
                            "name": "unit_variant",
                            "candidate_count": 2,
                            "selected_count": 2,
                            "total_counterfactual_pnl_cents": -5.0,
                            "brier": 0.1,
                            "log_loss": 0.2,
                            "beats_brownian": True,
                            "beats_market": True,
                            "beats_current_calibrated": True,
                            "ev_rank_correlation_sign": 0.1,
                            "top_ev_bucket_pnl_cents": 1.0,
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )

        report = build_variant_loro_selection_diagnostic(stability_path)

        self.assertEqual(report.run_count, 3)
        self.assertFalse(report.promotion_safe)
        self.assertTrue(all(not row.strict_all_holdouts for row in report.selector_summary_rows))
        self.assertEqual({row.holdout_run for row in report.holdout_rows}, {"run1", "run2", "run3"})

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = variant_loro_selection_diagnostic_main(
                [
                    "--stability-report",
                    str(stability_path),
                    "--output-dir",
                    str(root / "loro_reports"),
                    "--stem",
                    "loro",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "loro_reports" / "loro.json").read_text(encoding="utf-8"))
        self.assertFalse(payload["promotion_safe"])
        self.assertIn("promotion_safe=False", stdout.getvalue())
        self.assertIn("Variant LORO Selection Diagnostic", (root / "loro_reports" / "loro.md").read_text(encoding="utf-8"))

    def test_strict_replay_refuses_snapshot_received_after_decision(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-LEAK",
            decision_ts_utc=decision,
            recv_ts_utc=decision + timedelta(milliseconds=1),
            strike=100.0,
            spot=100.0,
            yes_ask_cents=50.0,
            no_ask_cents=52.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-LEAK",
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.0,
            strike=100.0,
        )
        replay_input = ReplayInput(
            snapshot=snapshot,
            label=label,
            particle_p_yes=0.6,
            brownian_p_yes=0.5,
            market_p_yes=0.5,
            current_calibrated_p_yes=0.55,
        )

        with self.assertRaises(FutureDataLeakageError):
            evaluate_replay([replay_input])

    def test_selection_sweep_reports_threshold_sensitivity(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        rows = [
            ReplayInput(
                snapshot=CandidateSnapshot(
                    market_ticker="KXBTC15M-SWEEP1",
                    decision_ts_utc=decision,
                    recv_ts_utc=decision,
                    strike=100.0,
                    spot=101.0,
                    yes_ask_cents=40.0,
                    no_ask_cents=65.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                ),
                label=SettlementLabel(
                    market_ticker="KXBTC15M-SWEEP1",
                    settlement_ts_utc=decision + timedelta(minutes=15),
                    label_available_ts_utc=decision + timedelta(minutes=16),
                    settlement_price=101.0,
                    strike=100.0,
                ),
                particle_p_yes=0.75,
                brownian_p_yes=0.55,
                market_p_yes=0.50,
                current_calibrated_p_yes=0.60,
            ),
            ReplayInput(
                snapshot=CandidateSnapshot(
                    market_ticker="KXBTC15M-SWEEP2",
                    decision_ts_utc=decision + timedelta(seconds=1),
                    recv_ts_utc=decision + timedelta(seconds=1),
                    strike=100.0,
                    spot=99.0,
                    yes_ask_cents=60.0,
                    no_ask_cents=45.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                ),
                label=SettlementLabel(
                    market_ticker="KXBTC15M-SWEEP2",
                    settlement_ts_utc=decision + timedelta(minutes=15),
                    label_available_ts_utc=decision + timedelta(minutes=16),
                    settlement_price=99.0,
                    strike=100.0,
                ),
                particle_p_yes=0.55,
                brownian_p_yes=0.50,
                market_p_yes=0.50,
                current_calibrated_p_yes=0.52,
            ),
        ]

        report = evaluate_selection_sweep(
            rows,
            min_ev_grid=[0.0, 10.0, 40.0],
            min_fill_grid=[0.0],
            counterfactual_fill_threshold=0.5,
        )

        self.assertEqual(len(report.rows), 3)
        self.assertEqual(report.rows[0].selected_count, 1)
        self.assertEqual(report.rows[1].selected_count, 1)
        self.assertEqual(report.rows[2].selected_count, 0)
        self.assertEqual(report.positive_nonzero_rows, 2)
        self.assertIsNotNone(report.best_positive_row)
        self.assertGreater(report.best_positive_row.total_counterfactual_pnl_cents, 0.0)

    def test_selection_sweep_cli_writes_json_and_markdown(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-SWEEPCLI",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=101.0,
            yes_ask_cents=40.0,
            no_ask_cents=65.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-SWEEPCLI",
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.0,
            strike=100.0,
        )
        CandidateSnapshotRecorder(root).record(
            snapshot,
            decision_shadow="candidate",
            reason="selection_sweep_cli_test",
            extra={
                "particle_p_yes": 0.75,
                "brownian_p_yes": 0.55,
                "market_p_yes": 0.50,
                "current_calibrated_p_yes": 0.60,
            },
        )
        SettlementLabelRecorder(root).record(label, source="selection_sweep_cli_test")

        with contextlib.redirect_stdout(io.StringIO()):
            result = selection_sweep_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "sweep",
                    "--min-ev-grid",
                    "0,10,40",
                    "--min-fill-grid",
                    "0",
                ]
            )

        self.assertEqual(result, 0)
        payload = json.loads((root / "reports" / "sweep.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["positive_nonzero_rows"], 2)
        self.assertTrue((root / "reports" / "sweep.md").exists())

    def test_shadow_adapter_records_only_complete_strict_candidate_context(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        context = {
            "market_ticker": "KXBTC15M-SHADOW",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": decision.isoformat(),
            "strike": 100.0,
            "spot": 100.4,
            "yes_ask_cents": 58.0,
            "no_ask_cents": 44.0,
            "fee_cents": 1.0,
            "fill_prob": 0.8,
            "particle_p_yes": 0.7,
            "brownian_p_yes": 0.6,
            "market_p_yes": 0.57,
            "current_calibrated_p_yes": 0.62,
        }

        snapshot = ShadowCandidateAdapter(root).record_context(
            context,
            decision_shadow="candidate",
            reason="unit_test_all_candidate",
        )

        self.assertEqual(snapshot.market_ticker, "KXBTC15M-SHADOW")
        path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        payload = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(payload["extra"]["particle_p_yes"], 0.7)
        self.assertEqual(payload["decision_shadow"], "candidate")

    def test_shadow_adapter_refuses_missing_or_late_context(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        incomplete = {
            "market_ticker": "KXBTC15M-MISSING",
            "decision_ts_utc": decision.isoformat(),
        }
        with self.assertRaises(MissingShadowFieldError):
            snapshot_from_shadow_context(incomplete)

        late = {
            "market_ticker": "KXBTC15M-LATE",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": (decision + timedelta(milliseconds=1)).isoformat(),
            "strike": 100.0,
            "spot": 100.4,
            "yes_ask_cents": 58.0,
            "no_ask_cents": 44.0,
            "fee_cents": 1.0,
            "fill_prob": 0.8,
        }
        with self.assertRaises(ValueError):
            snapshot_from_shadow_context(late)

    def test_particle_engine_generates_deterministic_shadow_prediction(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-ENGINE",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=100.2,
            yes_ask_cents=55.0,
            no_ask_cents=47.0,
            fee_cents=1.0,
            fill_prob=0.75,
        )
        engine = NextSecondParticleEngine(
            ParticleEngineConfig(annualized_vol=0.5, sample_count=600, seed=42)
        )

        first = engine.predict(snapshot, settlement_ts_utc=decision + timedelta(minutes=15))
        second = engine.predict(snapshot, settlement_ts_utc=decision + timedelta(minutes=15))

        self.assertAlmostEqual(first.particle_p_yes, second.particle_p_yes)
        self.assertAlmostEqual(first.brownian_p_yes, second.brownian_p_yes)
        self.assertTrue(0.0 <= first.particle_p_yes <= 1.0)
        self.assertIn("particle_p_yes", first.as_shadow_extra())
        self.assertIn("particle_calibrated_p_yes", first.as_shadow_extra())
        self.assertIn("ev_yes_cents", first.as_shadow_extra())

    def test_shadow_collect_cli_records_candidates_and_labels_with_engine_predictions(self) -> None:
        root = Path(tempfile.mkdtemp())
        input_dir = root / "input"
        artifact_root = root / "artifacts"
        input_dir.mkdir()
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_path = input_dir / "candidate_contexts.ndjson"
        label_path = input_dir / "label_contexts.ndjson"
        candidate_path.write_text(
            json.dumps(
                {
                    "market_ticker": "KXBTC15M-COLLECT",
                    "decision_ts_utc": decision.isoformat(),
                    "recv_ts_utc": decision.isoformat(),
                    "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                    "strike": 100.0,
                    "spot": 100.4,
                    "yes_ask_cents": 58.0,
                    "no_ask_cents": 44.0,
                    "fee_cents": 1.0,
                    "fill_prob": 0.8,
                    "current_calibrated_p_yes": 0.62,
                    "book_age_ms": 12.0,
                    "btc_age_ms": 34.0,
                    "depth_count": 50.0,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        label_path.write_text(
            json.dumps(
                {
                    "market_ticker": "KXBTC15M-COLLECT",
                    "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                    "label_available_ts_utc": (decision + timedelta(minutes=16)).isoformat(),
                    "settlement_price": 101.0,
                    "strike": 100.0,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                shadow_collect_main(
                    [
                        "candidates",
                        "--input",
                        str(candidate_path),
                        "--root",
                        str(artifact_root),
                        "--annualized-vol",
                        "0.5",
                        "--sample-count",
                        "500",
                        "--seed",
                        "7",
                    ]
                ),
                0,
            )
            self.assertEqual(
                shadow_collect_main(
                    [
                        "labels",
                        "--input",
                        str(label_path),
                        "--root",
                        str(artifact_root),
                        "--source",
                        "unit_test",
                    ]
                ),
                0,
            )

        recorded_candidate = json.loads(
            (artifact_root / "candidate_snapshots" / "candidate_snapshots.ndjson")
            .read_text(encoding="utf-8")
            .splitlines()[0]
        )
        recorded_label = json.loads(
            (artifact_root / "settlement_labels" / "settlement_labels.ndjson")
            .read_text(encoding="utf-8")
            .splitlines()[0]
        )
        self.assertIn("particle_p_yes", recorded_candidate["extra"])
        self.assertIn("brownian_p_yes", recorded_candidate["extra"])
        self.assertIn("current_calibrated_p_yes", recorded_candidate["extra"])
        self.assertIn("particle_calibrated_p_yes", recorded_candidate["extra"])
        self.assertEqual(recorded_candidate["extra"]["current_calibrated_p_yes"], 0.62)
        self.assertEqual(recorded_candidate["extra"]["current_calibrated_p_yes_source"], "input_baseline")
        self.assertEqual(recorded_candidate["extra"]["book_age_ms"], 12.0)
        self.assertEqual(recorded_candidate["extra"]["btc_age_ms"], 34.0)
        self.assertEqual(recorded_candidate["extra"]["depth_count"], 50.0)
        self.assertEqual(recorded_label["source"], "unit_test")

    def test_v28_event_adapter_extracts_complete_candidate_context(self) -> None:
        event = {
            "event_type": "mushroom_v28_rejected",
            "market": "KXBTC15M-ADAPT",
            "ts_wall": "2026-05-10T12:00:00+00:00",
            "mushroom_v28_side": "yes",
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 100.4,
            "mushroom_v28_ask_cents": 58,
            "mushroom_v28_fee_cents": 1.0,
            "mushroom_v28_p_yes": 0.7,
            "mushroom_v28_seconds_to_close": 600,
            "yes_ask_cents": 58,
            "no_ask_cents": 44,
            "eligible_depth": "8",
            "depth_required": "2",
            "decision_reason": "unit_test",
        }

        adapted = adapt_v28_event(event)

        self.assertIsInstance(adapted, AdaptedEvent)
        assert isinstance(adapted, AdaptedEvent)
        self.assertEqual(adapted.context["market_ticker"], "KXBTC15M-ADAPT")
        self.assertEqual(adapted.context["yes_ask_cents"], 58.0)
        self.assertEqual(adapted.context["no_ask_cents"], 44.0)
        self.assertEqual(adapted.context["fill_prob"], 1.0)
        self.assertEqual(adapted.context["current_calibrated_p_yes"], 0.7)

    def test_v28_event_adapter_refuses_to_invent_missing_opposite_ask(self) -> None:
        event = {
            "event_type": "mushroom_v28_rejected",
            "market": "KXBTC15M-ADAPT",
            "ts_wall": "2026-05-10T12:00:00+00:00",
            "mushroom_v28_side": "yes",
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 100.4,
            "mushroom_v28_ask_cents": 58,
            "mushroom_v28_fee_cents": 1.0,
            "mushroom_v28_p_yes": 0.7,
            "mushroom_v28_seconds_to_close": 600,
        }

        adapted = adapt_v28_event(event)

        self.assertIsInstance(adapted, AdapterIssue)
        assert isinstance(adapted, AdapterIssue)
        self.assertEqual(adapted.reason, "missing_exact_two_sided_asks")

    def test_v28_event_context_probe_writes_context_and_issue_reports(self) -> None:
        root = Path(tempfile.mkdtemp())
        input_path = root / "execution_events.ndjson"
        output_path = root / "contexts.ndjson"
        issue_path = root / "issues.ndjson"
        complete = {
            "event_type": "mushroom_v28_rejected",
            "market": "KXBTC15M-ADAPT1",
            "ts_wall": "2026-05-10T12:00:00+00:00",
            "mushroom_v28_side": "no",
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 99.4,
            "mushroom_v28_ask_cents": 43,
            "mushroom_v28_fee_cents": 1.0,
            "mushroom_v28_p_yes": 0.3,
            "mushroom_v28_seconds_to_close": 300,
            "yes_ask_cents": 59,
            "no_ask_cents": 43,
        }
        incomplete = dict(complete)
        incomplete["market"] = "KXBTC15M-ADAPT2"
        incomplete.pop("yes_ask_cents")
        input_path.write_text(
            json.dumps(complete) + "\n" + json.dumps(incomplete) + "\n",
            encoding="utf-8",
        )

        adapted_count, issue_count = adapt_v28_events_file(input_path, output_path, issue_path)

        self.assertEqual(adapted_count, 1)
        self.assertEqual(issue_count, 1)
        self.assertEqual(
            json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])["market_ticker"],
            "KXBTC15M-ADAPT1",
        )
        self.assertEqual(
            json.loads(issue_path.read_text(encoding="utf-8").splitlines()[0])["reason"],
            "missing_exact_two_sided_asks",
        )

    def test_v28_event_context_probe_cli_runs_on_fixture(self) -> None:
        root = Path(tempfile.mkdtemp())
        input_path = root / "execution_events.ndjson"
        input_path.write_text(
            json.dumps(
                {
                    "event_type": "mushroom_v28_rejected",
                    "market": "KXBTC15M-ADAPTCLI",
                    "ts_wall": "2026-05-10T12:00:00+00:00",
                    "mushroom_v28_side": "yes",
                    "mushroom_v28_strike": 100.0,
                    "mushroom_v28_btc_price": 100.4,
                    "mushroom_v28_ask_cents": 58,
                    "mushroom_v28_fee_cents": 1.0,
                    "mushroom_v28_p_yes": 0.7,
                    "mushroom_v28_seconds_to_close": 600,
                    "yes_ask_cents": 58,
                    "no_ask_cents": 44,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            result = v28_event_context_main(
                [
                    "--input",
                    str(input_path),
                    "--stem",
                    "unit_test_v28_event_contexts",
                ]
            )

        self.assertEqual(result, 0)

    def test_market_result_label_builder_joins_candidate_strike_to_binary_result(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-LABEL",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=101.0,
            yes_ask_cents=60.0,
            no_ask_cents=42.0,
            fee_cents=1.0,
            fill_prob=0.7,
        )
        CandidateSnapshotRecorder(root).record(
            snapshot,
            decision_shadow="candidate",
            reason="label_builder_test",
            extra={
                "particle_p_yes": 0.7,
                "brownian_p_yes": 0.6,
                "market_p_yes": 0.58,
                "current_calibrated_p_yes": 0.65,
            },
        )
        market_results = root / "market_results.json"
        market_results.write_text(
            json.dumps(
                [
                    {
                        "market": "KXBTC15M-LABEL",
                        "result": "yes",
                        "status": "finalized",
                        "settlement_ts": "2026-05-10T12:15:12Z",
                        "close_time": "2026-05-10T12:15:00Z",
                        "source": "unit_test",
                    }
                ]
            ),
            encoding="utf-8",
        )
        output = root / "label_contexts.ndjson"

        written, skipped = build_label_contexts_from_market_results(
            root / "candidate_snapshots" / "candidate_snapshots.ndjson",
            market_results,
            output,
        )

        self.assertEqual(written, 1)
        self.assertEqual(skipped, 0)
        label = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(label["market_ticker"], "KXBTC15M-LABEL")
        self.assertEqual(label["settlement_price"], 101.0)
        self.assertTrue(label["settlement_price_is_binary_proxy"])

    def test_market_result_label_builder_cli_runs_on_fixture(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-LABELCLI",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=99.0,
            yes_ask_cents=40.0,
            no_ask_cents=62.0,
            fee_cents=1.0,
            fill_prob=0.7,
        )
        CandidateSnapshotRecorder(root).record(
            snapshot,
            decision_shadow="candidate",
            reason="label_builder_test",
            extra={
                "particle_p_yes": 0.3,
                "brownian_p_yes": 0.4,
                "market_p_yes": 0.42,
                "current_calibrated_p_yes": 0.35,
            },
        )
        market_results = root / "market_results.csv"
        market_results.write_text(
            "market,result,status,settlement_ts,close_time,source\n"
            "KXBTC15M-LABELCLI,no,finalized,2026-05-10T12:15:08Z,2026-05-10T12:15:00Z,unit_test\n",
            encoding="utf-8",
        )
        output = root / "label_contexts.ndjson"

        with contextlib.redirect_stdout(io.StringIO()):
            result = market_result_labels_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--market-results",
                    str(market_results),
                    "--output",
                    str(output),
                ]
            )

        self.assertEqual(result, 0)
        label = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(label["settlement_price"], 99.0)

    def test_kalshi_market_result_row_requires_resolved_yes_or_no(self) -> None:
        resolved = market_result_row_from_market(
            {
                "ticker": "KXBTC15M-RESULT",
                "result": "yes",
                "close_time": "2026-05-10T12:15:00Z",
                "status": "settled",
                "_result_source": "kalshi_public_market",
            }
        )
        unresolved = market_result_row_from_market(
            {
                "ticker": "KXBTC15M-RESULT",
                "result": "",
                "close_time": "2026-05-10T12:15:00Z",
                "status": "active",
            }
        )

        self.assertEqual(resolved["market"], "KXBTC15M-RESULT")
        self.assertEqual(resolved["result"], "yes")
        self.assertEqual(resolved["source"], "kalshi_public_market")
        self.assertIsNone(unresolved)

    def test_kalshi_market_payload_accepts_single_market_response(self) -> None:
        market = _market_from_payload(
            {
                "market": {
                    "ticker": "KXBTC15M-SINGLE",
                    "result": "no",
                    "close_time": "2026-05-10T12:15:00Z",
                }
            },
            "KXBTC15M-SINGLE",
        )

        self.assertEqual(market["ticker"], "KXBTC15M-SINGLE")

    def test_kalshi_market_fetch_prefers_resolved_fallback(self) -> None:
        calls: list[str] = []
        original_get_json = kalshi_market_results._get_json

        def fake_get_json(url: str) -> dict[str, object]:
            calls.append(url)
            if url.endswith("/markets?tickers=KXBTC15M-FALLBACK&limit=10"):
                return {
                    "markets": [
                        {
                            "ticker": "KXBTC15M-FALLBACK",
                            "result": "",
                            "close_time": "2026-05-10T12:15:00Z",
                        }
                    ]
                }
            return {
                "market": {
                    "ticker": "KXBTC15M-FALLBACK",
                    "result": "no",
                    "close_time": "2026-05-10T12:15:00Z",
                }
            }

        try:
            kalshi_market_results._get_json = fake_get_json
            market = kalshi_market_results.fetch_market_payload(
                "KXBTC15M-FALLBACK",
                base_url="https://example.test/trade-api/v2",
            )
        finally:
            kalshi_market_results._get_json = original_get_json

        self.assertEqual(market["result"], "no")
        self.assertEqual(market["_result_source"], "kalshi_public_market")
        self.assertEqual(len(calls), 2)

    def test_candidate_context_builder_requires_exact_two_sided_quotes(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        raw = {
            "market_ticker": "KXBTC15M-CTX",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": decision.isoformat(),
            "seconds_to_close": 600,
            "strike": 100.0,
            "spot": 100.2,
            "yes_ask_cents": 58,
            "no_ask_cents": 44,
            "fee_cents": 1.0,
            "fill_prob": 0.75,
            "current_calibrated_p_yes": 0.62,
        }

        context = build_candidate_context(raw)

        self.assertEqual(context["market_ticker"], "KXBTC15M-CTX")
        self.assertEqual(context["yes_ask_cents"], 58.0)
        self.assertEqual(context["no_ask_cents"], 44.0)
        self.assertEqual(context["current_calibrated_p_yes"], 0.62)

        missing = dict(raw)
        missing.pop("no_ask_cents")
        with self.assertRaises(CandidateContextError):
            build_candidate_context(missing)

    def test_candidate_context_preserves_side_specific_fill_probabilities(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        raw = {
            "market_ticker": "KXBTC15M-SIDEFILL",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": decision.isoformat(),
            "seconds_to_close": 600,
            "strike": 100.0,
            "spot": 99.8,
            "yes_ask_cents": 58,
            "no_ask_cents": 44,
            "fee_cents": 1.0,
            "fill_prob": 0.2,
            "yes_fill_prob": 0.2,
            "no_fill_prob": 0.9,
            "current_calibrated_p_yes": 0.35,
        }

        context = build_candidate_context(raw)
        snapshot = snapshot_from_shadow_context(context)

        self.assertEqual(context["yes_fill_prob"], 0.2)
        self.assertEqual(context["no_fill_prob"], 0.9)
        self.assertEqual(snapshot.yes_fill_prob, 0.2)
        self.assertEqual(snapshot.no_fill_prob, 0.9)

    def test_side_specific_fill_probability_controls_replay_selection(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-SIDEFILLREPLAY",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=99.5,
            yes_ask_cents=40.0,
            no_ask_cents=40.0,
            fee_cents=1.0,
            fill_prob=0.1,
            yes_fill_prob=0.1,
            no_fill_prob=0.8,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-SIDEFILLREPLAY",
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=99.0,
            strike=100.0,
        )

        report = evaluate_replay(
            [
                ReplayInput(
                    snapshot=snapshot,
                    label=label,
                    particle_p_yes=0.1,
                    brownian_p_yes=0.2,
                    market_p_yes=0.5,
                    current_calibrated_p_yes=0.15,
                )
            ],
            ReplayConfig(
                min_ev_cents=1.0,
                min_fill_prob=0.5,
                counterfactual_fill_policy="threshold",
                counterfactual_fill_threshold=0.5,
            ),
        )

        self.assertEqual(report.selected_count, 1)
        self.assertEqual(report.decisions[0].side, "no")
        self.assertTrue(report.decisions[0].filled_counterfactual)
        self.assertAlmostEqual(report.total_counterfactual_pnl_cents, 59.0)

    def test_read_only_candidate_source_builds_exact_implied_asks(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        row = build_raw_candidate_observation(
            TopOfBookObservation(
                market_ticker="KXBTC15M-SOURCE",
                decision_ts_utc=decision,
                recv_ts_utc=decision,
                settlement_ts_utc=decision + timedelta(minutes=15),
                strike=100.0,
                spot=100.4,
                yes_bid_cents=40,
                no_bid_cents=35,
                yes_bid_depth=2,
                no_bid_depth=1,
                current_calibrated_p_yes=0.62,
                position_size=2,
                book_age_ms=12.0,
                btc_age_ms=20.0,
                seconds_to_close=900,
            )
        )

        self.assertEqual(row["yes_ask_cents"], 65.0)
        self.assertEqual(row["no_ask_cents"], 60.0)
        self.assertEqual(row["yes_fill_prob"], 0.5)
        self.assertEqual(row["no_fill_prob"], 1.0)
        self.assertEqual(row["fill_prob"], 0.5)
        self.assertEqual(row["fee_cents"], 2.0)
        self.assertEqual(build_candidate_context(row)["market_ticker"], "KXBTC15M-SOURCE")

    def test_read_only_candidate_source_cli_writes_observations_and_issues(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        good = {
            "market_ticker": "KXBTC15M-SOURCEGOOD",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": decision.isoformat(),
            "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
            "strike": 100.0,
            "spot": 100.4,
            "yes_bid_cents": 40,
            "no_bid_cents": 35,
            "yes_bid_depth": 2,
            "no_bid_depth": 1,
            "current_calibrated_p_yes": 0.62,
            "position_size": 2,
        }
        bad = dict(good)
        bad["market_ticker"] = "KXBTC15M-SOURCEBAD"
        bad.pop("no_bid_cents")
        input_path = root / "top_book.ndjson"
        output_path = root / "raw_candidates.ndjson"
        issue_path = root / "source_issues.ndjson"
        input_path.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n", encoding="utf-8")

        written, issues = convert_observations(input_path, output_path, issue_path)

        self.assertEqual(written, 1)
        self.assertEqual(issues, 1)
        self.assertIn("yes_ask_cents", output_path.read_text(encoding="utf-8"))
        self.assertIn("missing required observation fields", issue_path.read_text(encoding="utf-8"))

        with contextlib.redirect_stdout(io.StringIO()):
            result = read_only_candidate_source_main(
                [
                    "--input",
                    str(input_path),
                    "--output",
                    str(root / "source_cli.ndjson"),
                    "--issues",
                    str(root / "source_cli_issues.ndjson"),
                ]
            )
        self.assertEqual(result, 0)

    def test_passive_checkpoint_source_builds_strict_candidate_row(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        checkpoint = {
            "checkpoint_ts": decision.isoformat(),
            "market_ticker": "KXBTC15M-PASSIVE",
            "yes_bid_prices": [40, 39],
            "yes_bid_sizes": [2, 5],
            "no_bid_prices": [35, 34],
            "no_bid_sizes": [1, 3],
        }
        context = PassiveCheckpointContext(
            market_ticker="KXBTC15M-PASSIVE",
            context_ts_utc=decision - timedelta(milliseconds=10),
            strike=100.0,
            settlement_ts_utc=decision + timedelta(minutes=15),
            spot=100.4,
            current_calibrated_p_yes=0.62,
            position_size=2,
            spot_ts_utc=decision - timedelta(milliseconds=250),
        )

        row = build_observation_from_passive_checkpoint(checkpoint, context)

        self.assertEqual(row["yes_ask_cents"], 65.0)
        self.assertEqual(row["no_ask_cents"], 60.0)
        self.assertEqual(row["yes_fill_prob"], 0.5)
        self.assertEqual(row["no_fill_prob"], 1.0)
        self.assertEqual(row["btc_age_ms"], 250.0)
        self.assertEqual(row["seconds_to_close"], 900.0)
        self.assertEqual(build_candidate_context(row)["market_ticker"], "KXBTC15M-PASSIVE")

    def test_passive_checkpoint_source_cli_writes_rows_and_issues(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        good_checkpoint = {
            "checkpoint_ts": decision.isoformat(),
            "market_ticker": "KXBTC15M-PASSIVEGOOD",
            "yes_bid_prices": [40],
            "yes_bid_sizes": [2],
            "no_bid_prices": [35],
            "no_bid_sizes": [1],
        }
        bad_checkpoint = dict(good_checkpoint)
        bad_checkpoint["market_ticker"] = "KXBTC15M-PASSIVEBAD"
        context = {
            "market_ticker": "KXBTC15M-PASSIVEGOOD",
            "context_ts_utc": (decision - timedelta(milliseconds=10)).isoformat(),
            "strike": 100.0,
            "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
            "spot": 100.4,
            "current_calibrated_p_yes": 0.62,
            "position_size": 2,
        }
        checkpoint_path = root / "checkpoints.ndjson"
        context_path = root / "contexts.ndjson"
        output_path = root / "raw_candidates.ndjson"
        issue_path = root / "issues.ndjson"
        checkpoint_path.write_text(
            json.dumps(good_checkpoint) + "\n" + json.dumps(bad_checkpoint) + "\n",
            encoding="utf-8",
        )
        context_path.write_text(json.dumps(context) + "\n", encoding="utf-8")

        written, issues = convert_passive_checkpoints(
            checkpoint_path,
            context_path,
            output_path,
            issue_path,
        )

        self.assertEqual(written, 1)
        self.assertEqual(issues, 1)
        self.assertIn("KXBTC15M-PASSIVEGOOD", output_path.read_text(encoding="utf-8"))
        self.assertIn("missing context for market_ticker", issue_path.read_text(encoding="utf-8"))

        with contextlib.redirect_stdout(io.StringIO()):
            result = passive_checkpoint_source_main(
                [
                    "--checkpoints",
                    str(checkpoint_path),
                    "--contexts",
                    str(context_path),
                    "--output",
                    str(root / "cli_raw_candidates.ndjson"),
                    "--issues",
                    str(root / "cli_issues.ndjson"),
                ]
            )
        self.assertEqual(result, 0)

    def test_passive_checkpoint_source_uses_latest_timestamp_available_context(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        checkpoint_path = root / "checkpoints.ndjson"
        context_path = root / "contexts.ndjson"
        output_path = root / "raw_candidates.ndjson"
        issue_path = root / "issues.ndjson"
        checkpoint = {
            "checkpoint_ts": decision.isoformat(),
            "market_ticker": "KXBTC15M-TIMECTX",
            "yes_bid_prices": [40],
            "yes_bid_sizes": [2],
            "no_bid_prices": [35],
            "no_bid_sizes": [1],
        }
        early_context = {
            "market_ticker": "KXBTC15M-TIMECTX",
            "context_ts_utc": (decision - timedelta(seconds=1)).isoformat(),
            "strike": 100.0,
            "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
            "spot": 99.1,
            "current_calibrated_p_yes": 0.40,
            "position_size": 2,
        }
        future_context = dict(early_context)
        future_context["context_ts_utc"] = (decision + timedelta(milliseconds=1)).isoformat()
        future_context["spot"] = 101.9
        future_context["current_calibrated_p_yes"] = 0.90
        checkpoint_path.write_text(json.dumps(checkpoint) + "\n", encoding="utf-8")
        context_path.write_text(
            json.dumps(early_context) + "\n" + json.dumps(future_context) + "\n",
            encoding="utf-8",
        )

        written, issues = convert_passive_checkpoints(
            checkpoint_path,
            context_path,
            output_path,
            issue_path,
        )

        self.assertEqual(written, 1)
        self.assertEqual(issues, 0)
        row = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(row["spot"], 99.1)
        self.assertEqual(row["current_calibrated_p_yes"], 0.40)

    def test_passive_checkpoint_source_accepts_glob_paths(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        checkpoint_dir = root / "book_checkpoints" / "day=2026-05-10"
        checkpoint_dir.mkdir(parents=True)
        checkpoint_path = checkpoint_dir / "part.ndjson"
        context_path = root / "contexts.ndjson"
        output_path = root / "raw_candidates.ndjson"
        issue_path = root / "issues.ndjson"
        checkpoint_path.write_text(
            json.dumps(
                {
                    "checkpoint_ts": decision.isoformat(),
                    "market_ticker": "KXBTC15M-GLOB",
                    "yes_bid_prices": [40],
                    "yes_bid_sizes": [2],
                    "no_bid_prices": [35],
                    "no_bid_sizes": [1],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        context_path.write_text(
            json.dumps(
                {
                    "market_ticker": "KXBTC15M-GLOB",
                    "context_ts_utc": (decision - timedelta(seconds=1)).isoformat(),
                    "strike": 100.0,
                    "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                    "spot": 100.4,
                    "current_calibrated_p_yes": 0.62,
                    "position_size": 2,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        written, issues = convert_passive_checkpoints(
            Path(str(root / "book_checkpoints" / "**" / "*.ndjson")),
            context_path,
            output_path,
            issue_path,
        )

        self.assertEqual(written, 1)
        self.assertEqual(issues, 0)
        self.assertIn("KXBTC15M-GLOB", output_path.read_text(encoding="utf-8"))

    def test_spot_ticker_recorder_parses_binance_trade_message(self) -> None:
        local_recv = datetime(2026, 5, 10, 12, 0, 1, tzinfo=timezone.utc)

        tick = parse_binance_trade_message(
            {
                "e": "trade",
                "s": "BTCUSDT",
                "p": "62400.25",
                "T": 1770000000123,
                "t": 987654,
            },
            local_recv_ts_utc=local_recv,
            source="unit_test_spot",
        )

        self.assertEqual(tick.schema_version, "spot-tick-v1")
        self.assertEqual(tick.source, "unit_test_spot")
        self.assertEqual(tick.symbol, "BTCUSDT")
        self.assertEqual(tick.price, 62400.25)
        self.assertEqual(tick.trade_id, "987654")
        self.assertEqual(tick.raw_event_type, "trade")
        self.assertEqual(tick.local_recv_ts_utc, local_recv.isoformat())
        self.assertEqual(
            tick.exchange_ts_utc,
            datetime.fromtimestamp(1770000000123 / 1000.0, tz=timezone.utc).isoformat(),
        )

        with self.assertRaises(ValueError):
            parse_binance_trade_message(
                {"e": "depthUpdate", "s": "BTCUSDT", "p": "62400.25", "T": 1770000000123},
                local_recv_ts_utc=local_recv,
            )

    def test_spot_ticker_recorder_parses_coinbase_match_message(self) -> None:
        local_recv = datetime(2026, 5, 10, 12, 0, 1, tzinfo=timezone.utc)

        tick = parse_coinbase_match_message(
            {
                "type": "match",
                "product_id": "BTC-USD",
                "price": "81159.99",
                "time": "2026-05-11T12:05:07.979815Z",
                "trade_id": 1016360787,
            },
            local_recv_ts_utc=local_recv,
            source="coinbase_unit",
        )

        self.assertEqual(tick.schema_version, "spot-tick-v1")
        self.assertEqual(tick.source, "coinbase_unit")
        self.assertEqual(tick.symbol, "BTC-USD")
        self.assertEqual(tick.price, 81159.99)
        self.assertEqual(tick.trade_id, "1016360787")
        self.assertEqual(tick.raw_event_type, "match")
        self.assertEqual(tick.exchange_ts_utc, "2026-05-11T12:05:07.979815+00:00")

        with self.assertRaises(ValueError):
            parse_coinbase_match_message(
                {"type": "subscriptions"},
                local_recv_ts_utc=local_recv,
            )

    def test_rv600_offline_v28_context_replay_uses_only_non_future_spot(self) -> None:
        class FakeReplayer:
            warmup_rows = 180
            warmup_end_utc = datetime(2026, 5, 13, 11, 59, tzinfo=timezone.utc)

            def __init__(self, ticks: list[SpotTickRow]) -> None:
                self.ticks = ticks
                self.index = 0
                self.last_tick: SpotTickRow | None = None

            def update_through(self, decision_ts: datetime) -> SpotTickRow | None:
                while self.index < len(self.ticks) and self.ticks[self.index].available_ts_utc <= decision_ts:
                    self.last_tick = self.ticks[self.index]
                    self.index += 1
                return self.last_tick

            def predict_p_yes(self, *, strike: float, horizon_seconds: float) -> float:
                if strike <= 0.0 or horizon_seconds <= 0.0:
                    raise AssertionError("fake replay received invalid prediction inputs")
                return 0.61

        decision_ts = datetime(2026, 5, 13, 12, 0, 3, tzinfo=timezone.utc)
        ticks = [
            SpotTickRow(
                available_ts_utc=decision_ts - timedelta(seconds=2),
                exchange_ts_utc=decision_ts - timedelta(seconds=2),
                price=100.0,
                source="unit_before",
            ),
            SpotTickRow(
                available_ts_utc=decision_ts + timedelta(seconds=1),
                exchange_ts_utc=decision_ts + timedelta(seconds=1),
                price=999.0,
                source="unit_future_must_not_leak",
            ),
        ]
        meta = MarketMeta(
            market_ticker="KXBTC15M-OFFLINEV28",
            strike=101.0,
            settlement_ts_utc=decision_ts + timedelta(minutes=5),
            source="unit_market",
        )

        contexts, issues = build_offline_context_rows(
            checkpoints=[
                {
                    "checkpoint_ts": decision_ts.isoformat(),
                    "market_ticker": "KXBTC15M-OFFLINEV28",
                    "yes_bid_prices": [42],
                    "yes_bid_sizes": [1],
                    "no_bid_prices": [57],
                    "no_bid_sizes": [1],
                }
            ],
            market_meta={"KXBTC15M-OFFLINEV28": meta},
            replayer=FakeReplayer(ticks),
            max_spot_age_ms=5_000,
        )

        self.assertEqual(issues, [])
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0]["spot"], 100.0)
        self.assertEqual(contexts[0]["spot_ts_utc"], (decision_ts - timedelta(seconds=2)).isoformat())
        self.assertEqual(contexts[0]["current_calibrated_p_yes"], 0.61)
        self.assertTrue(contexts[0]["causal_replay"])

    def test_spot_context_merge_uses_latest_non_future_tick(self) -> None:
        root = Path(tempfile.mkdtemp())
        context_ts = datetime(2026, 5, 10, 12, 0, 10, tzinfo=timezone.utc)
        context_path = root / "contexts.ndjson"
        spot_path = root / "spot_ticks.ndjson"
        output_path = root / "merged_contexts.ndjson"
        issue_path = root / "merge_issues.ndjson"
        context_path.write_text(
            json.dumps(
                {
                    "market_ticker": "KXBTC15M-SPOTMERGE",
                    "context_ts_utc": context_ts.isoformat(),
                    "spot": 90.0,
                    "spot_ts_utc": (context_ts - timedelta(seconds=30)).isoformat(),
                    "current_calibrated_p_yes": 0.55,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        spot_path.write_text(
            "\n".join(
                json.dumps(row)
                for row in (
                    {
                        "exchange_ts_utc": (context_ts - timedelta(seconds=5)).isoformat(),
                        "local_recv_ts_utc": (context_ts - timedelta(seconds=5)).isoformat(),
                        "price": 100.0,
                        "source": "unit_spot",
                    },
                    {
                        "exchange_ts_utc": (context_ts - timedelta(seconds=1)).isoformat(),
                        "local_recv_ts_utc": (context_ts + timedelta(seconds=1)).isoformat(),
                        "price": 200.0,
                        "source": "delayed_spot_must_not_leak",
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )

        result = merge_contexts_with_spot(
            context_path=context_path,
            spot_path=spot_path,
            output_path=output_path,
            issue_path=issue_path,
            max_age_ms=10_000,
        )

        self.assertEqual(result.contexts_read, 1)
        self.assertEqual(result.contexts_written, 1)
        self.assertEqual(result.contexts_with_independent_spot, 1)
        self.assertEqual(result.issue_count, 0)
        row = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(row["spot"], 100.0)
        self.assertEqual(row["original_spot"], 90.0)
        self.assertEqual(row["independent_spot_source"], "unit_spot")
        self.assertEqual(
            row["independent_spot_available_ts_utc"],
            (context_ts - timedelta(seconds=5)).isoformat(),
        )
        self.assertEqual(
            row["independent_spot_exchange_ts_utc"],
            (context_ts - timedelta(seconds=5)).isoformat(),
        )
        self.assertEqual(row["independent_spot_age_ms"], 5000.0)
        self.assertEqual(row["source"], "merged_independent_spot_context")

    def test_spot_context_merge_keeps_context_and_reports_stale_tick(self) -> None:
        root = Path(tempfile.mkdtemp())
        context_ts = datetime(2026, 5, 10, 12, 0, 10, tzinfo=timezone.utc)
        context_path = root / "contexts.ndjson"
        spot_path = root / "spot_ticks.ndjson"
        output_path = root / "merged_contexts.ndjson"
        issue_path = root / "merge_issues.ndjson"
        context_path.write_text(
            json.dumps(
                {
                    "market_ticker": "KXBTC15M-STALESPOT",
                    "context_ts_utc": context_ts.isoformat(),
                    "spot": 91.0,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        spot_path.write_text(
            json.dumps(
                {
                    "exchange_ts_utc": (context_ts - timedelta(seconds=20)).isoformat(),
                    "price": 100.0,
                    "source": "unit_spot",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        result = merge_contexts_with_spot(
            context_path=context_path,
            spot_path=spot_path,
            output_path=output_path,
            issue_path=issue_path,
            max_age_ms=1_000,
            require_spot=False,
        )

        self.assertEqual(result.contexts_read, 1)
        self.assertEqual(result.contexts_written, 1)
        self.assertEqual(result.contexts_with_independent_spot, 0)
        self.assertEqual(result.issue_count, 1)
        row = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(row["spot"], 91.0)
        self.assertNotIn("independent_spot_age_ms", row)
        self.assertIn("too old", issue_path.read_text(encoding="utf-8"))

    def test_spot_context_merge_cli_can_require_fresh_spot(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_ts = datetime(2026, 5, 10, 12, 0, 10, tzinfo=timezone.utc)
        context_path = root / "contexts.ndjson"
        spot_path = root / "spot_ticks.ndjson"
        output_path = root / "cli_merged_contexts.ndjson"
        issue_path = root / "cli_merge_issues.ndjson"
        contexts = [
            {
                "market_ticker": "KXBTC15M-FRESHSPOT",
                "context_ts_utc": base_ts.isoformat(),
                "spot": 91.0,
            },
            {
                "market_ticker": "KXBTC15M-STALEREQUIRED",
                "context_ts_utc": (base_ts + timedelta(seconds=20)).isoformat(),
                "spot": 92.0,
            },
        ]
        context_path.write_text(
            "\n".join(json.dumps(row) for row in contexts) + "\n",
            encoding="utf-8",
        )
        spot_path.write_text(
            json.dumps(
                {
                    "exchange_ts_utc": (base_ts - timedelta(seconds=2)).isoformat(),
                    "price": 101.0,
                    "source": "unit_spot",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            result = spot_context_merge_main(
                [
                    "--contexts",
                    str(context_path),
                    "--spot-ticks",
                    str(spot_path),
                    "--output",
                    str(output_path),
                    "--issues",
                    str(issue_path),
                    "--max-age-ms",
                    "5000",
                    "--require-spot",
                ]
            )

        self.assertEqual(result, 0)
        written = output_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(written), 1)
        self.assertIn("KXBTC15M-FRESHSPOT", written[0])
        self.assertIn("KXBTC15M-STALEREQUIRED", issue_path.read_text(encoding="utf-8"))

    def test_v28_context_source_extracts_model_context_without_quotes(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        event = {
            "market": "KXBTC15M-V28CTX",
            "ts_wall": decision.isoformat(),
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 100.8,
            "mushroom_v28_p_yes": 0.64,
            "mushroom_v28_seconds_to_close": 600,
            "mushroom_v28_btc_age_ms": 250,
            "mushroom_v28_ask_cents": 70,
        }

        context = context_from_v28_event(event, market_ticker="KXBTC15M-V28CTX")

        self.assertEqual(context["market_ticker"], "KXBTC15M-V28CTX")
        self.assertEqual(context["spot"], 100.8)
        self.assertEqual(context["current_calibrated_p_yes"], 0.64)
        self.assertNotIn("mushroom_v28_ask_cents", context)
        self.assertEqual(
            context["settlement_ts_utc"],
            (decision + timedelta(seconds=600)).isoformat(),
        )
        self.assertEqual(
            context["spot_ts_utc"],
            (decision - timedelta(milliseconds=250)).isoformat(),
        )

    def test_v28_context_source_cli_filters_window_and_reports_issues(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        good = {
            "market": "KXBTC15M-V28CTX",
            "ts_wall": decision.isoformat(),
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 100.8,
            "mushroom_v28_p_yes": 0.64,
            "mushroom_v28_seconds_to_close": 600,
        }
        bad = dict(good)
        bad["ts_wall"] = (decision + timedelta(seconds=1)).isoformat()
        bad.pop("mushroom_v28_p_yes")
        other_market = dict(good)
        other_market["market"] = "KXBTC15M-OTHER"
        input_path = root / "execution_events.ndjson"
        output_path = root / "passive_contexts.ndjson"
        issue_path = root / "issues.ndjson"
        input_path.write_text(
            "\n".join(json.dumps(row) for row in (good, bad, other_market)) + "\n",
            encoding="utf-8",
        )

        written, issues = convert_v28_events_to_passive_contexts(
            input_path,
            output_path,
            issue_path,
            market_ticker="KXBTC15M-V28CTX",
            start_ts_utc=decision - timedelta(seconds=1),
            end_ts_utc=decision + timedelta(seconds=2),
            settlement_ts_utc=decision + timedelta(minutes=15),
        )

        self.assertEqual(written, 1)
        self.assertEqual(issues, 1)
        self.assertIn("v28_execution_context_only", output_path.read_text(encoding="utf-8"))
        self.assertIn("missing v28 context fields", issue_path.read_text(encoding="utf-8"))

        with contextlib.redirect_stdout(io.StringIO()):
            result = v28_context_source_main(
                [
                    "--input",
                    str(input_path),
                    "--output",
                    str(root / "cli_contexts.ndjson"),
                    "--issues",
                    str(root / "cli_issues.ndjson"),
                    "--market-ticker",
                    "KXBTC15M-V28CTX",
                    "--settlement-ts-utc",
                    (decision + timedelta(minutes=15)).isoformat(),
                ]
            )
        self.assertEqual(result, 0)

    def test_v28_context_tailer_records_contexts_and_issues(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        good = {
            "market": "KXBTC15M-TAIL",
            "ts_wall": decision.isoformat(),
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 100.8,
            "mushroom_v28_p_yes": 0.64,
            "mushroom_v28_seconds_to_close": 600,
        }
        bad = dict(good)
        bad["ts_wall"] = (decision + timedelta(seconds=1)).isoformat()
        bad.pop("mushroom_v28_p_yes")
        other_market = dict(good)
        other_market["market"] = "KXBTC15M-OTHER"
        input_path = root / "execution_events.ndjson"
        output_path = root / "passive_contexts.ndjson"
        issue_path = root / "issues.ndjson"
        status_path = root / "status.json"
        input_path.write_text(
            "\n".join(json.dumps(row) for row in (good, bad, other_market)) + "\n",
            encoding="utf-8",
        )

        status = run_v28_context_tailer(
            input_path=input_path,
            output_path=output_path,
            issue_path=issue_path,
            status_path=status_path,
            market_ticker="KXBTC15M-TAIL",
            settlement_ts_utc=decision + timedelta(minutes=15),
        )

        output_rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
        issue_rows = [json.loads(line) for line in issue_path.read_text(encoding="utf-8").splitlines()]
        status_payload = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status.contexts_written, 1)
        self.assertEqual(status.issue_count, 1)
        self.assertEqual(status.skipped_other_market, 1)
        self.assertEqual(output_rows[0]["source"], "v28_context_tailer")
        self.assertEqual(output_rows[0]["market_ticker"], "KXBTC15M-TAIL")
        self.assertIn("missing v28 context fields", issue_rows[0]["reason"])
        self.assertEqual(status_payload["contexts_written"], 1)

        with self.assertRaises(FileExistsError):
            run_v28_context_tailer(
                input_path=input_path,
                output_path=output_path,
                issue_path=root / "issues2.ndjson",
                status_path=root / "status2.json",
            )

        with self.assertRaises(FileNotFoundError):
            run_v28_context_tailer(
                input_path=root / "missing.ndjson",
                output_path=root / "missing_contexts.ndjson",
                issue_path=root / "missing_issues.ndjson",
                status_path=root / "missing_status.json",
            )

    def test_v28_context_tailer_cli_writes_status(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        input_path = root / "execution_events.ndjson"
        output_path = root / "cli_contexts.ndjson"
        issue_path = root / "cli_issues.ndjson"
        status_path = root / "cli_status.json"
        input_path.write_text(
            json.dumps(
                {
                    "market": "KXBTC15M-TAILCLI",
                    "ts_wall": decision.isoformat(),
                    "mushroom_v28_strike": 100.0,
                    "mushroom_v28_btc_price": 100.8,
                    "mushroom_v28_p_yes": 0.64,
                    "mushroom_v28_seconds_to_close": 600,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            result = v28_context_tailer_main(
                [
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--issues",
                    str(issue_path),
                    "--status",
                    str(status_path),
                    "--market-ticker",
                    "KXBTC15M-TAILCLI",
                    "--max-rows",
                    "1",
                ]
            )

        self.assertEqual(result, 0)
        status_payload = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status_payload["status"], "max_rows_reached")
        self.assertEqual(status_payload["contexts_written"], 1)

    def test_v28_context_tailer_can_seed_latest_prior_context(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        older = {
            "market": "KXBTC15M-SEED",
            "ts_wall": decision.isoformat(),
            "mushroom_v28_strike": 100.0,
            "mushroom_v28_btc_price": 99.5,
            "mushroom_v28_p_yes": 0.40,
            "mushroom_v28_seconds_to_close": 600,
        }
        newer = dict(older)
        newer["ts_wall"] = (decision + timedelta(seconds=10)).isoformat()
        newer["mushroom_v28_btc_price"] = 100.5
        newer["mushroom_v28_p_yes"] = 0.60
        malformed = dict(newer)
        malformed["market"] = "KXBTC15M-SEED-MALFORMED"
        malformed.pop("mushroom_v28_p_yes")
        input_path = root / "execution_events.ndjson"
        output_path = root / "seed_contexts.ndjson"
        issue_path = root / "seed_issues.ndjson"
        status_path = root / "seed_status.json"
        input_path.write_text(
            "\n".join(json.dumps(row) for row in (older, malformed, newer)) + "\n",
            encoding="utf-8",
        )

        status = run_v28_context_tailer(
            input_path=input_path,
            output_path=output_path,
            issue_path=issue_path,
            status_path=status_path,
            market_ticker="KXBTC15M-SEED",
            start_at_end=True,
            seed_last_contexts=True,
        )

        rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(status.contexts_written, 1)
        self.assertEqual(status.seeded_contexts, 1)
        self.assertEqual(status.issue_count, 0)
        self.assertEqual(rows[0]["source"], "v28_context_tailer_seed")
        self.assertEqual(rows[0]["spot"], 100.5)
        self.assertEqual(rows[0]["current_calibrated_p_yes"], 0.60)

        with self.assertRaises(ValueError):
            run_v28_context_tailer(
                input_path=input_path,
                output_path=root / "bad_seed_contexts.ndjson",
                issue_path=root / "bad_seed_issues.ndjson",
                status_path=root / "bad_seed_status.json",
                seed_last_contexts=True,
            )

    def test_shadow_pipeline_runs_raw_candidate_to_replay_manifest(self) -> None:
        root = Path(tempfile.mkdtemp())
        input_dir = root / "input"
        output_root = root / "pipeline_artifacts"
        input_dir.mkdir()
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        raw_path = input_dir / "raw_candidates.ndjson"
        label_path = input_dir / "label_contexts.ndjson"
        raw_rows = [
            {
                "market_ticker": "KXBTC15M-PIPE1",
                "decision_ts_utc": decision.isoformat(),
                "recv_ts_utc": decision.isoformat(),
                "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                "strike": 100.0,
                "spot": 100.8,
                "yes_ask_cents": 60,
                "no_ask_cents": 42,
                "fee_cents": 1.0,
                "fill_prob": 1.0,
                "current_calibrated_p_yes": 0.65,
            },
            {
                "market_ticker": "KXBTC15M-PIPE2",
                "decision_ts_utc": (decision + timedelta(seconds=1)).isoformat(),
                "recv_ts_utc": (decision + timedelta(seconds=1)).isoformat(),
                "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                "strike": 100.0,
                "spot": 99.2,
                "yes_ask_cents": 40,
                "no_ask_cents": 62,
                "fee_cents": 1.0,
                "fill_prob": 1.0,
                "current_calibrated_p_yes": 0.35,
            },
        ]
        label_rows = [
            {
                "market_ticker": "KXBTC15M-PIPE1",
                "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                "label_available_ts_utc": (decision + timedelta(minutes=16)).isoformat(),
                "settlement_price": 101.0,
                "strike": 100.0,
            },
            {
                "market_ticker": "KXBTC15M-PIPE2",
                "settlement_ts_utc": (decision + timedelta(minutes=15)).isoformat(),
                "label_available_ts_utc": (decision + timedelta(minutes=16)).isoformat(),
                "settlement_price": 99.0,
                "strike": 100.0,
            },
        ]
        raw_path.write_text("\n".join(json.dumps(row) for row in raw_rows) + "\n", encoding="utf-8")
        label_path.write_text("\n".join(json.dumps(row) for row in label_rows) + "\n", encoding="utf-8")

        with contextlib.redirect_stdout(io.StringIO()):
            result = shadow_pipeline_main(
                [
                    "--source-type",
                    "raw",
                    "--input",
                    str(raw_path),
                    "--label-contexts",
                    str(label_path),
                    "--root",
                    str(output_root),
                    "--annualized-vol",
                    "0.5",
                    "--sample-count",
                    "400",
                    "--seed",
                    "5",
                    "--min-fill-prob",
                    "0.5",
                    "--counterfactual-fill-threshold",
                    "0.5",
                ]
            )

        self.assertEqual(result, 0)
        manifest = json.loads((output_root / "pipeline_work" / "pipeline_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["contexts_written"], 2)
        self.assertEqual(manifest["labels_written"], 2)
        self.assertEqual(manifest["replay_candidate_count"], 2)
        self.assertTrue((output_root / "candidate_snapshots" / "candidate_snapshots.ndjson").exists())
        self.assertTrue((output_root / "settlement_labels" / "settlement_labels.ndjson").exists())
        self.assertTrue(Path(manifest["replay_json_path"]).exists())

    def test_online_calibrated_replay_updates_only_available_prior_labels(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        rows: list[ReplayInput] = []
        specs = [
            ("KXBTC15M-ONLINE1", 0, 120, 0.9, 99.0),
            ("KXBTC15M-ONLINE2", 60, 180, 0.9, 101.0),
            ("KXBTC15M-ONLINE3", 150, 240, 0.1, 99.0),
        ]
        for ticker, decision_offset, label_offset, p_raw, settlement in specs:
            row_decision = decision + timedelta(seconds=decision_offset)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=row_decision,
                recv_ts_utc=row_decision,
                strike=100.0,
                spot=100.0,
                yes_ask_cents=50.0,
                no_ask_cents=50.0,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(seconds=label_offset),
                settlement_price=settlement,
                strike=100.0,
            )
            rows.append(
                ReplayInput(
                    snapshot=snapshot,
                    label=label,
                    particle_p_yes=p_raw,
                    brownian_p_yes=0.5,
                    market_p_yes=0.5,
                    current_calibrated_p_yes=0.5,
                )
            )
        calibrator = LabelGatedACICalibrator(q=0.1, step_size=0.1)

        report = evaluate_online_calibrated_replay(rows, calibrator=calibrator)

        self.assertEqual(report.candidate_count, 3)
        self.assertAlmostEqual(report.steps[0].q_at_decision, 0.1)
        self.assertAlmostEqual(report.steps[1].q_at_decision, 0.1)
        self.assertGreater(report.steps[2].q_at_decision, 0.1)
        self.assertLess(report.final_q, report.steps[2].q_at_decision)

    def test_online_calibrated_replay_refuses_label_available_at_decision(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-LEAKLABEL",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=100.0,
            yes_ask_cents=50.0,
            no_ask_cents=50.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-LEAKLABEL",
            settlement_ts_utc=decision,
            label_available_ts_utc=decision,
            settlement_price=101.0,
            strike=100.0,
        )

        with self.assertRaises(FutureDataLeakageError):
            evaluate_online_calibrated_replay(
                [
                    ReplayInput(
                        snapshot=snapshot,
                        label=label,
                        particle_p_yes=0.6,
                        brownian_p_yes=0.5,
                        market_p_yes=0.5,
                        current_calibrated_p_yes=0.5,
                    )
                ]
            )

    def test_online_calibrated_report_cli_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-ONLINEREPORT",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=101.0,
            yes_ask_cents=60.0,
            no_ask_cents=42.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker="KXBTC15M-ONLINEREPORT",
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.0,
            strike=100.0,
        )
        CandidateSnapshotRecorder(root).record(
            snapshot,
            decision_shadow="candidate",
            reason="online_report_test",
            extra={
                "particle_p_yes": 0.7,
                "brownian_p_yes": 0.6,
                "market_p_yes": 0.58,
                "current_calibrated_p_yes": 0.65,
            },
        )
        SettlementLabelRecorder(root).record(label, source="online_report_test")

        with contextlib.redirect_stdout(io.StringIO()):
            result = particle_reports_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "online_replay",
                    "--online-calibrated",
                ]
            )

        self.assertEqual(result, 0)
        report_json = root / "reports" / "online_replay.json"
        payload = json.loads(report_json.read_text(encoding="utf-8"))
        self.assertIn("online_calibrated", payload)
        self.assertTrue((root / "reports" / "online_replay.md").exists())

    def test_reports_cli_can_explicitly_skip_unlabeled_active_market(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        labeled_snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-LABELED",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=101.0,
            yes_ask_cents=60.0,
            no_ask_cents=42.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        unlabeled_snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-ACTIVE",
            decision_ts_utc=decision + timedelta(seconds=1),
            recv_ts_utc=decision + timedelta(seconds=1),
            strike=100.0,
            spot=99.0,
            yes_ask_cents=40.0,
            no_ask_cents=62.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        for snapshot in (labeled_snapshot, unlabeled_snapshot):
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="skip_unlabeled_test",
                extra={
                    "particle_p_yes": 0.7,
                    "brownian_p_yes": 0.6,
                    "market_p_yes": 0.55,
                    "current_calibrated_p_yes": 0.65,
                },
            )
        SettlementLabelRecorder(root).record(
            SettlementLabel(
                market_ticker="KXBTC15M-LABELED",
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=101.0,
                strike=100.0,
            ),
            source="skip_unlabeled_test",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            result = particle_reports_main(
                [
                    "--candidates",
                    str(root / "candidate_snapshots" / "candidate_snapshots.ndjson"),
                    "--labels",
                    str(root / "settlement_labels" / "settlement_labels.ndjson"),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "resolved_subset",
                    "--allow-missing-labels",
                ]
            )

        self.assertEqual(result, 0)
        payload = json.loads((root / "reports" / "resolved_subset.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["source_candidate_count"], 2)
        self.assertEqual(payload["skipped_unlabeled_count"], 1)
        self.assertEqual(payload["denominator_scope"], "resolved_labeled_subset")

    def test_replay_diagnostics_summarizes_failure_modes(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        report_path = root / "replay.json"
        report_path.write_text(
            json.dumps(
                {
                    "candidate_count": 2,
                    "selected_count": 2,
                    "total_counterfactual_pnl_cents": -5.0,
                    "particle": {"brier": 0.25, "log_loss": 0.70},
                    "market": {"brier": 0.20, "log_loss": 0.60},
                    "current_calibrated": {"brier": 0.22, "log_loss": 0.65},
                    "decisions": [
                        {
                            "market_ticker": "KXBTC15M-DIAG1",
                            "decision_ts_utc": decision.isoformat(),
                            "settlement_result_yes": False,
                            "particle_p_yes": 0.7,
                            "brownian_p_yes": 0.6,
                            "market_p_yes": 0.5,
                            "current_calibrated_p_yes": 0.55,
                            "ev_yes_cents": 10.0,
                            "ev_no_cents": -8.0,
                            "selected": True,
                            "side": "yes",
                            "filled_counterfactual": True,
                            "won": False,
                            "counterfactual_pnl_cents": -20.0,
                            "reason": "selected",
                        },
                        {
                            "market_ticker": "KXBTC15M-DIAG2",
                            "decision_ts_utc": (decision + timedelta(seconds=1)).isoformat(),
                            "settlement_result_yes": True,
                            "particle_p_yes": 0.8,
                            "brownian_p_yes": 0.7,
                            "market_p_yes": 0.6,
                            "current_calibrated_p_yes": 0.65,
                            "ev_yes_cents": 12.0,
                            "ev_no_cents": -9.0,
                            "selected": True,
                            "side": "yes",
                            "filled_counterfactual": True,
                            "won": True,
                            "counterfactual_pnl_cents": 15.0,
                            "reason": "selected",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        report = build_diagnostics(report_path)

        self.assertEqual(report.candidate_count, 2)
        self.assertEqual(report.selected_yes_count, 2)
        self.assertAlmostEqual(report.selected_yes_pnl_cents, -5.0)
        self.assertEqual(len(report.markets), 2)
        self.assertGreater(report.particle_brier_minus_market_brier, 0.0)

        with contextlib.redirect_stdout(io.StringIO()):
            result = replay_diagnostics_main(
                [
                    "--report",
                    str(report_path),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "diag",
                ]
            )
        self.assertEqual(result, 0)
        self.assertTrue((root / "reports" / "diag.json").exists())
        self.assertIn("Replay Diagnostics", (root / "reports" / "diag.md").read_text(encoding="utf-8"))

    def test_side_regime_diagnostic_reports_consensus_and_rule_stability(self) -> None:
        root = Path(tempfile.mkdtemp())
        report_paths = []
        base_decision = datetime(2026, 5, 11, 11, 40, tzinfo=timezone.utc)
        for idx, pnl in enumerate((-10.0, 12.0)):
            path = root / f"run{idx}" / "reports" / "replay.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "candidate_count": 2,
                        "selected_count": 2,
                        "total_counterfactual_pnl_cents": pnl + 20.0,
                        "particle": {"brier": 0.2, "log_loss": 0.6},
                        "market": {"brier": 0.1, "log_loss": 0.4},
                        "current_calibrated": {"brier": 0.12, "log_loss": 0.45},
                        "decisions": [
                            {
                                "market_ticker": "KXBTC15M-26MAY110745-45",
                                "decision_ts_utc": (base_decision + timedelta(seconds=idx)).isoformat(),
                                "settlement_result_yes": True,
                                "particle_p_yes": 0.35,
                                "brownian_p_yes": 0.4,
                                "market_p_yes": 0.9,
                                "current_calibrated_p_yes": 0.88,
                                "ev_yes_cents": -5.0,
                                "ev_no_cents": 15.0,
                                "selected": True,
                                "side": "no",
                                "filled_counterfactual": True,
                                "won": False,
                                "counterfactual_pnl_cents": pnl,
                                "reason": "selected",
                            },
                            {
                                "market_ticker": "KXBTC15M-26MAY110745-45",
                                "decision_ts_utc": (base_decision + timedelta(seconds=idx + 10)).isoformat(),
                                "settlement_result_yes": True,
                                "particle_p_yes": 0.8,
                                "brownian_p_yes": 0.7,
                                "market_p_yes": 0.82,
                                "current_calibrated_p_yes": 0.85,
                                "ev_yes_cents": 12.0,
                                "ev_no_cents": -8.0,
                                "selected": True,
                                "side": "yes",
                                "filled_counterfactual": True,
                                "won": True,
                                "counterfactual_pnl_cents": 20.0,
                                "reason": "selected",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            report_paths.append(path)

        report = build_side_regime_diagnostic(report_paths)

        self.assertEqual(report.run_count, 2)
        self.assertIn("skip_against_consensus_20", {row.rule for row in report.rule_summary_rows})
        self.assertIn("skip_against_consensus_20", report.stable_positive_rules)
        consensus_buckets = {
            row.bucket: row
            for row in report.bucket_rows
            if row.bucket_type == "consensus"
        }
        self.assertEqual(consensus_buckets["against_market_current"].selected_count, 2)
        self.assertEqual(consensus_buckets["aligned_with_market_current"].selected_count, 2)

        with contextlib.redirect_stdout(io.StringIO()):
            result = side_regime_diagnostic_main(
                [
                    "--report",
                    str(report_paths[0]),
                    "--report",
                    str(report_paths[1]),
                    "--output-dir",
                    str(root / "side_regime_reports"),
                    "--stem",
                    "side_regime",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "side_regime_reports" / "side_regime.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(payload["rule_summary_rows"]), 1)
        self.assertIn("Side/Regime Diagnostic", (root / "side_regime_reports" / "side_regime.md").read_text(encoding="utf-8"))

    def test_ev_rank_calibration_diagnostic_flags_unstable_top_ev_bucket(self) -> None:
        root = Path(tempfile.mkdtemp())
        report_paths = []
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        for idx, top_pnl in enumerate((-30.0, 20.0)):
            decisions = []
            for row_idx in range(5):
                is_top_ev = row_idx == 0
                decision_pnl = top_pnl if is_top_ev else 5.0
                decisions.append(
                    {
                        "market_ticker": "KXBTC15M-26MAY111200-00",
                        "decision_ts_utc": (
                            base_decision + timedelta(seconds=idx * 60 + row_idx)
                        ).isoformat(),
                        "settlement_result_yes": row_idx % 2 == 0,
                        "particle_p_yes": 0.8 if is_top_ev else 0.45,
                        "brownian_p_yes": 0.65 if is_top_ev else 0.5,
                        "market_p_yes": 0.55 if is_top_ev else 0.48,
                        "current_calibrated_p_yes": 0.6 if is_top_ev else 0.49,
                        "ev_yes_cents": 25.0 if is_top_ev else 3.0 + row_idx,
                        "ev_no_cents": -5.0 if is_top_ev else 2.0,
                        "selected": True,
                        "side": "yes",
                        "filled_counterfactual": True,
                        "won": decision_pnl > 0.0,
                        "counterfactual_pnl_cents": decision_pnl,
                        "reason": "selected",
                    }
                )
            path = root / f"run{idx}" / "reports" / "replay.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"decisions": decisions}), encoding="utf-8")
            report_paths.append(path)

        report = build_ev_rank_calibration_diagnostic(report_paths)

        self.assertEqual(report.run_count, 2)
        self.assertFalse(report.top_ev_bucket_stable_positive)
        top_summary = {
            row.bucket: row
            for row in report.ev_bucket_summary_rows
        }["ev_rank_1_highest"]
        self.assertEqual(top_summary.positive_run_count, 1)
        self.assertIn(
            report.best_probability_model_by_brier,
            {"particle", "brownian", "market", "current_calibrated"},
        )

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = ev_rank_calibration_diagnostic_main(
                [
                    "--report",
                    str(report_paths[0]),
                    "--report",
                    str(report_paths[1]),
                    "--output-dir",
                    str(root / "ev_reports"),
                    "--stem",
                    "ev_diag",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "ev_reports" / "ev_diag.json").read_text(encoding="utf-8"))
        self.assertFalse(payload["top_ev_bucket_stable_positive"])
        self.assertIn("top_ev_bucket_stable_positive=False", stdout.getvalue())
        self.assertIn("EV Rank / Calibration Diagnostic", (root / "ev_reports" / "ev_diag.md").read_text(encoding="utf-8"))

    def test_market_cluster_diagnostic_equal_weights_markets(self) -> None:
        root = Path(tempfile.mkdtemp())
        path = root / "run0" / "reports" / "replay.json"
        path.parent.mkdir(parents=True)
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        decisions = []
        for market_idx, (ticker, result_yes) in enumerate(
            (("KXBTC15M-26MAY111200-00", True), ("KXBTC15M-26MAY111215-15", False))
        ):
            for row_idx in range(2):
                decisions.append(
                    {
                        "market_ticker": ticker,
                        "decision_ts_utc": (
                            base_decision + timedelta(minutes=market_idx, seconds=row_idx)
                        ).isoformat(),
                        "settlement_result_yes": result_yes,
                        "particle_p_yes": 0.8 if result_yes else 0.7,
                        "brownian_p_yes": 0.65 if result_yes else 0.55,
                        "market_p_yes": 0.55 if result_yes else 0.45,
                        "current_calibrated_p_yes": 0.6 if result_yes else 0.4,
                        "ev_yes_cents": 10.0 if result_yes else 8.0,
                        "ev_no_cents": -2.0 if result_yes else 1.0,
                        "selected": True,
                        "side": "yes",
                        "filled_counterfactual": True,
                        "won": result_yes,
                        "counterfactual_pnl_cents": 20.0 if result_yes else -10.0,
                        "reason": "selected",
                    }
                )
        path.write_text(json.dumps({"decisions": decisions}), encoding="utf-8")

        report = build_market_cluster_diagnostic([path], ev_bucket_count=2)

        self.assertEqual(report.market_count, 2)
        self.assertEqual(report.candidate_count, 4)
        self.assertEqual(report.best_probability_model_by_market_brier, "current_calibrated")
        self.assertEqual({row.market_ticker for row in report.market_rows}, {
            "KXBTC15M-26MAY111200-00",
            "KXBTC15M-26MAY111215-15",
        })

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = market_cluster_diagnostic_main(
                [
                    "--report",
                    str(path),
                    "--output-dir",
                    str(root / "market_reports"),
                    "--stem",
                    "market_diag",
                    "--ev-bucket-count",
                    "2",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "market_reports" / "market_diag.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["market_count"], 2)
        self.assertIn("market_count=2", stdout.getvalue())
        self.assertIn("Market Cluster Diagnostic", (root / "market_reports" / "market_diag.md").read_text(encoding="utf-8"))

    def test_meta_probability_loro_trains_on_other_runs_only(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-META{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.0,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="meta_loro_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.60 if result_yes else 0.40,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.62 if result_yes else 0.38,
                    },
                )
                label_recorder.record(label, source="meta_loro_unit")

        report = build_meta_probability_loro_report(run_roots, epochs=30)

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual({row.train_run_count for row in report.holdout_rows}, {2})
        self.assertEqual({row.train_market_count for row in report.holdout_rows}, {4})

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = meta_probability_loro_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--output-dir",
                    str(root / "meta_reports"),
                    "--stem",
                    "meta_loro",
                    "--epochs",
                    "30",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "meta_reports" / "meta_loro.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("promotion_safe=", stdout.getvalue())
        self.assertIn("Meta Probability LORO Report", (root / "meta_reports" / "meta_loro.md").read_text(encoding="utf-8"))

    def test_state_feature_loro_trains_on_other_runs_only(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-STATE{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=101.0 if result_yes else 99.0,
                    yes_ask_cents=46.0 if result_yes else 54.0,
                    no_ask_cents=56.0 if result_yes else 48.0,
                    fee_cents=1.0,
                    fill_prob=0.8,
                    yes_fill_prob=0.9 if result_yes else 0.6,
                    no_fill_prob=0.6 if result_yes else 0.9,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.5 if result_yes else 98.5,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="state_loro_unit",
                    extra={
                        "particle_p_yes": 0.68 if result_yes else 0.32,
                        "brownian_p_yes": 0.59 if result_yes else 0.41,
                        "market_p_yes": 0.57 if result_yes else 0.43,
                        "current_calibrated_p_yes": 0.61 if result_yes else 0.39,
                    },
                )
                label_recorder.record(label, source="state_loro_unit")

        report = build_state_feature_loro_report(run_roots, epochs=30)

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual({row.train_run_count for row in report.holdout_rows}, {2})
        self.assertEqual({row.train_market_count for row in report.holdout_rows}, {4})
        self.assertIn("state_book_cost", {row.model for row in report.summary_rows})

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = state_feature_loro_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--output-dir",
                    str(root / "state_reports"),
                    "--stem",
                    "state_loro",
                    "--epochs",
                    "30",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "state_reports" / "state_loro.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("promotion_safe=", stdout.getvalue())
        self.assertIn("State Feature LORO Report", (root / "state_reports" / "state_loro.md").read_text(encoding="utf-8"))

    def test_pasc_loro_threshold_diagnostic_uses_held_out_runs(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-PASC{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.5 if result_yes else 99.5,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="pasc_loro_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.60 if result_yes else 0.40,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.62 if result_yes else 0.38,
                    },
                )
                label_recorder.record(label, source="pasc_loro_unit")

        report = build_pasc_threshold_loro_report(
            run_roots,
            variants=("particle",),
            min_ev_grid=(0.0, 5.0),
            min_fill_grid=(0.0,),
        )

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual({row.train_run_count for row in report.holdout_rows}, {2})
        self.assertEqual({row.variant for row in report.holdout_rows}, {"particle"})
        self.assertEqual(
            {row.selector for row in report.selector_summary_rows},
            {"train_best_gate_score", "train_best_stable_pnl", "train_best_total_pnl"},
        )

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = pasc_loro_threshold_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--variant",
                    "particle",
                    "--min-ev-grid",
                    "0,5",
                    "--min-fill-grid",
                    "0",
                    "--output-dir",
                    str(root / "pasc_reports"),
                    "--stem",
                    "pasc_loro",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "pasc_reports" / "pasc_loro.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("promotion_safe=", stdout.getvalue())
        self.assertIn(
            "PASC Threshold LORO Diagnostic",
            (root / "pasc_reports" / "pasc_loro.md").read_text(encoding="utf-8"),
        )

    def test_anchor_switch_loro_trains_on_other_runs_only(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-ANCHOR{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=101.0 if result_yes else 99.0,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="anchor_switch_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.62 if result_yes else 0.38,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.64 if result_yes else 0.36,
                    },
                )
                label_recorder.record(label, source="anchor_switch_unit")

        report = build_anchor_switch_loro_report(run_roots, min_bucket_clusters=1)

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual({row.train_run_count for row in report.holdout_rows}, {2})
        self.assertIn("time_moneyness", {row.spec for row in report.summary_rows})

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = anchor_switch_loro_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--min-bucket-clusters",
                    "1",
                    "--output-dir",
                    str(root / "anchor_reports"),
                    "--stem",
                    "anchor_loro",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "anchor_reports" / "anchor_loro.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("promotion_safe=", stdout.getvalue())
        self.assertIn(
            "Anchor Switch LORO Report",
            (root / "anchor_reports" / "anchor_loro.md").read_text(encoding="utf-8"),
        )

    def test_spot_rv_anchor_switch_loro_uses_only_tick_eligible_runs(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-RVANCHOR{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                direction = 1.0 if result_yes else -1.0
                for offset in (5, 4, 3, 2, 1):
                    tick_ts = ts - timedelta(seconds=offset)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": 100.0 + direction * 0.02 * (5 - offset),
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.2 if result_yes else 99.8,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="spot_rv_anchor_switch_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.62 if result_yes else 0.38,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.64 if result_yes else 0.36,
                    },
                )
                label_recorder.record(label, source="spot_rv_anchor_switch_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_spot_rv_anchor_switch_loro_report(
            run_roots + [root / "missing_spot_run"],
            min_bucket_clusters=1,
        )

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertIn("rv_terminal", report.anchors)
        self.assertFalse(report.promotion_safe)
        self.assertTrue(report.summary_rows)
        self.assertTrue(all(hasattr(row, "market_ev_rank_correlation_sign") for row in report.holdout_rows))
        self.assertTrue(all(hasattr(row, "positive_market_top_bucket_count") for row in report.summary_rows))
        self.assertEqual(sum(row.rv_fallback_row_count for row in report.run_inputs), 0)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_rv_anchor_switch_loro_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--min-bucket-clusters",
                    "1",
                    "--output-dir",
                    str(root / "spot_rv_anchor_reports"),
                    "--stem",
                    "spot_rv_anchor",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "spot_rv_anchor_reports" / "spot_rv_anchor.json").read_text(encoding="utf-8"))
        self.assertIn("rv_terminal", payload["anchors"])
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("market_ev_rank_correlation_sign", payload["holdout_rows"][0])
        self.assertIn("eligible_run_count=3", stdout.getvalue())
        self.assertIn(
            "Spot RV Anchor Switch LORO Report",
            (root / "spot_rv_anchor_reports" / "spot_rv_anchor.md").read_text(encoding="utf-8"),
        )

    def test_spot_rv_current_residual_loro_defaults_thin_buckets_to_current(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"residual_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-RVRESID{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                direction = 1.0 if result_yes else -1.0
                for offset in (5, 4, 3, 2, 1):
                    tick_ts = ts - timedelta(seconds=offset)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": 100.0 + direction * 0.03 * (5 - offset),
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.2 if result_yes else 99.8,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="spot_rv_current_residual_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.62 if result_yes else 0.38,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.64 if result_yes else 0.36,
                    },
                )
                label_recorder.record(label, source="spot_rv_current_residual_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_spot_rv_current_residual_loro_report(
            run_roots + [root / "missing_spot_run"],
            min_bucket_clusters=10,
        )

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertFalse(report.promotion_safe)
        self.assertFalse(report.candidate_ready_for_predeclared_shadow)
        self.assertTrue(report.summary_rows)
        self.assertTrue(all(row.nudged_bucket_count == 0 for row in report.holdout_rows))
        self.assertTrue(all(row.bucket_count == 0 for row in report.holdout_rows))
        self.assertTrue(all(not row.beats_current_calibrated for row in report.holdout_rows))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_rv_current_residual_loro_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--min-bucket-clusters",
                    "10",
                    "--output-dir",
                    str(root / "spot_rv_residual_reports"),
                    "--stem",
                    "spot_rv_current_residual",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads(
            (root / "spot_rv_residual_reports" / "spot_rv_current_residual.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertEqual(payload["min_bucket_clusters"], 10)
        self.assertTrue(all(row["nudged_bucket_count"] == 0 for row in payload["holdout_rows"]))
        self.assertIn("candidate_ready_for_predeclared_shadow=False", stdout.getvalue())
        self.assertIn(
            "Spot RV Current Residual LORO Report",
            (root / "spot_rv_residual_reports" / "spot_rv_current_residual.md").read_text(encoding="utf-8"),
        )

    def test_spot_drift_terminal_uses_past_ticks_only(self) -> None:
        decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-DRIFTLEAK",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=100.0,
            yes_ask_cents=50.0,
            no_ask_cents=51.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker=snapshot.market_ticker,
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.0,
            strike=100.0,
        )
        row = ReplayInput(
            snapshot=snapshot,
            label=label,
            particle_p_yes=0.50,
            brownian_p_yes=0.50,
            market_p_yes=0.50,
            current_calibrated_p_yes=0.50,
        )
        times = [
            decision - timedelta(seconds=3),
            decision - timedelta(seconds=2),
            decision - timedelta(seconds=1),
            decision + timedelta(seconds=1),
        ]
        prices = [100.0, 100.0, 100.0, 150.0]

        drift, fallback = recent_spot_drift_per_second(
            row,
            times,
            prices,
            window_seconds=5,
            drift_weight=1.0,
            total_drift_cap_bps=100.0,
        )

        self.assertFalse(fallback)
        self.assertAlmostEqual(drift, 0.0)

        stale_drift, stale_fallback = recent_spot_drift_per_second(
            row,
            [decision - timedelta(seconds=10)],
            [100.0],
            window_seconds=5,
            drift_weight=1.0,
            total_drift_cap_bps=100.0,
            max_spot_age_ms=5_000.0,
        )
        self.assertTrue(stale_fallback)
        self.assertAlmostEqual(stale_drift, 0.0)

    def test_spot_drift_terminal_diagnostic_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"drift_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-DRIFT{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                direction = 1.0 if result_yes else -1.0
                for offset in range(40, 0, -1):
                    tick_ts = ts - timedelta(seconds=offset)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": 100.0 + direction * 0.01 * (40 - offset),
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.2 if result_yes else 99.8,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="spot_drift_terminal_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.62 if result_yes else 0.38,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.64 if result_yes else 0.36,
                    },
                )
                label_recorder.record(label, source="spot_drift_terminal_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_spot_drift_terminal_diagnostic(run_roots + [root / "missing_spot_run"])

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertGreaterEqual(len(report.specs), 3)
        self.assertEqual({row.run_count for row in report.summary_rows}, {3})
        self.assertTrue(report.side_run_rows)
        self.assertTrue(report.side_summary_rows)
        self.assertEqual({row.side for row in report.side_summary_rows}, {"yes", "no"})
        self.assertFalse(report.promotion_safe)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_drift_terminal_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--output-dir",
                    str(root / "spot_drift_reports"),
                    "--stem",
                    "spot_drift_terminal",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "spot_drift_reports" / "spot_drift_terminal.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("side_summary_rows", payload)
        self.assertEqual({row["side"] for row in payload["side_summary_rows"]}, {"yes", "no"})
        self.assertIn("candidate_ready_for_predeclared_shadow=False", stdout.getvalue())
        self.assertIn(
            "Spot Drift Terminal Diagnostic",
            (root / "spot_drift_reports" / "spot_drift_terminal.md").read_text(encoding="utf-8"),
        )

    def test_spot_drift_regime_diagnostic_reports_stable_timestamp_safe_rules(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"drift_regime_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-DRIFTREGIME{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                direction = 1.0 if result_yes else -1.0
                for offset in range(30, 0, -1):
                    tick_ts = ts - timedelta(seconds=offset)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": 100.0 + direction * 0.02 * (30 - offset),
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.2 if result_yes else 99.8,
                    yes_ask_cents=45.0 if result_yes else 58.0,
                    no_ask_cents=58.0 if result_yes else 45.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="spot_drift_regime_unit",
                    extra={
                        "particle_p_yes": 0.50,
                        "brownian_p_yes": 0.50,
                        "market_p_yes": 0.50,
                        "current_calibrated_p_yes": 0.50,
                    },
                )
                label_recorder.record(label, source="spot_drift_regime_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_spot_drift_regime_diagnostic(
            run_roots + [root / "missing_spot_run"],
            spec_names=("drift13_cap10_fixed65_blend25",),
        )

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertEqual(report.specs, ("drift13_cap10_fixed65_blend25",))
        self.assertTrue(report.bucket_rows)
        self.assertTrue(report.rule_summary_rows)
        self.assertFalse(report.promotion_safe)
        self.assertIn(
            "drift13_cap10_fixed65_blend25:require_drift_aligned",
            report.stable_positive_rules,
        )
        drift_alignment_buckets = {
            row.bucket: row
            for row in report.bucket_rows
            if row.bucket_type == "drift_alignment"
        }
        self.assertEqual(drift_alignment_buckets["aligned_with_drift"].positive_run_count, 3)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_drift_regime_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--spec",
                    "drift13_cap10_fixed65_blend25",
                    "--output-dir",
                    str(root / "spot_drift_regime_reports"),
                    "--stem",
                    "spot_drift_regime",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads(
            (root / "spot_drift_regime_reports" / "spot_drift_regime.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["specs"], ["drift13_cap10_fixed65_blend25"])
        self.assertFalse(payload["promotion_safe"])
        self.assertIn("stable_positive_rules=", stdout.getvalue())
        self.assertIn(
            "Spot Drift Regime Diagnostic",
            (root / "spot_drift_regime_reports" / "spot_drift_regime.md").read_text(encoding="utf-8"),
        )

    def test_empirical_next_second_particle_uses_past_ticks_only(self) -> None:
        decision = datetime(2026, 5, 11, 12, 0, 0, 500000, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-EMPIRICALLEAK",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=110.0,
            spot=100.0,
            yes_ask_cents=50.0,
            no_ask_cents=51.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker=snapshot.market_ticker,
            settlement_ts_utc=decision + timedelta(seconds=10),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=99.0,
            strike=110.0,
        )
        row = ReplayInput(
            snapshot=snapshot,
            label=label,
            particle_p_yes=0.50,
            brownian_p_yes=0.50,
            market_p_yes=0.50,
            current_calibrated_p_yes=0.50,
        )
        spec = EmpiricalSecondParticleSpec(
            name="unit_empirical",
            lookback_seconds=10,
            particle_count=32,
            max_draws_per_particle=8,
            recency_half_life_seconds=0.0,
            return_cap_bps=10.0,
            mean_weight=1.0,
            brownian_blend_weight=0.0,
            min_return_count=2,
        )
        times = [
            decision - timedelta(seconds=3),
            decision - timedelta(seconds=2),
            decision - timedelta(seconds=1),
            decision + timedelta(milliseconds=250),
            decision + timedelta(seconds=1),
        ]
        prices = [100.0, 100.0, 100.0, 100.0, 200.0]

        result = empirical_second_particle_probability(row, times, prices, spec)

        self.assertFalse(result.used_fallback)
        self.assertEqual(result.return_count, 2)
        self.assertAlmostEqual(result.probability_yes, 0.0)

        stale = empirical_second_particle_probability(
            row,
            [decision - timedelta(seconds=10)],
            [100.0],
            spec,
            max_spot_age_ms=5_000.0,
        )
        self.assertTrue(stale.used_fallback)
        self.assertAlmostEqual(stale.probability_yes, row.brownian_p_yes)

    def test_empirical_next_second_particle_diagnostic_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"empirical_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-EMPIRICAL{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                direction = 1.0 if result_yes else -1.0
                for offset in range(80, 0, -1):
                    tick_ts = ts - timedelta(seconds=offset)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": 100.0 + direction * 0.01 * (80 - offset),
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.3 if result_yes else 99.7,
                    yes_ask_cents=45.0 if result_yes else 58.0,
                    no_ask_cents=58.0 if result_yes else 45.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="empirical_next_second_unit",
                    extra={
                        "particle_p_yes": 0.50,
                        "brownian_p_yes": 0.50,
                        "market_p_yes": 0.50,
                        "current_calibrated_p_yes": 0.50,
                    },
                )
                label_recorder.record(label, source="empirical_next_second_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_empirical_next_second_particle_diagnostic(run_roots + [root / "missing_spot_run"])

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertGreaterEqual(len(report.specs), 3)
        self.assertEqual({row.run_count for row in report.summary_rows}, {3})
        self.assertFalse(report.promotion_safe)
        self.assertTrue(any(row.avg_return_count > 0 for row in report.summary_rows))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = empirical_next_second_particle_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--output-dir",
                    str(root / "empirical_reports"),
                    "--stem",
                    "empirical_next_second",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "empirical_reports" / "empirical_next_second.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("candidate_ready_for_predeclared_shadow=", stdout.getvalue())
        self.assertIn(
            "Empirical Next-Second Particle Diagnostic",
            (root / "empirical_reports" / "empirical_next_second.md").read_text(encoding="utf-8"),
        )

    def test_empirical_current_anchor_defaults_stale_particle_rows_to_current(self) -> None:
        decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        snapshot = CandidateSnapshot(
            market_ticker="KXBTC15M-EMPCURRENTSTALE",
            decision_ts_utc=decision,
            recv_ts_utc=decision,
            strike=100.0,
            spot=100.0,
            yes_ask_cents=50.0,
            no_ask_cents=51.0,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker=snapshot.market_ticker,
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=101.0,
            strike=100.0,
        )
        row = ReplayInput(
            snapshot=snapshot,
            label=label,
            particle_p_yes=0.50,
            brownian_p_yes=0.20,
            market_p_yes=0.50,
            current_calibrated_p_yes=0.73,
        )
        spec = EmpiricalCurrentAnchorSpec(
            "unit_current_anchor",
            EmpiricalSecondParticleSpec("inner_unit", 233, 16, 8, 89.0, 5.0, 0.0, 0.0, 20),
            0.25,
        )
        stale_tick = {
            "available_ts_utc": decision - timedelta(seconds=10),
            "exchange_ts_utc": decision - timedelta(seconds=10),
            "price": 100.0,
            "source": "unit_spot",
        }
        tick = type("Tick", (), stale_tick)

        materialized, diagnostics = materialize_empirical_current_anchor_rows(
            [row],
            [tick],
            spec,
            max_spot_age_ms=5_000.0,
        )

        self.assertEqual(diagnostics["fallback_to_current_count"], 1)
        self.assertAlmostEqual(materialized[0].particle_p_yes, 0.73)

    def test_empirical_current_anchor_diagnostic_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"empirical_current_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-EMPCURRENT{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                direction = 1.0 if result_yes else -1.0
                for offset in range(80, 0, -1):
                    tick_ts = ts - timedelta(seconds=offset)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": 100.0 + direction * 0.01 * (80 - offset),
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.3 if result_yes else 99.7,
                    yes_ask_cents=45.0 if result_yes else 58.0,
                    no_ask_cents=58.0 if result_yes else 45.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="empirical_current_anchor_unit",
                    extra={
                        "particle_p_yes": 0.50,
                        "brownian_p_yes": 0.50,
                        "market_p_yes": 0.50,
                        "current_calibrated_p_yes": 0.50,
                    },
                )
                label_recorder.record(label, source="empirical_current_anchor_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_empirical_current_anchor_diagnostic(run_roots + [root / "missing_spot_run"])

        self.assertEqual(len(report.run_inputs), 3)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertTrue(report.summary_rows)
        self.assertFalse(report.promotion_safe)
        self.assertTrue(any(row.avg_return_count > 0 for row in report.summary_rows))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = empirical_current_anchor_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--output-dir",
                    str(root / "empirical_current_reports"),
                    "--stem",
                    "empirical_current",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "empirical_current_reports" / "empirical_current.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 3)
        self.assertIn("candidate_ready_for_predeclared_shadow=", stdout.getvalue())
        self.assertIn(
            "Empirical Current-Anchor Diagnostic",
            (root / "empirical_current_reports" / "empirical_current.md").read_text(encoding="utf-8"),
        )

    def test_empirical_market_opportunity_diagnostic_collapses_to_one_opportunity_per_market(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(2):
            run_root = root / f"market_opp_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-MARKETOPP{run_idx}{market_idx}"
                direction = 1.0 if result_yes else -1.0
                label = None
                for snapshot_idx, seconds_offset in enumerate((0, 10)):
                    ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx * 30 + seconds_offset)
                    for offset in range(80, 0, -1):
                        tick_ts = ts - timedelta(seconds=offset)
                        tick_rows.append(
                            {
                                "exchange_ts_utc": tick_ts.isoformat(),
                                "local_recv_ts_utc": tick_ts.isoformat(),
                                "price": 100.0 + direction * 0.01 * (80 - offset + snapshot_idx),
                                "source": "unit_spot",
                            }
                        )
                    snapshot = CandidateSnapshot(
                        market_ticker=ticker,
                        decision_ts_utc=ts,
                        recv_ts_utc=ts,
                        strike=100.0,
                        spot=100.3 if result_yes else 99.7,
                        yes_ask_cents=45.0 if result_yes else 58.0,
                        no_ask_cents=58.0 if result_yes else 45.0,
                        fee_cents=1.0,
                        fill_prob=1.0,
                        yes_fill_prob=1.0,
                        no_fill_prob=1.0,
                    )
                    if label is None:
                        label = SettlementLabel(
                            market_ticker=ticker,
                            settlement_ts_utc=ts + timedelta(minutes=15),
                            label_available_ts_utc=ts + timedelta(minutes=16),
                            settlement_price=101.0 if result_yes else 99.0,
                            strike=100.0,
                        )
                        label_recorder.record(label, source="empirical_market_opportunity_unit")
                    candidate_recorder.record(
                        snapshot,
                        decision_shadow="candidate",
                        reason="empirical_market_opportunity_unit",
                        extra={
                            "particle_p_yes": 0.50,
                            "brownian_p_yes": 0.50,
                            "market_p_yes": 0.50,
                            "current_calibrated_p_yes": 0.50,
                        },
                    )
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_empirical_market_opportunity_diagnostic(
            run_roots + [root / "missing_spot_run"],
            families=("current_anchor",),
        )

        self.assertEqual(len(report.run_inputs), 2)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertTrue(report.run_rows)
        self.assertEqual({row.market_count for row in report.run_rows}, {2})
        self.assertTrue(all(0 < row.selected_market_count <= row.market_count for row in report.run_rows))
        self.assertTrue(all(row.candidate_count == 4 for row in report.run_rows))
        self.assertEqual(len(report.opportunity_rows), sum(row.market_count for row in report.run_rows))
        self.assertEqual({row.candidate_count for row in report.opportunity_rows}, {2})
        self.assertFalse(report.promotion_safe)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = empirical_market_opportunity_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(root / "missing_spot_run"),
                    "--family",
                    "current_anchor",
                    "--output-dir",
                    str(root / "market_opportunity_reports"),
                    "--stem",
                    "market_opportunity",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads(
            (root / "market_opportunity_reports" / "market_opportunity.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["families"], ["current_anchor"])
        self.assertEqual(len(payload["opportunity_rows"]), sum(row["market_count"] for row in payload["run_rows"]))
        self.assertIn("candidate_ready_for_predeclared_shadow=", stdout.getvalue())
        self.assertIn("opportunity_row_count=", stdout.getvalue())
        self.assertIn(
            "Empirical Market Opportunity Diagnostic",
            (root / "market_opportunity_reports" / "market_opportunity.md").read_text(encoding="utf-8"),
        )

    def test_empirical_market_opportunity_loro_uses_holdout_only_after_training_choice(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"market_opp_loro_run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-MARKETLORO{run_idx}{market_idx}"
                direction = 1.0 if result_yes else -1.0
                label = None
                for snapshot_idx, seconds_offset in enumerate((0, 10)):
                    ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx * 30 + seconds_offset)
                    for offset in range(80, 0, -1):
                        tick_ts = ts - timedelta(seconds=offset)
                        tick_rows.append(
                            {
                                "exchange_ts_utc": tick_ts.isoformat(),
                                "local_recv_ts_utc": tick_ts.isoformat(),
                                "price": 100.0 + direction * 0.01 * (80 - offset + snapshot_idx),
                                "source": "unit_spot",
                            }
                        )
                    snapshot = CandidateSnapshot(
                        market_ticker=ticker,
                        decision_ts_utc=ts,
                        recv_ts_utc=ts,
                        strike=100.0,
                        spot=100.3 if result_yes else 99.7,
                        yes_ask_cents=45.0 if result_yes else 58.0,
                        no_ask_cents=58.0 if result_yes else 45.0,
                        fee_cents=1.0,
                        fill_prob=1.0,
                        yes_fill_prob=1.0,
                        no_fill_prob=1.0,
                    )
                    if label is None:
                        label = SettlementLabel(
                            market_ticker=ticker,
                            settlement_ts_utc=ts + timedelta(minutes=15),
                            label_available_ts_utc=ts + timedelta(minutes=16),
                            settlement_price=101.0 if result_yes else 99.0,
                            strike=100.0,
                        )
                        label_recorder.record(label, source="empirical_market_opportunity_loro_unit")
                    candidate_recorder.record(
                        snapshot,
                        decision_shadow="candidate",
                        reason="empirical_market_opportunity_loro_unit",
                        extra={
                            "particle_p_yes": 0.50,
                            "brownian_p_yes": 0.50,
                            "market_p_yes": 0.50,
                            "current_calibrated_p_yes": 0.50,
                        },
                    )
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        source_report = build_empirical_market_opportunity_diagnostic(run_roots, families=("current_anchor",))
        source_json, _ = write_empirical_market_opportunity_diagnostic(
            source_report,
            root / "market_loro_reports",
            "market_loro_source",
        )
        loro = build_market_opportunity_loro_report(source_json)

        self.assertEqual(loro.source_run_count, 3)
        self.assertEqual(loro.source_opportunity_row_count, len(source_report.opportunity_rows))
        self.assertEqual(len(loro.holdout_rows), 3)
        self.assertEqual({row.train_run_count for row in loro.choices}, {2})
        self.assertFalse(loro.promotion_safe)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = empirical_market_opportunity_loro_main(
                [
                    "--source-report",
                    str(source_json),
                    "--output-dir",
                    str(root / "market_loro_cli_reports"),
                    "--stem",
                    "market_loro",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "market_loro_cli_reports" / "market_loro.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["source_run_count"], 3)
        self.assertIn("candidate_ready_for_predeclared_shadow=", stdout.getvalue())
        self.assertIn(
            "Empirical Market Opportunity LORO",
            (root / "market_loro_cli_reports" / "market_loro.md").read_text(encoding="utf-8"),
        )

    def test_spot_micro_loro_uses_only_eligible_tick_runs(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(3):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-SPOTMICRO{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=30 * market_idx)
                for offset in (8, 5, 3, 1):
                    tick_ts = ts - timedelta(seconds=offset)
                    price = 100.0 + (0.03 * (8 - offset) if result_yes else -0.03 * (8 - offset))
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": price,
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.1 if result_yes else 99.9,
                    yes_ask_cents=46.0 if result_yes else 54.0,
                    no_ask_cents=56.0 if result_yes else 48.0,
                    fee_cents=1.0,
                    fill_prob=0.8,
                    yes_fill_prob=0.9 if result_yes else 0.6,
                    no_fill_prob=0.6 if result_yes else 0.9,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.5 if result_yes else 98.5,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="spot_micro_unit",
                    extra={
                        "particle_p_yes": 0.68 if result_yes else 0.32,
                        "brownian_p_yes": 0.59 if result_yes else 0.41,
                        "market_p_yes": 0.57 if result_yes else 0.43,
                        "current_calibrated_p_yes": 0.61 if result_yes else 0.39,
                    },
                )
                label_recorder.record(label, source="spot_micro_unit")
            if run_idx < 2:
                (run_root / "independent_spot_ticks.ndjson").write_text(
                    "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                    encoding="utf-8",
                )

        report = build_spot_micro_loro_report(run_roots, epochs=30)

        self.assertEqual(len(report.run_inputs), 2)
        self.assertEqual(len(report.skipped_run_roots), 1)
        self.assertEqual({row.train_run_count for row in report.holdout_rows}, {1})
        self.assertTrue(all(row.rows_with_recent_spot == row.row_count for row in report.run_inputs))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_micro_loro_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--run-root",
                    str(run_roots[2]),
                    "--output-dir",
                    str(root / "spot_reports"),
                    "--stem",
                    "spot_loro",
                    "--epochs",
                    "30",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "spot_reports" / "spot_loro.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["run_inputs"]), 2)
        self.assertIn("skipped_run_count=1", stdout.getvalue())
        self.assertIn("Spot Micro LORO Report", (root / "spot_reports" / "spot_loro.md").read_text(encoding="utf-8"))

    def test_spot_realized_vol_terminal_diagnostic_uses_past_ticks_only(self) -> None:
        decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        times = [
            decision - timedelta(seconds=3),
            decision - timedelta(seconds=2),
            decision - timedelta(seconds=1),
            decision + timedelta(seconds=1),
        ]
        prices = [100.0, 100.0, 100.0, 130.0]

        vol, used_fallback = realized_annualized_vol_at_decision(
            decision,
            times,
            prices,
            10,
            fallback_annualized_vol=0.65,
            floor_annualized_vol=0.20,
            cap_annualized_vol=1.50,
        )

        self.assertFalse(used_fallback)
        self.assertAlmostEqual(vol, 0.20)

    def test_spot_realized_vol_terminal_diagnostic_writes_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(2):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            tick_rows = []
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-RVTERM{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=30 * market_idx)
                for offset in (20, 13, 8, 5, 3, 1):
                    tick_ts = ts - timedelta(seconds=offset)
                    drift = 0.04 * (20 - offset)
                    price = 100.0 + (drift if result_yes else -drift)
                    tick_rows.append(
                        {
                            "exchange_ts_utc": tick_ts.isoformat(),
                            "local_recv_ts_utc": tick_ts.isoformat(),
                            "price": price,
                            "source": "unit_spot",
                        }
                    )
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.3 if result_yes else 99.7,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="spot_realized_vol_terminal_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.60 if result_yes else 0.40,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.62 if result_yes else 0.38,
                    },
                )
                label_recorder.record(label, source="spot_realized_vol_terminal_unit")
            (run_root / "independent_spot_ticks.ndjson").write_text(
                "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
                encoding="utf-8",
            )

        report = build_spot_realized_vol_terminal_diagnostic(run_roots)

        self.assertEqual(len(report.run_inputs), 2)
        self.assertEqual(report.skipped_run_roots, ())
        self.assertGreater(report.spec_count, 3)
        self.assertEqual({row.run_count for row in report.summary_rows}, {2})

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_realized_vol_terminal_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--output-dir",
                    str(root / "rv_reports"),
                    "--stem",
                    "rv_terminal",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "rv_reports" / "rv_terminal.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["spec_count"], report.spec_count)
        self.assertIn("best_by_brier=", stdout.getvalue())
        self.assertIn(
            "Spot Realized-Vol Terminal Diagnostic",
            (root / "rv_reports" / "rv_terminal.md").read_text(encoding="utf-8"),
        )

    def test_spot_realized_vol_terminal_oos_blocks_same_sample_scope(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        tick_rows = []
        for market_idx, result_yes in enumerate((True, False)):
            ticker = f"KXBTC15M-RVOOS{market_idx}"
            ts = base_decision + timedelta(seconds=30 * market_idx)
            for offset in (20, 13, 8, 5, 3, 1):
                tick_ts = ts - timedelta(seconds=offset)
                price = 100.0 + (0.02 * (20 - offset) if result_yes else -0.02 * (20 - offset))
                tick_rows.append(
                    {
                        "exchange_ts_utc": tick_ts.isoformat(),
                        "local_recv_ts_utc": tick_ts.isoformat(),
                        "price": price,
                        "source": "unit_spot",
                    }
                )
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=100.3 if result_yes else 99.7,
                yes_ask_cents=45.0 if result_yes else 55.0,
                no_ask_cents=57.0 if result_yes else 47.0,
                fee_cents=1.0,
                fill_prob=1.0,
                yes_fill_prob=1.0,
                no_fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=ts + timedelta(minutes=15),
                label_available_ts_utc=ts + timedelta(minutes=16),
                settlement_price=101.0 if result_yes else 99.0,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="spot_realized_vol_terminal_oos_unit",
                extra={
                    "particle_p_yes": 0.70 if result_yes else 0.30,
                    "brownian_p_yes": 0.60 if result_yes else 0.40,
                    "market_p_yes": 0.58 if result_yes else 0.42,
                    "current_calibrated_p_yes": 0.62 if result_yes else 0.38,
                },
            )
            label_recorder.record(label, source="spot_realized_vol_terminal_oos_unit")
        spot_path = root / "independent_spot_ticks.ndjson"
        spot_path.write_text(
            "\n".join(json.dumps(row, sort_keys=True) for row in tick_rows) + "\n",
            encoding="utf-8",
        )
        candidates = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        labels = root / "settlement_labels" / "settlement_labels.ndjson"
        rows = load_replay_inputs_from_jsonl(candidates, labels)

        same_sample = evaluate_spot_realized_vol_terminal_oos(rows, load_spot_ticks(spot_path))
        materialized_rows, vols, fallback_count = materialize_spot_realized_vol_terminal_rows(
            rows,
            load_spot_ticks(spot_path),
        )

        self.assertFalse(same_sample.gate_results.locked_oos_scope)
        self.assertFalse(same_sample.promotion_safe)
        self.assertEqual(same_sample.hypothesis_id, "rv233_blend50_fixed65_terminal_v1")
        self.assertEqual(len(materialized_rows), len(rows))
        self.assertEqual(len(vols), len(rows))
        self.assertEqual(fallback_count, same_sample.fallback_row_count)
        self.assertTrue(all(0.0 <= row.particle_p_yes <= 1.0 for row in materialized_rows))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_realized_vol_terminal_oos_main(
                [
                    "--candidates",
                    str(candidates),
                    "--labels",
                    str(labels),
                    "--spot-ticks",
                    str(spot_path),
                    "--output-dir",
                    str(root / "rv_oos_reports"),
                    "--stem",
                    "rv_oos",
                    "--evaluation-scope",
                    "locked_oos_shadow",
                    "--gate-min-candidates",
                    "1",
                    "--gate-min-markets",
                    "1",
                    "--gate-min-selected",
                    "1",
                    "--materialized-stem",
                    "rv_oos_materialized",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "rv_oos_reports" / "rv_oos.json").read_text(encoding="utf-8"))
        materialized_payload = json.loads(
            (root / "rv_oos_reports" / "rv_oos_materialized.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["hypothesis_id"], "rv233_blend50_fixed65_terminal_v1")
        self.assertIn("promotion_safe=", stdout.getvalue())
        self.assertIn("materialized_json_report=", stdout.getvalue())
        self.assertEqual(materialized_payload["candidate_count"], len(rows))
        self.assertIn("decisions", materialized_payload)
        self.assertIn(
            "Spot Realized-Vol Terminal OOS Report",
            (root / "rv_oos_reports" / "rv_oos.md").read_text(encoding="utf-8"),
        )

    def test_spot_realized_vol_terminal_locked_oos_plan_writes_manifest(self) -> None:
        root = Path(tempfile.mkdtemp())

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = spot_realized_vol_terminal_locked_oos_plan_main(
                [
                    "--hypothesis-id",
                    "rv233_blend50_fixed65_terminal_v1",
                    "--run-id",
                    "UNITRVLOCK",
                    "--dataset",
                    "particle_spot_rv_terminal_oos_unit",
                    "--artifact-root",
                    str(root / "artifacts"),
                    "--output-dir",
                    str(root / "plans"),
                    "--stem",
                    "rv_terminal_locked_plan",
                    "--run-seconds",
                    "3900",
                    "--gate-min-candidates",
                    "1000",
                    "--gate-min-markets",
                    "5",
                    "--gate-min-selected",
                    "250",
                ]
            )

        payload = json.loads((root / "plans" / "rv_terminal_locked_plan.json").read_text(encoding="utf-8"))
        md = (root / "plans" / "rv_terminal_locked_plan.md").read_text(encoding="utf-8")
        self.assertEqual(result, 0)
        self.assertEqual(payload["hypothesis_id"], "rv233_blend50_fixed65_terminal_v1")
        self.assertEqual(payload["evaluation_scope"], "locked_oos_shadow")
        self.assertEqual(payload["gate_config"]["min_market_count"], 5)
        self.assertIn("--record-independent-spot", payload["paired_capture_command"])
        self.assertIn("--require-independent-spot", payload["paired_capture_command"])
        self.assertIn("independent_spot_ticks.ndjson", payload["spot_realized_vol_terminal_oos_command"])
        self.assertIn("--evaluation-scope locked_oos_shadow", payload["spot_realized_vol_terminal_oos_command"])
        self.assertIn("research_particle.spot_realized_vol_terminal_oos", md)
        self.assertIn("json_plan=", stdout.getvalue())

    def test_fat_tail_particle_diagnostic_writes_fixed_distribution_report(self) -> None:
        root = Path(tempfile.mkdtemp())
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        run_roots = []
        for run_idx in range(2):
            run_root = root / f"run{run_idx + 1}"
            run_roots.append(run_root)
            candidate_recorder = CandidateSnapshotRecorder(run_root)
            label_recorder = SettlementLabelRecorder(run_root)
            for market_idx, result_yes in enumerate((True, False)):
                ticker = f"KXBTC15M-FATTAIL{run_idx}{market_idx}"
                ts = base_decision + timedelta(minutes=run_idx, seconds=market_idx)
                snapshot = CandidateSnapshot(
                    market_ticker=ticker,
                    decision_ts_utc=ts,
                    recv_ts_utc=ts,
                    strike=100.0,
                    spot=100.8 if result_yes else 99.2,
                    yes_ask_cents=45.0 if result_yes else 55.0,
                    no_ask_cents=57.0 if result_yes else 47.0,
                    fee_cents=1.0,
                    fill_prob=1.0,
                    yes_fill_prob=1.0,
                    no_fill_prob=1.0,
                )
                label = SettlementLabel(
                    market_ticker=ticker,
                    settlement_ts_utc=ts + timedelta(minutes=15),
                    label_available_ts_utc=ts + timedelta(minutes=16),
                    settlement_price=101.0 if result_yes else 99.0,
                    strike=100.0,
                )
                candidate_recorder.record(
                    snapshot,
                    decision_shadow="candidate",
                    reason="fat_tail_unit",
                    extra={
                        "particle_p_yes": 0.70 if result_yes else 0.30,
                        "brownian_p_yes": 0.60 if result_yes else 0.40,
                        "market_p_yes": 0.58 if result_yes else 0.42,
                        "current_calibrated_p_yes": 0.62 if result_yes else 0.38,
                    },
                )
                label_recorder.record(label, source="fat_tail_unit")

        base = terminal_jump_mixture_probability(
            spot=100.0,
            strike=101.0,
            seconds_to_close=900.0,
            annualized_vol=0.65,
            jump_weight=0.0,
            jump_vol_scale=1.0,
            jump_mean_bps=0.0,
        )
        tailed = terminal_jump_mixture_probability(
            spot=100.0,
            strike=101.0,
            seconds_to_close=900.0,
            annualized_vol=0.65,
            jump_weight=0.2,
            jump_vol_scale=5.0,
            jump_mean_bps=0.0,
        )
        self.assertGreaterEqual(base, 0.0)
        self.assertLessEqual(base, 1.0)
        self.assertGreaterEqual(tailed, 0.0)
        self.assertLessEqual(tailed, 1.0)

        report = build_fat_tail_particle_diagnostic(run_roots)

        self.assertEqual(len(report.run_inputs), 2)
        self.assertGreater(report.spec_count, 3)
        self.assertEqual({row.run_count for row in report.summary_rows}, {2})

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = fat_tail_particle_diagnostic_main(
                [
                    "--run-root",
                    str(run_roots[0]),
                    "--run-root",
                    str(run_roots[1]),
                    "--output-dir",
                    str(root / "fat_reports"),
                    "--stem",
                    "fat_tail",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "fat_reports" / "fat_tail.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["spec_count"], report.spec_count)
        self.assertIn("best_by_brier=", stdout.getvalue())
        self.assertIn("Fat-Tail Particle Diagnostic", (root / "fat_reports" / "fat_tail.md").read_text(encoding="utf-8"))

    def test_v28_rolling_vol_transfer_diagnostic_keeps_current_as_control(self) -> None:
        root = Path(tempfile.mkdtemp())
        run_root = root / "transfer_run"
        candidate_recorder = CandidateSnapshotRecorder(run_root)
        label_recorder = SettlementLabelRecorder(run_root)
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        specs = [
            ("KXBTC15M-TRANSFER0", 0, 100.4, True, 45.0, 57.0, 0.62),
            ("KXBTC15M-TRANSFER1", 20, 99.6, False, 57.0, 45.0, 0.38),
            ("KXBTC15M-TRANSFER2", 40, 100.5, True, 46.0, 56.0, 0.61),
            ("KXBTC15M-TRANSFER3", 60, 99.5, False, 56.0, 46.0, 0.39),
        ]
        for ticker, offset, spot, result_yes, yes_ask, no_ask, current_p in specs:
            ts = base_decision + timedelta(seconds=offset)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=yes_ask,
                no_ask_cents=no_ask,
                fee_cents=1.0,
                fill_prob=1.0,
                yes_fill_prob=1.0,
                no_fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=ts + timedelta(minutes=15),
                label_available_ts_utc=ts + timedelta(minutes=16),
                settlement_price=101.0 if result_yes else 99.0,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="v28_transfer_unit",
                extra={
                    "particle_p_yes": 0.50,
                    "brownian_p_yes": 0.50,
                    "market_p_yes": 0.50,
                    "current_calibrated_p_yes": current_p,
                },
            )
            label_recorder.record(label, source="v28_transfer_unit")

        pipeline_dir = run_root / "pipeline_work"
        pipeline_dir.mkdir(parents=True)
        (pipeline_dir / "label_contexts_full_refresh.ndjson").write_text(
            (run_root / "settlement_labels" / "settlement_labels.ndjson").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        replay_rows = load_replay_inputs_from_jsonl(
            run_root / "candidate_snapshots" / "candidate_snapshots.ndjson",
            run_root / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        )
        run_rows = evaluate_transfer_rows(replay_rows, root_name=run_root.name)
        by_strategy = {row.strategy: row for row in run_rows}

        self.assertEqual(by_strategy["current_calibrated_v28"].strategy_family, "baseline")
        self.assertEqual(by_strategy["current_calibrated_v28"].delta_vs_current_cents, 0.0)
        self.assertIn("rv300", by_strategy)
        self.assertIn("rv600", by_strategy)
        self.assertIn("v28_95_rv300_05", by_strategy)
        self.assertIn("v28_with_rv600_side_agreement_veto", by_strategy)
        self.assertLessEqual(
            by_strategy["v28_with_rv600_side_agreement_veto"].selected_count,
            by_strategy["current_calibrated_v28"].selected_count,
        )
        self.assertTrue(all(row.candidate_count == len(replay_rows) for row in run_rows))

        report = build_v28_rolling_vol_transfer_diagnostic(
            [run_root],
            output_json=root / "reports" / "transfer.json",
            output_md=root / "reports" / "transfer.md",
        )
        self.assertFalse(report.promotion_allowed)
        self.assertEqual(report.root_count, 1)
        self.assertEqual(report.best_probability_transfer.startswith("v28_"), True)
        write_v28_rolling_vol_transfer_diagnostic(report)
        self.assertIn("V28 Rolling-Vol Transfer Diagnostic", (root / "reports" / "transfer.md").read_text(encoding="utf-8"))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = v28_rolling_vol_transfer_diagnostic_main(
                [
                    "--root",
                    str(run_root),
                    "--output-json",
                    str(root / "reports" / "transfer_cli.json"),
                    "--output-md",
                    str(root / "reports" / "transfer_cli.md"),
                    "--write",
                ]
            )
        self.assertEqual(result, 0)
        self.assertIn("promotion_allowed=False", stdout.getvalue())
        self.assertTrue((root / "reports" / "transfer_cli.json").exists())

    def test_rv600_variation_test_accounts_for_repeated_entries_and_matched_v28(self) -> None:
        root = Path(tempfile.mkdtemp())
        run_root = root / "rv600_run"
        candidate_recorder = CandidateSnapshotRecorder(run_root)
        label_recorder = SettlementLabelRecorder(run_root)
        base_decision = datetime(2026, 5, 13, 12, 0, tzinfo=timezone.utc)

        def record_candidate(ticker: str, offset: int, spot: float, result_yes: bool) -> None:
            ts = base_decision + timedelta(seconds=offset)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=spot,
                yes_ask_cents=60.0,
                no_ask_cents=41.0,
                fee_cents=1.0,
                fill_prob=1.0,
                yes_fill_prob=1.0,
                no_fill_prob=1.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="rv600_variation_unit",
                extra={
                    "particle_p_yes": 0.50,
                    "brownian_p_yes": 0.50,
                    "market_p_yes": 0.595,
                    "current_calibrated_p_yes": 0.50,
                    "book_age_ms": 0.0,
                    "depth_count": 10.0,
                    "seconds_to_close": 360.0 - offset,
                },
            )
            if offset == 0:
                label_recorder.record(
                    SettlementLabel(
                        market_ticker=ticker,
                        settlement_ts_utc=base_decision + timedelta(seconds=360),
                        label_available_ts_utc=base_decision + timedelta(seconds=420),
                        settlement_price=101.0 if result_yes else 99.0,
                        strike=100.0,
                    ),
                    source="rv600_variation_unit",
                )

        for offset in (0, 130, 260):
            record_candidate("KXBTC15M-RV600A", offset, 101.0, True)
        record_candidate("KXBTC15M-RV600B", 0, 101.1, True)

        pipeline_dir = run_root / "pipeline_work"
        pipeline_dir.mkdir(parents=True)
        (pipeline_dir / "label_contexts_full_refresh.ndjson").write_text(
            (run_root / "settlement_labels" / "settlement_labels.ndjson").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        rows = load_replay_inputs_from_jsonl(
            run_root / "candidate_snapshots" / "candidate_snapshots.ndjson",
            run_root / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        )
        metrics = materialize_rv600_metrics(rows)
        run_rows = evaluate_variant_specs(
            metrics,
            first_candidate_specs(),
            root_name=run_root.name,
            config=ReplayConfig(counterfactual_fill_threshold=0.5),
        )
        by_key = {(row.variant, row.accounting_mode): row for row in run_rows}
        single = by_key[("rv600_single_70_420_ev10", "all_entries")]
        repeated = by_key[("rv600_max2_refresh120_70_420_ev10", "all_entries")]
        one_per_side = by_key[("rv600_max2_refresh120_70_420_ev10", "one_per_side_per_market")]

        self.assertGreater(repeated.accepted_entries, single.accepted_entries)
        self.assertGreater(repeated.avg_added_entry_pnl_cents, 0.0)
        self.assertEqual(one_per_side.accepted_entries, single.accepted_entries)
        self.assertLess(repeated.matched_v28_control_pnl_cents, repeated.selected_pnl_cents)

        report = build_rv600_variation_report(
            [run_root],
            output_json=root / "reports" / "rv600.json",
            output_md=root / "reports" / "rv600.md",
        )
        self.assertEqual(report.root_count, 1)
        self.assertFalse(report.promotion_allowed)
        write_rv600_variation_report(report)
        self.assertIn("RV600 Variation Test Report", (root / "reports" / "rv600.md").read_text(encoding="utf-8"))

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = rv600_variation_test_main(
                [
                    "--root",
                    str(run_root),
                    "--output-json",
                    str(root / "reports" / "rv600_cli.json"),
                    "--output-md",
                    str(root / "reports" / "rv600_cli.md"),
                    "--write",
                ]
            )
        self.assertEqual(result, 0)
        self.assertIn("promotion_allowed=False", stdout.getvalue())
        self.assertTrue((root / "reports" / "rv600_cli.json").exists())

    def test_rv600_summary_blocks_repeated_entry_variants_with_negative_added_value(self) -> None:
        def row(
            variant: str,
            accounting_mode: str,
            *,
            accepted_entries: int,
            distinct_markets: int,
            selected_pnl_cents: float,
            avg_pnl_per_market_cents: float,
            added_entry_count: int = 0,
            added_entry_pnl_cents: float = 0.0,
            worst_market_pnl_cents: float = -10.0,
        ) -> RV600VariantRunRow:
            return RV600VariantRunRow(
                root_name="root-a",
                variant=variant,
                accounting_mode=accounting_mode,  # type: ignore[arg-type]
                gate_count=3,
                candidate_rows=100,
                accepted_entries=accepted_entries,
                distinct_markets=distinct_markets,
                entries_per_market_max=2 if added_entry_count else 1,
                entries_per_market_distribution={"1": distinct_markets},
                selected_pnl_cents=selected_pnl_cents,
                fill_adjusted_expected_pnl_cents=selected_pnl_cents,
                no_fill_penalty_pnl_cents=selected_pnl_cents,
                matched_v28_control_pnl_cents=0.0,
                matched_v28_delta_cents=selected_pnl_cents,
                avg_pnl_per_entry_cents=selected_pnl_cents / accepted_entries,
                avg_pnl_per_market_cents=avg_pnl_per_market_cents,
                win_count=accepted_entries,
                loss_count=0,
                positive_market_rate=1.0,
                max_single_market_pnl_share=0.20,
                last_window_pnl_cents=100.0,
                added_entry_count=added_entry_count,
                added_entry_pnl_cents=added_entry_pnl_cents,
                avg_added_entry_pnl_cents=(
                    added_entry_pnl_cents / added_entry_count if added_entry_count else 0.0
                ),
                worst_market_pnl_cents=worst_market_pnl_cents,
                root_pass=True,
                rejection_reason="",
            )

        summaries = _summarize(
            [
                row(
                    "rv600_primary_single_market_base_70_420_ev10",
                    "position_capped",
                    accepted_entries=25,
                    distinct_markets=25,
                    selected_pnl_cents=500.0,
                    avg_pnl_per_market_cents=20.0,
                ),
                row(
                    "rv600_primary_max_2_entries_base_70_420_ev10",
                    "position_capped",
                    accepted_entries=30,
                    distinct_markets=25,
                    selected_pnl_cents=600.0,
                    avg_pnl_per_market_cents=24.0,
                    added_entry_count=5,
                    added_entry_pnl_cents=-10.0,
                ),
            ]
        )
        repeated = next(
            item
            for item in summaries
            if item.variant == "rv600_primary_max_2_entries_base_70_420_ev10"
        )
        self.assertTrue(repeated.retrospective_gate_pass)
        self.assertFalse(repeated.repeated_entry_gate_pass)
        self.assertFalse(repeated.locked_candidate_eligible)
        self.assertIn("added_entries_nonpositive", repeated.rejection_reason)

    def test_rv600_sidecar_shadow_root_dedupes_model_rows(self) -> None:
        root = Path(tempfile.mkdtemp())
        pair_root = root / "sidecar_spot_pairs" / "run-a"
        pair_root.mkdir(parents=True)
        decision = "2026-05-13T11:09:00+00:00"
        enriched_row = {
            "market_ticker": "KXBTC15M-SIDECAR-15",
            "decision_ts_utc": decision,
            "market_close_ts_utc": "2026-05-13T11:15:00+00:00",
            "strike": "100.0",
            "independent_spot_ready": "True",
            "independent_spot_price": "100.8",
            "independent_spot_age_ms": "250.0",
            "btc_spot": "100.7",
            "yes_ask_cents": "45.0",
            "no_ask_cents": "57.0",
            "book_mid_yes_cents": "44.0",
            "v28_p_yes": "0.60",
            "candidate_p_yes": "0.55",
            "seconds_to_close": "360.0",
            "source_quality_tier": "native_predecision_sidecar_packet",
            "sidecar_spot_pair_run_id": "run-a",
            "source_file": "bundle-a.json",
        }
        duplicate_model_row = dict(enriched_row)
        duplicate_model_row["candidate_p_yes"] = "0.95"
        (pair_root / "sidecar_packets_independent_spot_enriched.json").write_text(
            json.dumps({"rows": [enriched_row, duplicate_model_row]}),
            encoding="utf-8",
        )
        (pair_root / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
            json.dumps(
                {
                    "diagnostic_rows": [
                        {
                            "market_ticker": "KXBTC15M-SIDECAR-15",
                            "decision_ts_utc": decision,
                            "y_yes_win": 1,
                        },
                        {
                            "market_ticker": "KXBTC15M-SIDECAR-15",
                            "decision_ts_utc": decision,
                            "y_yes_win": 1,
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )

        summary, candidate_rows, label_rows = build_sidecar_shadow_root(
            input_root=root / "sidecar_spot_pairs",
            output_root=root / "rv600_sidecar_root",
            min_decision_ts_utc=datetime(2026, 5, 13, 5, 37, 7, tzinfo=timezone.utc),
        )
        self.assertEqual(summary.candidate_rows_written, 1)
        self.assertEqual(summary.label_rows_written, 1)
        self.assertEqual(summary.duplicate_snapshot_rows_skipped, 1)
        self.assertEqual(candidate_rows[0]["snapshot"]["spot"], 100.8)
        self.assertEqual(candidate_rows[0]["extra"]["current_calibrated_p_yes"], 0.60)

        write_sidecar_shadow_root(summary, candidate_rows, label_rows)
        replay_rows = load_replay_inputs_from_jsonl(
            root / "rv600_sidecar_root" / "candidate_snapshots" / "candidate_snapshots.ndjson",
            root / "rv600_sidecar_root" / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        )
        self.assertEqual(len(replay_rows), 1)
        self.assertTrue(replay_rows[0].label.result_yes)

    def test_fixed_terminal_oos_blocks_same_sample_and_requires_locked_scope(self) -> None:
        root = Path(tempfile.mkdtemp())
        candidate_recorder = CandidateSnapshotRecorder(root)
        label_recorder = SettlementLabelRecorder(root)
        base_decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        for market_idx, result_yes in enumerate((True, False)):
            ticker = f"KXBTC15M-FIXEDOOS{market_idx}"
            ts = base_decision + timedelta(seconds=market_idx)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=100.8 if result_yes else 99.2,
                yes_ask_cents=45.0 if result_yes else 55.0,
                no_ask_cents=57.0 if result_yes else 47.0,
                fee_cents=1.0,
                fill_prob=1.0,
                yes_fill_prob=1.0,
                no_fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=ts + timedelta(minutes=15),
                label_available_ts_utc=ts + timedelta(minutes=16),
                settlement_price=101.0 if result_yes else 99.0,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="fixed_terminal_oos_unit",
                extra={
                    "particle_p_yes": 0.70 if result_yes else 0.30,
                    "brownian_p_yes": 0.60 if result_yes else 0.40,
                    "market_p_yes": 0.58 if result_yes else 0.42,
                    "current_calibrated_p_yes": 0.62 if result_yes else 0.38,
                },
            )
            label_recorder.record(label, source="fixed_terminal_oos_unit")
        candidates = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        labels = root / "settlement_labels" / "settlement_labels.ndjson"
        rows = load_replay_inputs_from_jsonl(candidates, labels)

        same_sample = evaluate_fixed_terminal_oos(rows)

        self.assertFalse(same_sample.gate_results.locked_oos_scope)
        self.assertFalse(same_sample.promotion_safe)
        self.assertEqual(same_sample.hypothesis_id, "gaussian_vol45_terminal_v1")

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = fixed_terminal_oos_main(
                [
                    "--candidates",
                    str(candidates),
                    "--labels",
                    str(labels),
                    "--output-dir",
                    str(root / "fixed_reports"),
                    "--stem",
                    "fixed_terminal",
                    "--evaluation-scope",
                    "locked_oos_shadow",
                    "--gate-min-candidates",
                    "1",
                    "--gate-min-markets",
                    "1",
                    "--gate-min-selected",
                    "1",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads((root / "fixed_reports" / "fixed_terminal.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["hypothesis_id"], "gaussian_vol45_terminal_v1")
        self.assertIn("promotion_safe=", stdout.getvalue())
        self.assertIn("Fixed Terminal OOS Report", (root / "fixed_reports" / "fixed_terminal.md").read_text(encoding="utf-8"))

    def test_fixed_terminal_locked_oos_plan_writes_predeclared_command_manifest(self) -> None:
        root = Path(tempfile.mkdtemp())

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            exit_code = fixed_terminal_locked_oos_plan_main(
                [
                    "--hypothesis-id",
                    "gaussian_vol45_terminal_v1",
                    "--run-id",
                    "UNITFIXEDLOCK",
                    "--dataset",
                    "particle_fixed_terminal_oos_unit",
                    "--artifact-root",
                    str(root / "artifacts"),
                    "--output-dir",
                    str(root / "plans"),
                    "--stem",
                    "fixed_terminal_locked_plan",
                    "--run-seconds",
                    "3900",
                    "--gate-min-candidates",
                    "1000",
                    "--gate-min-markets",
                    "5",
                    "--gate-min-selected",
                    "250",
                ]
            )

        payload = json.loads((root / "plans" / "fixed_terminal_locked_plan.json").read_text(encoding="utf-8"))
        md = (root / "plans" / "fixed_terminal_locked_plan.md").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hypothesis_id"], "gaussian_vol45_terminal_v1")
        self.assertEqual(payload["evaluation_scope"], "locked_oos_shadow")
        self.assertEqual(payload["baseline_pipeline_annualized_vol"], 0.65)
        self.assertEqual(payload["fixed_terminal_annualized_vol"], 0.45)
        self.assertEqual(payload["gate_config"]["min_market_count"], 5)
        self.assertIn("--record-independent-spot", payload["paired_capture_command"])
        self.assertIn("--require-independent-spot", payload["paired_capture_command"])
        self.assertIn("passive_contexts_independent_spot.ndjson", payload["pipeline_command"])
        self.assertIn("--annualized-vol 0.65", payload["pipeline_command"])
        self.assertIn("research_particle.fixed_terminal_oos", payload["fixed_terminal_oos_command"])
        self.assertIn("--hypothesis-id gaussian_vol45_terminal_v1", payload["fixed_terminal_oos_command"])
        self.assertIn("--evaluation-scope locked_oos_shadow", payload["fixed_terminal_oos_command"])
        self.assertIn("baseline pipeline remains at annualized vol 0.65", md)
        self.assertIn("json_plan=", stdout.getvalue())

    def test_particle_goal_audit_separates_synthetic_from_real_promotion(self) -> None:
        synthetic = {
            "candidate_count": 4,
            "particle_beats_brownian": True,
            "particle_beats_market": True,
            "particle_beats_current_calibrated": True,
            "total_counterfactual_pnl_cents": 141.0,
        }
        real_fail = dict(synthetic)
        real_fail["ev_rank_correlation_sign"] = -0.1
        real_pass = dict(synthetic)
        real_pass["ev_rank_correlation_sign"] = 0.2
        real_pass["top_ev_bucket_pnl_cents"] = 10.0

        self.assertTrue(_synthetic_report_passes(synthetic))
        self.assertFalse(_real_report_clears_promotion(real_fail))
        self.assertTrue(_real_report_clears_promotion(real_pass))

    def test_particle_goal_audit_counts_nested_real_replay_reports(self) -> None:
        root = Path(tempfile.mkdtemp())
        report_dir = root / "logs" / "particle_research" / "real_shadow" / "run1" / "reports"
        report_dir.mkdir(parents=True)
        (report_dir / "passive_particle_replay.json").write_text(
            json.dumps(
                {
                    "candidate_count": 2,
                    "particle_beats_brownian": True,
                    "particle_beats_market": False,
                    "particle_beats_current_calibrated": False,
                    "ev_rank_correlation_sign": 0.1,
                    "top_ev_bucket_pnl_cents": -1.0,
                    "total_counterfactual_pnl_cents": -2.0,
                }
            ),
            encoding="utf-8",
        )
        candidate_dir = root / "logs" / "particle_research" / "real_shadow" / "run1" / "candidate_snapshots"
        candidate_dir.mkdir(parents=True)
        (candidate_dir / "candidate_snapshots.ndjson").write_text("{}\n{}\n", encoding="utf-8")

        payload = particle_goal_audit(root)

        self.assertEqual(len(payload["real_replay_reports"]), 1)
        self.assertEqual(payload["strict_real_candidate_rows"], 2)
        self.assertFalse(payload["complete"])

    def test_artifact_leakage_audit_verifies_real_candidate_label_timing(self) -> None:
        root = Path(tempfile.mkdtemp())
        run_ok = root / "run_ok"
        decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        CandidateSnapshotRecorder(run_ok).record(
            CandidateSnapshot(
                market_ticker="KXBTC15M-ARTIFACTOK",
                decision_ts_utc=decision,
                recv_ts_utc=decision,
                strike=100.0,
                spot=101.0,
                yes_ask_cents=45.0,
                no_ask_cents=57.0,
                fee_cents=1.0,
                fill_prob=1.0,
            ),
            decision_shadow="candidate",
            reason="artifact_audit_unit",
            extra={
                "particle_p_yes": 0.70,
                "brownian_p_yes": 0.62,
                "market_p_yes": 0.58,
                "current_calibrated_p_yes": 0.64,
                "independent_spot_available_ts_utc": (decision - timedelta(seconds=1)).isoformat(),
            },
        )
        SettlementLabelRecorder(run_ok).record(
            SettlementLabel(
                market_ticker="KXBTC15M-ARTIFACTOK",
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision + timedelta(minutes=16),
                settlement_price=101.0,
                strike=100.0,
            ),
            source="artifact_audit_unit",
        )

        ok_report = build_artifact_leakage_audit([run_ok])

        self.assertTrue(ok_report.pass_no_future_leakage)
        self.assertEqual(ok_report.issue_count, 0)

        run_leak = root / "run_leak"
        CandidateSnapshotRecorder(run_leak).record(
            CandidateSnapshot(
                market_ticker="KXBTC15M-ARTIFACTLEAK",
                decision_ts_utc=decision,
                recv_ts_utc=decision + timedelta(seconds=1),
                strike=100.0,
                spot=101.0,
                yes_ask_cents=45.0,
                no_ask_cents=57.0,
                fee_cents=1.0,
                fill_prob=1.0,
            ),
            decision_shadow="candidate",
            reason="artifact_audit_unit",
            extra={
                "particle_p_yes": 0.70,
                "brownian_p_yes": 0.62,
                "market_p_yes": 0.58,
                "current_calibrated_p_yes": 0.64,
                "independent_spot_available_ts_utc": (decision + timedelta(seconds=2)).isoformat(),
            },
        )
        SettlementLabelRecorder(run_leak).record(
            SettlementLabel(
                market_ticker="KXBTC15M-ARTIFACTLEAK",
                settlement_ts_utc=decision + timedelta(minutes=15),
                label_available_ts_utc=decision,
                settlement_price=101.0,
                strike=100.0,
            ),
            source="artifact_audit_unit",
        )

        leak_report = build_artifact_leakage_audit([run_ok, run_leak])

        self.assertFalse(leak_report.pass_no_future_leakage)
        self.assertEqual(leak_report.issue_count, 3)
        leak_row = next(row for row in leak_report.run_rows if row.run == "run_leak")
        self.assertEqual(leak_row.candidate_recv_after_decision_count, 1)
        self.assertEqual(leak_row.label_available_at_or_before_decision_count, 1)
        self.assertEqual(leak_row.future_extra_timestamp_count, 1)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = artifact_leakage_audit_main(
                [
                    "--run-root",
                    str(run_ok),
                    "--output-dir",
                    str(root / "reports"),
                    "--stem",
                    "artifact_leakage",
                ]
            )
        payload = json.loads((root / "reports" / "artifact_leakage.json").read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertTrue(payload["pass_no_future_leakage"])
        self.assertIn("pass_no_future_leakage=True", stdout.getvalue())
        self.assertIn("Artifact Leakage Audit", (root / "reports" / "artifact_leakage.md").read_text(encoding="utf-8"))

    def test_denominator_integrity_audit_matches_candidates_reports_and_labels(self) -> None:
        root = Path(tempfile.mkdtemp())
        run_ok = root / "run_ok"
        decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
        candidate_recorder = CandidateSnapshotRecorder(run_ok)
        label_recorder = SettlementLabelRecorder(run_ok)
        replay_rows = []
        for idx, result_yes in enumerate((True, False)):
            ticker = f"KXBTC15M-DENOM{idx}"
            ts = decision + timedelta(seconds=idx)
            snapshot = CandidateSnapshot(
                market_ticker=ticker,
                decision_ts_utc=ts,
                recv_ts_utc=ts,
                strike=100.0,
                spot=101.0 if result_yes else 99.0,
                yes_ask_cents=45.0 if result_yes else 55.0,
                no_ask_cents=57.0 if result_yes else 47.0,
                fee_cents=1.0,
                fill_prob=1.0,
            )
            label = SettlementLabel(
                market_ticker=ticker,
                settlement_ts_utc=ts + timedelta(minutes=15),
                label_available_ts_utc=ts + timedelta(minutes=16),
                settlement_price=101.0 if result_yes else 99.0,
                strike=100.0,
            )
            candidate_recorder.record(
                snapshot,
                decision_shadow="candidate",
                reason="denominator_unit",
                extra={
                    "particle_p_yes": 0.70 if result_yes else 0.30,
                    "brownian_p_yes": 0.62 if result_yes else 0.38,
                    "market_p_yes": 0.58 if result_yes else 0.42,
                    "current_calibrated_p_yes": 0.64 if result_yes else 0.36,
                },
            )
            label_recorder.record(label, source="denominator_unit")
            replay_rows.append(
                ReplayInput(
                    snapshot=snapshot,
                    label=label,
                    particle_p_yes=0.70 if result_yes else 0.30,
                    brownian_p_yes=0.62 if result_yes else 0.38,
                    market_p_yes=0.58 if result_yes else 0.42,
                    current_calibrated_p_yes=0.64 if result_yes else 0.36,
                )
            )
        report = evaluate_replay(replay_rows)
        write_replay_report(
            report,
            run_ok / "reports",
            "passive_particle_replay_locked_oos",
        )

        ok_audit = build_denominator_integrity_audit([run_ok])

        self.assertTrue(ok_audit.pass_denominator_integrity)
        self.assertEqual(ok_audit.issue_count, 0)
        self.assertEqual(ok_audit.candidate_count, 2)

        run_bad = root / "run_bad"
        run_bad_candidates = run_bad / "candidate_snapshots"
        run_bad_labels = run_bad / "pipeline_work"
        run_bad_reports = run_bad / "reports"
        run_bad_candidates.mkdir(parents=True)
        run_bad_labels.mkdir(parents=True)
        run_bad_reports.mkdir(parents=True)
        (run_bad_candidates / "candidate_snapshots.ndjson").write_text(
            (run_ok / "candidate_snapshots" / "candidate_snapshots.ndjson").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (run_bad_labels / "label_contexts_full_refresh.ndjson").write_text(
            (run_ok / "settlement_labels" / "settlement_labels.ndjson").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        bad_payload = json.loads((run_ok / "reports" / "passive_particle_replay_locked_oos.json").read_text(encoding="utf-8"))
        bad_payload["candidate_count"] = 1
        bad_payload["source_candidate_count"] = 2
        bad_payload["skipped_unlabeled_count"] = 1
        bad_payload["denominator_scope"] = "resolved_labeled_subset"
        (run_bad_reports / "passive_particle_replay_locked_oos.json").write_text(
            json.dumps(bad_payload),
            encoding="utf-8",
        )

        bad_audit = build_denominator_integrity_audit([run_bad])

        self.assertFalse(bad_audit.pass_denominator_integrity)
        self.assertGreater(bad_audit.issue_count, 0)
        self.assertTrue(bad_audit.run_rows[0].count_mismatch)

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = denominator_integrity_audit_main(
                [
                    "--run-root",
                    str(run_ok),
                    "--output-dir",
                    str(root / "denom_reports"),
                    "--stem",
                    "denominator_integrity",
                ]
            )
        payload = json.loads((root / "denom_reports" / "denominator_integrity.json").read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertTrue(payload["pass_denominator_integrity"])
        self.assertIn("pass_denominator_integrity=True", stdout.getvalue())
        self.assertIn(
            "Denominator Integrity Audit",
            (root / "denom_reports" / "denominator_integrity.md").read_text(encoding="utf-8"),
        )

    def test_particle_goal_audit_uses_locked_stability_as_real_evidence(self) -> None:
        root = Path(tempfile.mkdtemp())
        report_dir = root / "logs" / "particle_research" / "reports"
        report_dir.mkdir(parents=True)
        (report_dir / "locked_oos_stability_latest.json").write_text(
            json.dumps(
                {
                    "stability_rows": [
                        {
                            "source": "dynamic",
                            "name": "rolling_vol_600s",
                            "total_counterfactual_pnl_cents": 10.0,
                            "stable_all_runs": False,
                        }
                    ],
                    "stable_candidate_count": 0,
                    "best_by_total_pnl": {
                        "source": "dynamic",
                        "name": "rolling_vol_600s",
                        "total_counterfactual_pnl_cents": 10.0,
                    },
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "artifact_leakage_audit_latest.json").write_text(
            json.dumps(
                {
                    "pass_no_future_leakage": True,
                    "run_count": 2,
                    "candidate_count": 100,
                    "issue_count": 0,
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "denominator_integrity_audit_latest.json").write_text(
            json.dumps(
                {
                    "pass_denominator_integrity": True,
                    "run_count": 2,
                    "candidate_count": 100,
                    "market_count": 10,
                    "issue_count": 0,
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "fixed_terminal_gauss45_stability_current.json").write_text(
            json.dumps(
                {
                    "run_count": 1,
                    "stable_candidate_count": 0,
                    "stability_rows": [
                        {
                            "source": "fixed_terminal",
                            "name": "gaussian_vol45_terminal_v1",
                            "run_count": 1,
                            "total_counterfactual_pnl_cents": 47.0,
                            "beats_brownian_run_count": 0,
                            "beats_current_run_count": 1,
                            "stable_all_runs": False,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "online_anchor_calibration_diagnostic_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "summary_rows": [
                        {
                            "spec": "online_logit_brownian_lr003_row",
                            "run_count": 2,
                            "strict_gate_count": 0,
                            "beats_raw_count": 1,
                            "beats_brownian_count": 1,
                            "beats_market_count": 1,
                            "beats_current_count": 1,
                            "total_counterfactual_pnl_cents": 12.0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "anchor_regime_profile_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "run_best_counts_by_brier": {
                        "brownian": 1,
                        "current_calibrated": 1,
                        "market": 0,
                        "particle": 0,
                    },
                    "market_best_counts_by_brier": {
                        "brownian": 2,
                        "current_calibrated": 1,
                        "market": 1,
                        "particle": 0,
                    },
                    "state_bucket_best_counts_by_brier": {
                        "brownian": 1,
                        "current_calibrated": 1,
                        "market": 1,
                        "particle": 0,
                    },
                    "conclusion": "No single timestamp-available anchor dominates all locked runs by Brier.",
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "spot_realized_vol_terminal_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "spec": "rv233_blend50_fixed65",
                            "run_count": 2,
                            "strict_gate_count": 0,
                            "beats_brownian_count": 1,
                            "beats_current_count": 1,
                            "total_counterfactual_pnl_cents": 20.0,
                            "mean_brier": 0.21,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "anchor_switch_loro_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "summary_rows": [
                        {
                            "spec": "time_moneyness",
                            "holdout_count": 2,
                            "strict_gate_count": 0,
                            "beats_current_count": 1,
                            "beats_market_count": 1,
                            "total_counterfactual_pnl_cents": 10.0,
                            "mean_brier": 0.22,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "spot_rv_anchor_switch_loro_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "spec": "time_rv_disagreement",
                            "holdout_count": 2,
                            "strict_gate_count": 0,
                            "beats_current_count": 1,
                            "beats_market_count": 1,
                            "total_counterfactual_pnl_cents": 30.0,
                            "mean_brier": 0.20,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "spot_rv_current_residual_loro_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "spec": "time_rv_disagreement",
                            "holdout_count": 2,
                            "strict_gate_count": 0,
                            "beats_current_count": 1,
                            "beats_market_count": 1,
                            "positive_market_ev_rank_count": 1,
                            "positive_market_top_bucket_count": 1,
                            "total_counterfactual_pnl_cents": 25.0,
                            "mean_brier": 0.19,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "spot_drift_terminal_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "spec": "drift13_cap10_fixed65_blend25",
                            "run_count": 2,
                            "strict_gate_count": 0,
                            "beats_current_count": 1,
                            "beats_market_count": 1,
                            "positive_market_ev_rank_count": 1,
                            "positive_market_top_bucket_count": 1,
                            "total_counterfactual_pnl_cents": 40.0,
                            "mean_brier": 0.18,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "empirical_next_second_particle_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "spec": "emp1s_610_center_blend50_p96_d48",
                            "run_count": 2,
                            "strict_gate_count": 0,
                            "beats_current_count": 1,
                            "beats_market_count": 1,
                            "positive_market_ev_rank_count": 1,
                            "positive_market_top_bucket_count": 1,
                            "total_counterfactual_pnl_cents": 50.0,
                            "mean_brier": 0.19,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "empirical_current_anchor_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "spec": "current_emp610_w25_center",
                            "run_count": 2,
                            "strict_gate_count": 0,
                            "beats_current_count": 1,
                            "positive_ev_rank_count": 1,
                            "positive_market_ev_rank_count": 1,
                            "total_counterfactual_pnl_cents": -15.0,
                            "mean_brier": 0.18,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "empirical_market_opportunity_diagnostic_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "summary_rows": [
                        {
                            "family": "empirical",
                            "spec": "emp1s_610_center_blend50_p96_d48",
                            "run_count": 2,
                            "market_count": 10,
                            "strict_gate_count": 0,
                            "positive_pnl_count": 2,
                            "beats_current_count": 1,
                            "positive_top_bucket_count": 1,
                            "total_counterfactual_pnl_cents": 20.0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "empirical_market_opportunity_loro_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "source_run_count": 2,
                    "source_opportunity_row_count": 10,
                    "summary_rows": [
                        {
                            "selector": "train_strict_ev_bucket_score",
                            "holdout_count": 2,
                            "strict_gate_holdout_count": 0,
                            "positive_pnl_holdout_count": 1,
                            "beats_current_holdout_count": 1,
                            "positive_ev_rank_holdout_count": 1,
                            "positive_top_bucket_holdout_count": 1,
                            "total_holdout_pnl_cents": 12.0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "spot_drift_regime_latest.json").write_text(
            json.dumps(
                {
                    "promotion_safe": False,
                    "candidate_ready_for_predeclared_shadow": False,
                    "run_inputs": [{"name": "run1"}, {"name": "run2"}],
                    "skipped_run_roots": ["run3"],
                    "stable_positive_rules": [],
                    "rule_summary_rows": [
                        {
                            "spec": "drift13_cap10_fixed65_blend25",
                            "rule": "require_abs_drift_ge_1bps",
                            "run_count": 2,
                            "positive_run_count": 1,
                            "nonzero_run_count": 2,
                            "selected_count": 100,
                            "total_counterfactual_pnl_cents": 30.0,
                            "min_run_pnl_cents": -7.0,
                            "stable_positive": False,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "paired_sidecar_spot_aggregate_latest.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "diagnostic_ready": True,
                        "promotion_allowed": False,
                        "candidate_ready_for_predeclared_shadow": False,
                        "diagnostic_file_count": 2,
                        "ready_diagnostic_count": 2,
                        "joined_rows": 28,
                        "joined_markets": 2,
                        "rows_remaining_for_shadow": 172,
                        "markets_remaining_for_shadow": 38,
                        "best_model_by_brier": "v28",
                        "best_model_by_logloss": "v28",
                        "tick_brownian_delta_brier_vs_candle": -0.00105,
                        "tick_brownian_delta_logloss_vs_candle": -0.00482,
                    }
                }
            ),
            encoding="utf-8",
        )
        (report_dir / "paired_sidecar_spot_refresh_latest.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "promotion_allowed": False,
                        "manifest_count": 5,
                        "skipped_manifest_count": 1,
                        "enrichment_ready_count": 4,
                        "diagnostic_ready_count": 4,
                        "pending_diagnostic_count": 0,
                        "aggregate_ready": True,
                        "aggregate_fresh": True,
                        "aggregate_joined_rows": 56,
                        "aggregate_joined_markets": 3,
                        "aggregate_rows_remaining_for_shadow": 144,
                        "aggregate_markets_remaining_for_shadow": 37,
                        "goal_complete": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        paired_dir = root / "logs" / "particle_research" / "real_shadow" / "sidecar_spot_pairs" / "unit"
        paired_dir.mkdir(parents=True)
        (paired_dir / "paired_sidecar_spot_manifest.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "paired_capture_ready": True,
                        "promotion_allowed": False,
                        "collect_mode": "public-rest",
                        "sidecar_markets_selected": 1,
                        "sidecar_packet_rows": 14,
                        "spot_ticks_written": 10,
                        "alignment_ready_count": 1,
                        "alignment_row_count": 1,
                    }
                }
            ),
            encoding="utf-8",
        )
        (paired_dir / "sidecar_packets_independent_spot_enriched.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "enrichment_ready": True,
                        "promotion_allowed": False,
                        "matching_packet_rows": 14,
                        "enriched_packet_rows": 14,
                        "issue_count": 0,
                    }
                }
            ),
            encoding="utf-8",
        )
        (paired_dir / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "diagnostic_ready": True,
                        "promotion_allowed": False,
                        "candidate_ready_for_predeclared_shadow": False,
                        "joined_rows": 14,
                        "joined_markets": 1,
                        "best_model_by_brier": "v28",
                        "best_model_by_logloss": "v28",
                        "tick_brownian_delta_brier_vs_candle": -0.0017,
                        "tick_brownian_delta_logloss_vs_candle": -0.006,
                    }
                }
            ),
            encoding="utf-8",
        )
        paired_dir_2 = root / "logs" / "particle_research" / "real_shadow" / "sidecar_spot_pairs" / "unit2"
        paired_dir_2.mkdir(parents=True)
        (paired_dir_2 / "sidecar_spot_tick_vs_candle_diagnostic.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "diagnostic_ready": True,
                        "promotion_allowed": False,
                        "candidate_ready_for_predeclared_shadow": False,
                        "joined_rows": 14,
                        "joined_markets": 1,
                        "best_model_by_brier": "v28",
                        "best_model_by_logloss": "v28",
                        "tick_brownian_delta_brier_vs_candle": -0.0017,
                        "tick_brownian_delta_logloss_vs_candle": -0.006,
                    }
                }
            ),
            encoding="utf-8",
        )

        payload = particle_goal_audit(root)
        probability_item = next(
            item for item in payload["checklist"]
            if item["requirement"].startswith("Particle probabilities")
        )
        strict_item = next(
            item for item in payload["checklist"]
            if item["requirement"].startswith("Strict replay")
        )
        denominator_item = next(
            item for item in payload["checklist"]
            if item["requirement"].startswith("All-candidate denominator")
        )
        recorder_item = next(
            item for item in payload["checklist"]
            if item["requirement"].startswith("Trustworthy all-candidate")
        )
        live_item = next(
            item for item in payload["checklist"]
            if item["requirement"].startswith("Live trading remains untouched")
        )

        self.assertEqual(payload["locked_oos_stability_rows"], 1)
        self.assertEqual(payload["locked_oos_stable_candidate_count"], 0)
        self.assertTrue(payload["paired_sidecar_spot_paired_capture_ready"])
        self.assertFalse(payload["paired_sidecar_spot_promotion_allowed"])
        self.assertEqual(payload["paired_sidecar_spot_alignment_ready_count"], 1)
        self.assertEqual(payload["paired_sidecar_spot_ticks_written"], 10)
        self.assertTrue(payload["paired_sidecar_spot_enrichment_ready"])
        self.assertFalse(payload["paired_sidecar_spot_enrichment_promotion_allowed"])
        self.assertEqual(payload["paired_sidecar_spot_enriched_packet_rows"], 14)
        self.assertEqual(payload["paired_sidecar_spot_enrichment_issue_count"], 0)
        self.assertTrue(payload["paired_sidecar_spot_diagnostic_ready"])
        self.assertFalse(payload["paired_sidecar_spot_diagnostic_promotion_allowed"])
        self.assertFalse(payload["paired_sidecar_spot_diagnostic_candidate_ready"])
        self.assertEqual(payload["paired_sidecar_spot_diagnostic_joined_rows"], 14)
        self.assertEqual(payload["paired_sidecar_spot_diagnostic_joined_markets"], 1)
        self.assertEqual(payload["paired_sidecar_spot_diagnostic_best_model_by_brier"], "v28")
        self.assertEqual(payload["paired_sidecar_spot_diagnostic_best_model_by_logloss"], "v28")
        self.assertLess(payload["paired_sidecar_spot_diagnostic_tick_delta_brier_vs_candle"], 0.0)
        self.assertLess(payload["paired_sidecar_spot_diagnostic_tick_delta_logloss_vs_candle"], 0.0)
        self.assertTrue(payload["paired_sidecar_spot_aggregate_ready"])
        self.assertFalse(payload["paired_sidecar_spot_aggregate_promotion_allowed"])
        self.assertFalse(payload["paired_sidecar_spot_aggregate_candidate_ready"])
        self.assertEqual(payload["paired_sidecar_spot_aggregate_diagnostic_file_count"], 2)
        self.assertEqual(payload["paired_sidecar_spot_actual_diagnostic_file_count"], 2)
        self.assertTrue(payload["paired_sidecar_spot_aggregate_fresh"])
        self.assertEqual(payload["paired_sidecar_spot_aggregate_stale_file_delta"], 0)
        self.assertEqual(payload["paired_sidecar_spot_aggregate_ready_diagnostic_count"], 2)
        self.assertEqual(payload["paired_sidecar_spot_aggregate_joined_rows"], 28)
        self.assertEqual(payload["paired_sidecar_spot_aggregate_joined_markets"], 2)
        self.assertEqual(payload["paired_sidecar_spot_aggregate_rows_remaining_for_shadow"], 172)
        self.assertEqual(payload["paired_sidecar_spot_aggregate_markets_remaining_for_shadow"], 38)
        self.assertEqual(payload["paired_sidecar_spot_aggregate_best_model_by_brier"], "v28")
        self.assertEqual(payload["paired_sidecar_spot_aggregate_best_model_by_logloss"], "v28")
        self.assertLess(payload["paired_sidecar_spot_aggregate_tick_delta_brier_vs_candle"], 0.0)
        self.assertLess(payload["paired_sidecar_spot_aggregate_tick_delta_logloss_vs_candle"], 0.0)
        self.assertFalse(payload["paired_sidecar_spot_refresh_promotion_allowed"])
        self.assertEqual(payload["paired_sidecar_spot_refresh_manifest_count"], 5)
        self.assertEqual(payload["paired_sidecar_spot_refresh_skipped_manifest_count"], 1)
        self.assertEqual(payload["paired_sidecar_spot_refresh_enrichment_ready_count"], 4)
        self.assertEqual(payload["paired_sidecar_spot_refresh_diagnostic_ready_count"], 4)
        self.assertEqual(payload["paired_sidecar_spot_refresh_pending_diagnostic_count"], 0)
        self.assertFalse(payload["paired_sidecar_spot_refresh_goal_complete"])
        self.assertTrue(payload["artifact_leakage_audit_pass"])
        self.assertEqual(payload["artifact_leakage_audit_issue_count"], 0)
        self.assertTrue(payload["denominator_integrity_audit_pass"])
        self.assertEqual(payload["denominator_integrity_audit_issue_count"], 0)
        self.assertEqual(strict_item["status"], "pass")
        self.assertIn("pass_no_future_leakage=True", strict_item["detail"])
        self.assertEqual(denominator_item["status"], "pass")
        self.assertEqual(recorder_item["status"], "pass")
        self.assertEqual(live_item["status"], "pass")
        self.assertIn("paired_sidecar_spot", recorder_item["detail"])
        self.assertIn("paired_sidecar_spot_enrichment", recorder_item["detail"])
        self.assertIn("paired_sidecar_spot_diagnostic", recorder_item["detail"])
        self.assertIn("paired_sidecar_spot_aggregate", recorder_item["detail"])
        self.assertIn("paired_sidecar_spot_refresh", recorder_item["detail"])
        self.assertIn("promotion_allowed=False", live_item["detail"])
        self.assertIn("candidate_ready=False", live_item["detail"])
        self.assertIn("pass_denominator_integrity=True", denominator_item["detail"])
        self.assertEqual(probability_item["status"], "fail")
        self.assertIn("stable_candidate_count=0", probability_item["detail"])
        self.assertIn("paired_sidecar_spot_diagnostic", probability_item["detail"])
        self.assertIn("tick_delta_brier_vs_candle=-0.0017", probability_item["detail"])
        self.assertIn("paired_sidecar_spot_aggregate", probability_item["detail"])
        self.assertIn("diagnostic_files=2/2", probability_item["detail"])
        self.assertIn("fresh=True", probability_item["detail"])
        self.assertIn("markets_remaining=38", probability_item["detail"])
        self.assertIn("paired_sidecar_spot_refresh", probability_item["detail"])
        self.assertIn("skipped=1", probability_item["detail"])
        self.assertEqual(payload["fixed_terminal_gauss45_stability_stable_candidate_count"], 0)
        self.assertIn("fixed_terminal_gauss45_stability", probability_item["detail"])
        self.assertFalse(payload["online_anchor_calibration_promotion_safe"])
        self.assertIn("online_anchor_calibration", probability_item["detail"])
        self.assertFalse(payload["anchor_regime_profile_promotion_safe"])
        self.assertIn("anchor_regime_profile", probability_item["detail"])
        self.assertFalse(payload["spot_realized_vol_terminal_promotion_safe"])
        self.assertIn("spot_realized_vol_terminal", probability_item["detail"])
        self.assertFalse(payload["anchor_switch_loro_promotion_safe"])
        self.assertIn("anchor_switch_loro", probability_item["detail"])
        self.assertFalse(payload["spot_rv_anchor_switch_loro_promotion_safe"])
        self.assertFalse(payload["spot_rv_anchor_switch_loro_candidate_ready"])
        self.assertIn("spot_rv_anchor_switch_loro", probability_item["detail"])
        self.assertFalse(payload["spot_rv_current_residual_loro_promotion_safe"])
        self.assertFalse(payload["spot_rv_current_residual_loro_candidate_ready"])
        self.assertIn("spot_rv_current_residual_loro", probability_item["detail"])
        self.assertFalse(payload["empirical_current_anchor_promotion_safe"])
        self.assertFalse(payload["empirical_current_anchor_candidate_ready"])
        self.assertIn("empirical_current_anchor", probability_item["detail"])
        self.assertFalse(payload["empirical_market_opportunity_promotion_safe"])
        self.assertFalse(payload["empirical_market_opportunity_candidate_ready"])
        self.assertIn("empirical_market_opportunity", probability_item["detail"])
        self.assertFalse(payload["empirical_market_opportunity_loro_promotion_safe"])
        self.assertFalse(payload["empirical_market_opportunity_loro_candidate_ready"])
        self.assertIn("empirical_market_opportunity_loro", probability_item["detail"])
        self.assertFalse(payload["empirical_next_second_particle_promotion_safe"])
        self.assertFalse(payload["empirical_next_second_particle_candidate_ready"])
        self.assertIn("empirical_next_second_particle", probability_item["detail"])
        self.assertFalse(payload["spot_drift_terminal_promotion_safe"])
        self.assertFalse(payload["spot_drift_terminal_candidate_ready"])
        self.assertIn("spot_drift_terminal", probability_item["detail"])
        self.assertFalse(payload["spot_drift_regime_promotion_safe"])
        self.assertFalse(payload["spot_drift_regime_candidate_ready"])
        self.assertIn("spot_drift_regime", probability_item["detail"])

    def test_shadow_run_preflight_reports_missing_and_ready_states(self) -> None:
        root = Path(tempfile.mkdtemp())
        dataset = "particle_shadow_test"
        artifact_root = root / "logs" / "particle_research" / "real_shadow" / dataset
        context_path = artifact_root / "passive_contexts.ndjson"
        market_results_path = artifact_root / "market_results.json"

        missing = build_preflight(
            dataset=dataset,
            artifact_root=artifact_root,
            context_path=context_path,
            market_results_path=market_results_path,
            workspace=root,
        )
        self.assertFalse(missing.ready_to_collect)
        self.assertFalse(missing.ready_to_pipeline)
        self.assertEqual(missing.checkpoint_row_count, 0)
        self.assertFalse(missing.context_tailer_exists)
        self.assertFalse(missing.paired_runner_exists)

        key_path = root / "secrets" / "kalshi.pem"
        key_path.parent.mkdir(parents=True)
        key_path.write_text("placeholder", encoding="utf-8")
        (root / ".env").write_text(
            "KALSHI_API_KEY_ID=test-key\n"
            "KALSHI_PRIVATE_KEY_PATH=secrets/kalshi.pem\n",
            encoding="utf-8",
        )
        (root / "research_native_passive_ws_recorder.py").write_text("# placeholder\n", encoding="utf-8")
        tailer_path = root / "research_particle" / "v28_context_tailer.py"
        tailer_path.parent.mkdir(parents=True)
        tailer_path.write_text("# placeholder\n", encoding="utf-8")
        (root / "research_particle" / "paired_passive_shadow_run.py").write_text(
            "# placeholder\n",
            encoding="utf-8",
        )
        checkpoint_dir = root / "research_data" / dataset / "book_checkpoints"
        checkpoint_dir.mkdir(parents=True)
        (checkpoint_dir / "part.ndjson").write_text(
            json.dumps({"market_ticker": "KXBTC15M-PREFLIGHT"}) + "\n",
            encoding="utf-8",
        )
        artifact_root.mkdir(parents=True)
        context_path.write_text(json.dumps({"market_ticker": "KXBTC15M-PREFLIGHT"}) + "\n", encoding="utf-8")
        market_results_path.write_text(
            json.dumps([{"market": "KXBTC15M-PREFLIGHT", "result": "yes"}]),
            encoding="utf-8",
        )

        ready = build_preflight(
            dataset=dataset,
            artifact_root=artifact_root,
            context_path=context_path,
            market_results_path=market_results_path,
            workspace=root,
        )
        self.assertTrue(ready.ready_to_collect)
        self.assertTrue(ready.ready_to_pipeline)
        self.assertIn("research_native_passive_ws_recorder.py", ready.recorder_command)
        self.assertTrue(ready.context_tailer_exists)
        self.assertTrue(ready.paired_runner_exists)
        self.assertIn("research_particle.v28_context_tailer", ready.context_tailer_command)
        self.assertIn("research_particle.paired_passive_shadow_run", ready.paired_run_command)
        self.assertIn("--record-independent-spot", ready.paired_run_command)
        json_path, md_path = write_preflight(ready, output_dir=root / "reports")
        self.assertTrue(json_path.exists())
        self.assertIn("ready_to_pipeline", md_path.read_text(encoding="utf-8"))

    def test_paired_passive_shadow_parser_exposes_bounded_research_run(self) -> None:
        parser = paired_passive_parser()

        args = parser.parse_args(
            [
                "--run-seconds",
                "30",
                "--checkpoint-interval-seconds",
                "1",
                "--checkpoint-depth",
                "5",
                "--include-existing-context",
                "--record-independent-spot",
                "--independent-spot-feed",
                "coinbase",
                "--independent-spot-max-age-ms",
                "2500",
                "--require-independent-spot",
            ]
        )

        self.assertEqual(args.run_seconds, 30.0)
        self.assertEqual(args.checkpoint_interval_seconds, 1.0)
        self.assertEqual(args.checkpoint_depth, 5)
        self.assertTrue(args.include_existing_context)
        self.assertTrue(args.record_independent_spot)
        self.assertEqual(args.independent_spot_feed, "coinbase")
        self.assertEqual(args.independent_spot_max_age_ms, 2500.0)
        self.assertTrue(args.require_independent_spot)

    def test_candidate_context_builder_refuses_late_receive_time(self) -> None:
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        raw = {
            "market_ticker": "KXBTC15M-LATECTX",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": (decision + timedelta(milliseconds=1)).isoformat(),
            "seconds_to_close": 600,
            "strike": 100.0,
            "spot": 100.2,
            "yes_ask_cents": 58,
            "no_ask_cents": 44,
            "fee_cents": 1.0,
            "fill_prob": 0.75,
            "current_calibrated_p_yes": 0.62,
        }

        with self.assertRaises(CandidateContextError):
            build_candidate_context(raw)

    def test_candidate_context_cli_normalizes_and_reports_issues(self) -> None:
        root = Path(tempfile.mkdtemp())
        decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
        raw_good = {
            "market_ticker": "KXBTC15M-CTXGOOD",
            "decision_ts_utc": decision.isoformat(),
            "recv_ts_utc": decision.isoformat(),
            "seconds_to_close": 600,
            "strike": 100.0,
            "spot": 100.2,
            "yes_ask_cents": 58,
            "no_ask_cents": 44,
            "fee_cents": 1.0,
            "fill_prob": 0.75,
            "current_calibrated_p_yes": 0.62,
        }
        raw_bad = dict(raw_good)
        raw_bad["market_ticker"] = "KXBTC15M-CTXBAD"
        raw_bad.pop("yes_ask_cents")
        input_path = root / "raw.ndjson"
        output_path = root / "contexts.ndjson"
        issue_path = root / "issues.ndjson"
        input_path.write_text(json.dumps(raw_good) + "\n" + json.dumps(raw_bad) + "\n", encoding="utf-8")

        written, issues = normalize_candidate_contexts(input_path, output_path, issue_path)

        self.assertEqual(written, 1)
        self.assertEqual(issues, 1)
        self.assertIn("KXBTC15M-CTXGOOD", output_path.read_text(encoding="utf-8"))
        self.assertIn("missing required raw fields", issue_path.read_text(encoding="utf-8"))

        with contextlib.redirect_stdout(io.StringIO()):
            result = candidate_contexts_main(
                ["--input", str(input_path), "--output", str(root / "cli.ndjson"), "--issues", str(root / "cli_issues.ndjson")]
            )
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
