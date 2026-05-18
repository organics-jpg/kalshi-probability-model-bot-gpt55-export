from __future__ import annotations

import unittest
from datetime import datetime, timezone

from build_v28_successor_live_pnl_policy_lab import (
    DEFAULT_POLICY_SPEC,
    build_labeled_decision_rows,
    build_policy_registry_rows,
    estimated_taker_fee_cents,
    policy_hash,
    score_labeled_decisions,
)
from run_v28_successor_live_pnl_policy_cycle import live_pnl_cycle_status


SELECTED_CANDIDATE_ID = "v28s_boundary_monotonic_light_v001"


def frozen_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "frozen_prediction_id": "frozen-1",
        "frozen_utc": "2026-05-12T00:02:00Z",
        "row_id": "row-1",
        "market_ticker": "KXBTC15M-TEST",
        "market_close_ts_utc": "2026-05-12T00:15:00Z",
        "decision_ts_utc": "2026-05-12T00:01:00Z",
        "side": "yes",
        "strike": "100000",
        "seconds_to_close": "840",
        "candidate_id": SELECTED_CANDIDATE_ID,
        "model_hash": "model-hash-a",
        "model_type": "regularized_logistic",
        "model_track": "pure_physics",
        "candidate_p_yes": "0.70",
        "candidate_fair_yes_cents": "70",
        "candidate_fair_no_cents": "30",
        "candidate_fair_side_cents": "70",
        "v28_p_yes": "0.40",
        "v28_fair_yes_cents": "40",
        "v28_fair_no_cents": "60",
        "ask_cents": "78",
        "source_status": "frozen_pre_resolution_prediction",
    }
    row.update(overrides)
    return row


def packet_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "row_id": "row-1",
        "candidate_id": SELECTED_CANDIDATE_ID,
        "model_hash": "model-hash-a",
        "side": "yes",
        "bid_cents": "49",
        "book_width_cents": "1",
        "book_mid_yes_cents": "49.5",
        "book_source_event_count": "2",
        "btc_tick_age_ms": "30000",
        "btc_stale_flag": "False",
        "v28_d_sigma": "0.50",
        "v28_sigma_t_dollars": "42",
        "v28_arrow": "0.10",
        "v28_transport_recent_n": "12",
        "v28_transport_long_n": "48",
    }
    row.update(overrides)
    return row


def trigger_no_row(**overrides: object) -> dict[str, object]:
    row = frozen_row(
        frozen_prediction_id="frozen-no",
        row_id="row-no",
        side="no",
        ask_cents="40",
        candidate_p_yes="0.30",
        candidate_fair_yes_cents="30",
        candidate_fair_no_cents="70",
        candidate_fair_side_cents="70",
        v28_fair_yes_cents="50",
        v28_fair_no_cents="50",
    )
    row.update(overrides)
    return row


class V28SuccessorLivePnlPolicyLabTests(unittest.TestCase):
    def test_fee_formula_matches_local_v28_integer_cent_taker_model(self) -> None:
        self.assertEqual(estimated_taker_fee_cents(50, 1), 2)
        self.assertEqual(estimated_taker_fee_cents(30, 1), 2)
        self.assertEqual(estimated_taker_fee_cents(1, 1), 1)

    def test_policy_hash_is_stable_and_registry_has_no_labels(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [frozen_row(), trigger_no_row()],
            [packet_row(), packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )
        yes_row = next(row for row in rows if row["row_id"] == "row-1")

        self.assertEqual(summary["policy_hash"], policy_hash(DEFAULT_POLICY_SPEC))
        self.assertEqual(summary["primary_evidence_rows"], 1)
        self.assertEqual(yes_row["allowed_for_primary_live_pnl_evidence"], "True")
        self.assertEqual(yes_row["policy_candidate_selected"], "True")
        self.assertEqual(yes_row["policy_action"], "enter")
        self.assertNotIn("y_yes_win", yes_row)
        self.assertNotIn("settlement_price", yes_row)

    def test_no_side_rows_are_diagnostic_and_policy_skipped(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                trigger_no_row()
            ],
            [packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )

        self.assertEqual(summary["primary_evidence_rows"], 0)
        self.assertEqual(rows[0]["policy_candidate_selected"], "False")
        self.assertEqual(rows[0]["allowed_for_primary_live_pnl_evidence"], "False")
        self.assertEqual(rows[0]["policy_action"], "skip")
        self.assertIn("side_not_allowed_for_policy", rows[0]["primary_evidence_blockers"])
        self.assertIn("side_not_allowed_for_policy", rows[0]["policy_skip_reason"])

    def test_policy_requires_five_cent_paired_no_v28_net_edge_before_entry(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(),
                trigger_no_row(v28_fair_yes_cents="54", v28_fair_no_cents="46"),
            ],
            [packet_row(), packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )
        yes_row = next(row for row in rows if row["row_id"] == "row-1")

        self.assertEqual(summary["primary_evidence_rows"], 1)
        self.assertEqual(yes_row["policy_action"], "skip")
        self.assertIn("policy_missing_net_edge", yes_row["policy_skip_reason"])

    def test_policy_rejects_yes_rows_inside_last_five_minutes(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(
                    seconds_to_close="250",
                ),
                trigger_no_row(seconds_to_close="250"),
            ],
            [packet_row(), packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )
        yes_row = next(row for row in rows if row["row_id"] == "row-1")

        self.assertEqual(summary["primary_evidence_rows"], 1)
        self.assertEqual(yes_row["dynamic_threshold_cents"], "5.000000")
        self.assertEqual(yes_row["policy_action"], "skip")
        self.assertIn("too_close_to_close", yes_row["policy_skip_reason"])

    def test_policy_requires_trigger_no_ask_below_fade_ceiling(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(),
                trigger_no_row(ask_cents="45", v28_fair_yes_cents="30", v28_fair_no_cents="70"),
            ],
            [packet_row(), packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )
        yes_row = next(row for row in rows if row["row_id"] == "row-1")

        self.assertEqual(summary["primary_evidence_rows"], 1)
        self.assertEqual(yes_row["policy_action"], "skip")
        self.assertIn("policy_missing_net_edge", yes_row["policy_skip_reason"])

    def test_unselected_candidate_rows_are_diagnostic_and_policy_skipped(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [frozen_row(candidate_id="other-candidate")],
            [packet_row(candidate_id="other-candidate")],
            policy_created_utc=created,
        )

        self.assertEqual(summary["primary_evidence_rows"], 0)
        self.assertEqual(rows[0]["policy_candidate_selected"], "False")
        self.assertEqual(rows[0]["allowed_for_primary_live_pnl_evidence"], "False")
        self.assertEqual(rows[0]["policy_action"], "skip")
        self.assertIn("candidate_model_not_selected_for_policy", rows[0]["primary_evidence_blockers"])
        self.assertIn("candidate_model_not_selected_for_policy", rows[0]["policy_skip_reason"])

    def test_selected_yes_side_rows_are_primary_when_quality_passes(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(
                    side="yes",
                    candidate_fair_side_cents="70",
                    ask_cents="78",
                ),
                trigger_no_row(),
            ],
            [packet_row(side="yes"), packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )
        yes_row = next(row for row in rows if row["row_id"] == "row-1")

        self.assertEqual(summary["primary_evidence_rows"], 1)
        self.assertEqual(yes_row["policy_candidate_selected"], "True")
        self.assertEqual(yes_row["allowed_for_primary_live_pnl_evidence"], "True")
        self.assertEqual(yes_row["policy_action"], "enter")

    def test_policy_uses_midband_yes_ask_window(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(
                    frozen_prediction_id="frozen-low",
                    row_id="row-low",
                    decision_ts_utc="2026-05-12T00:01:00Z",
                    ask_cents="64",
                    seconds_to_close="840",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-low",
                    row_id="row-no-low",
                    decision_ts_utc="2026-05-12T00:01:00Z",
                    seconds_to_close="840",
                ),
                frozen_row(
                    frozen_prediction_id="frozen-mid",
                    row_id="row-mid",
                    market_ticker="KXBTC15M-TEST2",
                    decision_ts_utc="2026-05-12T00:02:00Z",
                    ask_cents="65",
                    seconds_to_close="780",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-mid",
                    row_id="row-no-mid",
                    market_ticker="KXBTC15M-TEST2",
                    decision_ts_utc="2026-05-12T00:02:00Z",
                    seconds_to_close="780",
                ),
                frozen_row(
                    frozen_prediction_id="frozen-high",
                    row_id="row-high",
                    market_ticker="KXBTC15M-TEST3",
                    decision_ts_utc="2026-05-12T00:03:00Z",
                    ask_cents="81",
                    seconds_to_close="720",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-high",
                    row_id="row-no-high",
                    market_ticker="KXBTC15M-TEST3",
                    decision_ts_utc="2026-05-12T00:03:00Z",
                    seconds_to_close="720",
                ),
            ],
            [
                packet_row(row_id="row-low"),
                packet_row(row_id="row-no-low", side="no"),
                packet_row(row_id="row-mid"),
                packet_row(row_id="row-no-mid", side="no"),
                packet_row(row_id="row-high"),
                packet_row(row_id="row-no-high", side="no"),
            ],
            policy_created_utc=created,
        )
        yes_by_row = {row["row_id"]: row for row in rows if row["side"] == "yes"}

        self.assertEqual(summary["primary_evidence_rows"], 3)
        self.assertEqual(yes_by_row["row-low"]["policy_action"], "skip")
        self.assertIn("ask_too_low", yes_by_row["row-low"]["policy_skip_reason"])
        self.assertEqual(yes_by_row["row-mid"]["policy_action"], "enter")
        self.assertEqual(yes_by_row["row-high"]["policy_action"], "skip")
        self.assertIn("ask_too_high", yes_by_row["row-high"]["policy_skip_reason"])

    def test_policy_allows_only_one_entry_per_market(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(
                    frozen_prediction_id="frozen-1",
                    row_id="row-1",
                    decision_ts_utc="2026-05-12T00:01:00Z",
                    seconds_to_close="840",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-1",
                    row_id="row-no-1",
                    decision_ts_utc="2026-05-12T00:01:00Z",
                    seconds_to_close="840",
                ),
                frozen_row(
                    frozen_prediction_id="frozen-2",
                    row_id="row-2",
                    decision_ts_utc="2026-05-12T00:02:00Z",
                    seconds_to_close="780",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-2",
                    row_id="row-no-2",
                    decision_ts_utc="2026-05-12T00:02:00Z",
                    seconds_to_close="780",
                ),
            ],
            [
                packet_row(row_id="row-1"),
                packet_row(row_id="row-no-1", side="no"),
                packet_row(row_id="row-2"),
                packet_row(row_id="row-no-2", side="no"),
            ],
            policy_created_utc=created,
        )
        yes_rows = [row for row in rows if row["side"] == "yes"]

        self.assertEqual(summary["primary_evidence_rows"], 2)
        self.assertEqual(yes_rows[0]["policy_action"], "enter")
        self.assertEqual(yes_rows[1]["policy_action"], "skip")
        self.assertIn("market_entry_cap_reached", yes_rows[1]["policy_skip_reason"])

    def test_pre_policy_diagnostic_entry_does_not_consume_market_cap(self) -> None:
        created = datetime(2026, 5, 12, 0, 1, 30, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [
                frozen_row(
                    frozen_prediction_id="frozen-before",
                    row_id="row-before",
                    decision_ts_utc="2026-05-12T00:01:00Z",
                    seconds_to_close="840",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-before",
                    row_id="row-no-before",
                    decision_ts_utc="2026-05-12T00:01:00Z",
                    seconds_to_close="840",
                ),
                frozen_row(
                    frozen_prediction_id="frozen-after",
                    row_id="row-after",
                    decision_ts_utc="2026-05-12T00:02:00Z",
                    seconds_to_close="780",
                ),
                trigger_no_row(
                    frozen_prediction_id="frozen-no-after",
                    row_id="row-no-after",
                    decision_ts_utc="2026-05-12T00:02:00Z",
                    seconds_to_close="780",
                ),
            ],
            [
                packet_row(row_id="row-before"),
                packet_row(row_id="row-no-before", side="no"),
                packet_row(row_id="row-after"),
                packet_row(row_id="row-no-after", side="no"),
            ],
            policy_created_utc=created,
        )
        yes_rows = [row for row in rows if row["side"] == "yes"]

        self.assertEqual(summary["primary_evidence_rows"], 1)
        self.assertEqual(yes_rows[0]["allowed_for_primary_live_pnl_evidence"], "False")
        self.assertEqual(yes_rows[0]["policy_action"], "enter")
        self.assertEqual(yes_rows[1]["allowed_for_primary_live_pnl_evidence"], "True")
        self.assertEqual(yes_rows[1]["policy_action"], "enter")

    def test_pre_policy_rows_are_diagnostic_not_primary_credit(self) -> None:
        created_after_decision = datetime(2026, 5, 12, 0, 5, tzinfo=timezone.utc)
        rows, summary = build_policy_registry_rows(
            [frozen_row()],
            [packet_row()],
            policy_created_utc=created_after_decision,
        )

        self.assertEqual(summary["primary_evidence_rows"], 0)
        self.assertEqual(rows[0]["allowed_for_primary_live_pnl_evidence"], "False")
        self.assertIn("decision_before_policy_hash_created", rows[0]["primary_evidence_blockers"])

    def test_label_join_scores_policy_and_same_row_v28_baseline(self) -> None:
        created = datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc)
        registry, _summary = build_policy_registry_rows(
            [frozen_row(), trigger_no_row()],
            [packet_row(), packet_row(row_id="row-no", side="no")],
            policy_created_utc=created,
        )
        labels = [
            {
                "labeled_row_id": "label-1",
                "frozen_prediction_id": "frozen-1",
                "label_join_status": "joined_post_resolution",
                "y_yes_win": "1",
                "settlement_price": "100050",
                "settlement_margin_dollars": "50",
                "settlement_side": "yes",
                "settlement_ts_utc": "2026-05-12T00:15:05Z",
                "label_available_ts_utc": "2026-05-12T00:15:05Z",
                "settlement_source": "unit_test",
            }
        ]

        labeled, label_summary = build_labeled_decision_rows(registry, labels)
        scores, score_summary = score_labeled_decisions(labeled)

        self.assertEqual(label_summary["joined_rows"], 1)
        self.assertEqual(labeled[0]["policy_outcome"], "win")
        self.assertAlmostEqual(float(labeled[0]["policy_net_pnl_cents"]), 20.0)
        self.assertAlmostEqual(float(labeled[0]["v28_reference_net_pnl_cents"]), 0.0)
        self.assertAlmostEqual(float(labeled[0]["book_only_net_pnl_cents"]), 0.0)
        self.assertEqual(score_summary["primary_live_forward_rows_after_policy_hash"], 1)
        self.assertEqual(scores[1]["slice"], "primary_live_forward_rows_after_policy_hash")
        self.assertAlmostEqual(float(scores[1]["net_pnl_cents"]), 20.0)
        self.assertAlmostEqual(float(scores[1]["book_only_net_pnl_cents"]), 0.0)
        self.assertAlmostEqual(float(scores[1]["delta_net_cents_vs_always_skip"]), 20.0)

    def test_cycle_status_separates_unlabeled_primary_rows_from_no_capture(self) -> None:
        status, blockers, next_actions = live_pnl_cycle_status(
            sidecar_summary={"cycle_status": "sidecar_cycle_ready_for_external_promotion_verifier"},
            live_pnl_summary={
                "registry_rows": 18,
                "primary_policy_rows_after_hash": 18,
                "primary_live_forward_rows_after_policy_hash": 0,
                "diagnostic_rows_not_primary_credit": 0,
            },
            readiness={"level_1_complete": False},
        )

        self.assertEqual(status, "primary_rows_captured_waiting_for_settlement_labels")
        self.assertIn("primary_rows_pending_settlement_labels", blockers)
        self.assertTrue(any("Rerun" in action for action in next_actions))

    def test_cycle_status_keeps_positive_net_zero_delta_as_collect_more(self) -> None:
        status, blockers, next_actions = live_pnl_cycle_status(
            sidecar_summary={"cycle_status": "sidecar_cycle_ready_for_external_promotion_verifier"},
            live_pnl_summary={
                "registry_rows": 18,
                "primary_policy_rows_after_hash": 4,
                "primary_live_forward_rows_after_policy_hash": 4,
                "primary_markets_after_policy_hash": 2,
                "primary_entered_rows_after_policy_hash": 1,
                "primary_net_pnl_cents": "9.0",
                "primary_delta_vs_v28_cents": "0.0",
                "diagnostic_rows_not_primary_credit": 0,
            },
            readiness={"level_1_complete": False},
        )

        self.assertNotEqual(status, "profit_goal_incomplete_candidate_failed_forward_pnl")
        self.assertIn("profit_goal_delta_vs_v28_not_positive", blockers)
        self.assertTrue(any("zero v28 delta" in action for action in next_actions))


if __name__ == "__main__":
    unittest.main()
