from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from v28_phi_reward_memory import (
    PhiRewardMemoryConfig,
    PhiRewardMemoryController,
    phi_trend_weights,
)


def controller(config: PhiRewardMemoryConfig | None = None) -> PhiRewardMemoryController:
    root = Path(tempfile.mkdtemp())
    ctrl = PhiRewardMemoryController(
        config=config or PhiRewardMemoryConfig(enabled=True, mode="enforce"),
        state_path=root / "state.json",
        log_path=root / "events.ndjson",
    )
    return ctrl


class PhiRewardMemoryTests(unittest.TestCase):
    def test_phi_weights_are_normalized_and_decay_by_phi(self) -> None:
        weights = phi_trend_weights()
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=12)
        self.assertGreater(weights["5m"], weights["15m"])
        self.assertAlmostEqual(weights["5m"] / weights["15m"], (1.0 + 5.0 ** 0.5) / 2.0, places=12)

    def test_correction_caps_are_enforced(self) -> None:
        ctrl = controller(PhiRewardMemoryConfig(enabled=True, mode="enforce", max_entry_correction_cents=1.0))
        ctrl.state["weights_cents"] = {name: 10.0 for name in ctrl.state["weights_cents"]}
        features = {name: 1.0 for name in ctrl.state["weights_cents"]}
        self.assertEqual(ctrl.correction_cents(kind="entry", features=features), 1.0)

    def test_zero_exit_cap_keeps_live_raw_exit_and_logs_shadow_projection(self) -> None:
        ctrl = controller(PhiRewardMemoryConfig(enabled=True, mode="enforce", max_exit_correction_cents=0.0))
        ctrl.state["weights_cents"] = {name: 0.0 for name in ctrl.state["weights_cents"]}
        ctrl.state["weights_cents"]["bias"] = -2.0
        fields = {
            "mushroom_v28_side": "yes",
            "mushroom_v28_exit_reason": "",
            "mushroom_v28_exit_target_count": 0,
            "mushroom_v28_position_count": 2,
            "mushroom_v28_fair_hold_cents": 70.0,
            "mushroom_v28_p_hold": 0.90,
            "mushroom_v28_exit_net_cents": 68.5,
            "mushroom_v28_exit_hold_buffer_cents": 1.0,
            "mushroom_v28_exit_hysteresis_cents": 0.25,
            "mushroom_v28_entry_basis_cents": 70.0,
            "mushroom_v28_exit_full_p_hold_floor": 0.72,
            "mushroom_v28_exit_reduce_p_hold_floor": 0.80,
            "mushroom_v28_exit_full_drawdown_cents": 15.0,
            "mushroom_v28_exit_fair_drawdown_cents": 8.0,
            "mushroom_v28_exit_reduce_fraction": 0.5,
        }

        updated = ctrl.apply_exit(market="KXBTC15M-TEST", fields=fields, trends={})

        self.assertEqual(updated["mushroom_v28_exit_reason"], "")
        self.assertEqual(updated["mushroom_v28_exit_target_count"], 0)
        self.assertEqual(updated["mushroom_v28_phi_memory_correction_cents"], 0.0)
        self.assertEqual(updated["mushroom_v28_phi_memory_adjusted_exit_reason"], "")
        self.assertEqual(updated["mushroom_v28_phi_memory_shadow_exit_correction_cents"], -2.0)
        self.assertEqual(updated["mushroom_v28_phi_memory_shadow_exit_reason"], "mushroom_v28_exit_value_over_hold")
        self.assertEqual(updated["mushroom_v28_phi_memory_shadow_exit_target_count"], 2)
        rows = [json.loads(line) for line in ctrl.log_path.read_text(encoding="utf-8").splitlines()]
        row = next(row for row in rows if row.get("event_type") == "exit_decision")
        self.assertFalse(row["memory_would_trade"])
        self.assertTrue(row["shadow_memory_would_trade"])
        self.assertEqual(row["shadow_adjusted_reason"], "mushroom_v28_exit_value_over_hold")

    def test_hard_gates_cannot_be_relaxed_by_near_pass(self) -> None:
        ctrl = controller()
        fields = {
            "mushroom_v28_book_ok": False,
            "mushroom_v28_btc_ok": True,
            "mushroom_v28_time_ok": True,
            "mushroom_v28_ask_ok": True,
            "mushroom_v28_risk_ok": True,
            "mushroom_v28_balance_ok": True,
            "mushroom_v28_block_reason": "",
            "mushroom_v28_min_edge_cents": 3.0,
            "mushroom_v28_depth_ratio": 8.0,
            "mushroom_v28_abs_d_sigma": 0.90,
        }
        near_pass, misses, details = ctrl.entry_near_pass(fields, adjusted_edge=2.5)
        self.assertFalse(near_pass)
        self.assertIn("hard_book", misses)
        self.assertFalse(details["hard_ok"])

    def test_one_soft_near_miss_can_explore(self) -> None:
        ctrl = controller()
        fields = {
            "mushroom_v28_book_ok": True,
            "mushroom_v28_btc_ok": True,
            "mushroom_v28_time_ok": True,
            "mushroom_v28_ask_ok": True,
            "mushroom_v28_risk_ok": True,
            "mushroom_v28_balance_ok": True,
            "mushroom_v28_block_reason": "",
            "mushroom_v28_min_edge_cents": 3.0,
            "mushroom_v28_depth_ratio": 8.0,
            "mushroom_v28_depth_ratio_ok": True,
            "mushroom_v28_abs_d_sigma": 0.90,
            "mushroom_v28_feature_gate_abs_d_min": 0.80,
            "mushroom_v28_feature_gate_abs_d_max": 1.10,
        }
        near_pass, misses, _ = ctrl.entry_near_pass(fields, adjusted_edge=2.5)
        self.assertTrue(near_pass)
        self.assertEqual(misses, ["edge_near"])

    def test_kill_switch_downgrades_enforce_to_shadow(self) -> None:
        ctrl = controller(
            PhiRewardMemoryConfig(
                enabled=True,
                mode="enforce",
                kill_net_pnl_dollars=-4.0,
                kill_loss_cluster=6,
            )
        )
        ctrl.state["net_pnl_dollars"] = -4.01
        ctrl._maybe_downgrade()
        self.assertEqual(ctrl.effective_mode(), "shadow")
        self.assertEqual(ctrl.state["downgrade_reason"], "net_pnl_kill")

    def test_live_side_flips_are_not_enabled_by_default(self) -> None:
        cfg = PhiRewardMemoryConfig(enabled=True, mode="enforce")
        self.assertFalse(cfg.allow_side_flip_live)

    def test_settlement_reward_updates_memory_observations(self) -> None:
        ctrl = controller()
        features = {name: 0.0 for name in ctrl.state["weights_cents"]}
        features["bias"] = 1.0
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "side": "yes",
                "qty": 2,
                "ask_cents": 70.0,
                "fee_cents_per_contract": 1.0,
                "features": features,
            },
        )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="yes",
            actual_pnl_dollars=0.58,
        )

        self.assertTrue(outcome["updated"])
        self.assertEqual(outcome["used_decision_count"], 1)
        self.assertEqual(ctrl.state["observations"], 1)
        self.assertGreater(ctrl.state["weights_cents"]["bias"], 0.0)
        self.assertIn("KXBTC15M-TEST", ctrl.state["settled_markets"])
        self.assertNotIn("KXBTC15M-TEST", ctrl.state["pending_markets"])

    def test_settlement_reward_is_idempotent_per_market(self) -> None:
        ctrl = controller()
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "side": "no",
                "qty": 1,
                "ask_cents": 80.0,
                "fee_cents_per_contract": 1.0,
                "features": {"bias": 1.0},
            },
        )

        first = ctrl.learn_from_settlement(market="KXBTC15M-TEST", result="yes")
        second = ctrl.learn_from_settlement(market="KXBTC15M-TEST", result="yes")

        self.assertTrue(first["updated"])
        self.assertFalse(second["updated"])
        self.assertEqual(second["reason"], "already_settled")
        self.assertEqual(ctrl.state["observations"], 1)

    def test_state_save_retries_transient_windows_replace_error(self) -> None:
        ctrl = controller()
        real_replace = os.replace
        calls = {"count": 0}

        def flaky_replace(src: str, dst: str) -> None:
            calls["count"] += 1
            if calls["count"] == 1:
                raise PermissionError("locked")
            real_replace(src, dst)

        with mock.patch("v28_phi_reward_memory.os.replace", side_effect=flaky_replace):
            ctrl.state["observations"] = 7
            ctrl.save()

        self.assertGreaterEqual(calls["count"], 2)
        self.assertTrue(ctrl.state_path.exists())
        self.assertFalse(ctrl.state["downgraded"])

    def test_state_save_failure_downgrades_without_raising(self) -> None:
        ctrl = controller()

        with mock.patch("v28_phi_reward_memory.os.replace", side_effect=PermissionError("locked")):
            ctrl.save()

        self.assertTrue(ctrl.state["downgraded"])
        self.assertEqual(ctrl.state["downgrade_reason"], "memory_state_write_failed")
        self.assertEqual(ctrl.effective_mode(), "shadow")

    def test_non_action_decisions_do_not_evict_reward_decisions(self) -> None:
        ctrl = controller()
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "side": "yes",
                "qty": 1,
                "ask_cents": 60.0,
                "fee_cents_per_contract": 1.0,
                "features": {"bias": 1.0},
            },
        )
        for _ in range(300):
            ctrl._record_pending_decision(
                market="KXBTC15M-TEST",
                decision={
                    "kind": "entry",
                    "raw_would_trade": False,
                    "memory_would_trade": False,
                    "side": "yes",
                    "qty": 1,
                    "ask_cents": 60.0,
                    "fee_cents_per_contract": 1.0,
                    "features": {"bias": 1.0},
                },
            )

        decisions = ctrl.state["pending_markets"]["KXBTC15M-TEST"]["decisions"]
        self.assertEqual(len(decisions), 1)
        outcome = ctrl.learn_from_settlement(market="KXBTC15M-TEST", result="yes")
        self.assertEqual(outcome["used_decision_count"], 1)

    def test_duplicate_action_decisions_are_coalesced(self) -> None:
        ctrl = controller()
        decision = {
            "kind": "entry",
            "raw_would_trade": False,
            "memory_would_trade": True,
            "side": "yes",
            "action": "explore",
            "qty": 2,
            "ask_cents": 60.0,
            "fee_cents_per_contract": 1.0,
            "features": {"bias": 1.0},
        }
        ctrl._record_pending_decision(market="KXBTC15M-TEST", decision=dict(decision))
        ctrl._record_pending_decision(market="KXBTC15M-TEST", decision=dict(decision))

        decisions = ctrl.state["pending_markets"]["KXBTC15M-TEST"]["decisions"]
        self.assertEqual(len(decisions), 1)

    def test_settlement_recovers_action_decisions_from_journal(self) -> None:
        ctrl = controller()
        ctrl.state["pending_markets"]["KXBTC15M-TEST"] = {
            "decisions": [
                {
                    "kind": "entry",
                    "raw_would_trade": False,
                    "memory_would_trade": False,
                    "side": "yes",
                    "action": "none",
                    "features": {"bias": 1.0},
                }
            ]
        }
        ctrl.log_event(
            "entry_decision",
            market="KXBTC15M-TEST",
            kind="entry",
            side="yes",
            action="explore",
            raw_would_trade=False,
            memory_would_trade=True,
            ask_cents=60.0,
            fee_cents_per_contract=1.0,
            qty=1,
            features={"bias": 1.0},
        )

        outcome = ctrl.learn_from_settlement(market="KXBTC15M-TEST", result="yes")

        self.assertEqual(outcome["recovered_decision_count"], 1)
        self.assertEqual(outcome["used_decision_count"], 1)
        self.assertEqual(ctrl.state["observations"], 1)

    def test_filled_exploration_uses_actual_fill_cashflow(self) -> None:
        ctrl = controller()
        features = {"bias": 1.0}
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "enforced": True,
                "action": "explore",
                "side": "yes",
                "qty": 2,
                "ask_cents": 60.0,
                "fee_cents_per_contract": 1.0,
                "features": features,
            },
        )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="yes",
            outcome_record={
                "traded": True,
                "side": "yes",
                "entry_qty": 2,
                "entry_fill_cents": 50,
                "entry_fee_cents": 2,
                "exit_qty": 0,
                "pnl_dollars": 0.98,
            },
        )

        self.assertEqual(outcome["used_decision_count"], 1)
        self.assertEqual(outcome["actual_fill_decision_count"], 1)
        self.assertEqual(outcome["unfilled_label_decision_count"], 0)
        self.assertEqual(outcome["entry_fill_attributed_qty"], 2)
        self.assertEqual(outcome["attribution_mode_counts"], {"actual_entry_fill": 1})
        self.assertEqual(outcome["reward_by_kind_cents"], {"entry": 98.0})
        self.assertEqual(outcome["reward_by_action_cents"], {"explore": 98.0})
        self.assertAlmostEqual(outcome["reward_delta_cents"], 98.0)
        self.assertGreater(ctrl.state["weights_cents"]["bias"], 0.0)

    def test_zero_fill_exploration_gets_small_settlement_label_not_full_fill(self) -> None:
        ctrl = controller()
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "enforced": True,
                "action": "explore",
                "side": "yes",
                "qty": 2,
                "ask_cents": 60.0,
                "fee_cents_per_contract": 1.0,
                "features": {"bias": 1.0},
            },
        )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="yes",
            outcome_record={
                "traded": False,
                "side": "",
                "entry_qty": 0,
                "entry_fill_cents": None,
                "entry_fee_cents": 0,
                "ioc_zero_fill_count": 1,
                "pnl_dollars": 0.0,
            },
        )

        self.assertEqual(outcome["actual_fill_decision_count"], 0)
        self.assertEqual(outcome["unfilled_label_decision_count"], 1)
        self.assertEqual(outcome["entry_fill_attributed_qty"], 0)
        self.assertAlmostEqual(outcome["reward_delta_cents"], 10.0)

    def test_entry_fill_reward_uses_settlement_hold_path_not_exit_cashflow(self) -> None:
        ctrl = controller()
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "enforced": True,
                "action": "explore",
                "side": "yes",
                "qty": 2,
                "ask_cents": 60.0,
                "fee_cents_per_contract": 1.0,
                "features": {"bias": 1.0},
            },
        )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="no",
            outcome_record={
                "traded": True,
                "side": "yes",
                "entry_qty": 2,
                "entry_fill_cents": 60,
                "entry_fee_cents": 2,
                "exit_qty": 2,
                "exit_fill_cents": 80,
                "exit_fee_cents": 2,
                "pnl_dollars": 0.36,
            },
        )

        self.assertEqual(outcome["actual_fill_decision_count"], 1)
        self.assertAlmostEqual(outcome["reward_delta_cents"], -122.0)

    def test_same_market_side_flip_entry_reward_uses_matching_side_cashflow(self) -> None:
        ctrl = controller()
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "entry",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "enforced": True,
                "action": "explore",
                "side": "no",
                "qty": 3,
                "ask_cents": 12.0,
                "fee_cents_per_contract": 1.0,
                "features": {"bias": 1.0},
            },
        )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="yes",
            outcome_record={
                "traded": True,
                "side": "yes",
                "entry_qty": 6,
                "entry_fill_cents": 48.5,
                "entry_fee_cents": 6,
                "exit_qty": 3,
                "exit_fill_cents": 77,
                "exit_fee_cents": 3,
                "pnl_dollars": -0.69,
                "side_cashflows": {
                    "yes": {
                        "entry_qty": 3,
                        "entry_notional_cents": 255,
                        "entry_fee_cents": 3,
                        "exit_qty": 3,
                        "exit_notional_cents": 231,
                        "exit_fee_cents": 3,
                    },
                    "no": {
                        "entry_qty": 3,
                        "entry_notional_cents": 36,
                        "entry_fee_cents": 3,
                        "exit_qty": 0,
                        "exit_notional_cents": 0,
                        "exit_fee_cents": 0,
                    },
                },
            },
        )

        self.assertEqual(outcome["actual_fill_decision_count"], 1)
        self.assertEqual(outcome["entry_fill_attributed_qty"], 3)
        self.assertEqual(outcome["attribution_mode_counts"], {"actual_entry_fill": 1})
        self.assertAlmostEqual(outcome["reward_delta_cents"], -39.0)

    def test_repeated_unfilled_qualified_signals_are_labeled_once(self) -> None:
        ctrl = controller()
        for ask in (60.0, 61.0):
            ctrl._record_pending_decision(
                market="KXBTC15M-TEST",
                decision={
                    "kind": "entry",
                    "raw_would_trade": False,
                    "memory_would_trade": True,
                    "enforced": True,
                    "action": "explore",
                    "side": "no",
                    "qty": 1,
                    "ask_cents": ask,
                    "fee_cents_per_contract": 1.0,
                    "features": {"bias": 1.0},
                },
            )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="yes",
            outcome_record={"traded": False, "entry_qty": 0, "ioc_zero_fill_count": 2},
        )

        self.assertEqual(outcome["used_decision_count"], 1)
        self.assertEqual(outcome["unfilled_label_decision_count"], 1)
        self.assertAlmostEqual(outcome["reward_delta_cents"], -5.0)

    def test_actual_exit_fill_rewards_exit_vs_hold(self) -> None:
        ctrl = controller()
        ctrl._record_pending_decision(
            market="KXBTC15M-TEST",
            decision={
                "kind": "exit",
                "raw_would_trade": False,
                "memory_would_trade": True,
                "enforced": True,
                "action": "exit",
                "side": "yes",
                "qty": 2,
                "bid_cents": 80.0,
                "entry_basis_cents": 60.0,
                "fee_cents_per_contract": 1.0,
                "features": {"bias": 1.0},
            },
        )

        outcome = ctrl.learn_from_settlement(
            market="KXBTC15M-TEST",
            result="no",
            outcome_record={
                "traded": True,
                "side": "yes",
                "entry_qty": 2,
                "entry_fill_cents": 60,
                "entry_fee_cents": 2,
                "exit_qty": 2,
                "exit_fill_cents": 80,
                "exit_fee_cents": 2,
                "pnl_dollars": 0.36,
            },
        )

        self.assertEqual(outcome["actual_fill_decision_count"], 1)
        self.assertEqual(outcome["exit_fill_attributed_qty"], 2)
        self.assertAlmostEqual(outcome["reward_delta_cents"], 158.0)


if __name__ == "__main__":
    unittest.main()
