from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from v28_trade_lifecycle import TradeLifecycleConfig, TradeLifecycleController


def lifecycle(
    *,
    enabled: bool = True,
    mode: str = "exit_only_enforce",
    exit_toll_cents: float = 2.5,
    recheck_seconds: float = 5.0,
    promote_delta_cents: float = 100.0,
    disable_bad_settles: int = 3,
    min_promote_observations: int = 1,
) -> TradeLifecycleController:
    root = Path(tempfile.mkdtemp())
    return TradeLifecycleController(
        TradeLifecycleConfig(
            enabled=enabled,
            mode=mode,
            state_path=root / "state.json",
            log_path=root / "events.ndjson",
            exit_toll_cents=exit_toll_cents,
            recheck_seconds=recheck_seconds,
            cheap_entry_max_cents=15.0,
            promote_delta_cents=promote_delta_cents,
            disable_bad_settles=disable_bad_settles,
            min_promote_observations=min_promote_observations,
        )
    )


def exit_fields(
    *,
    reason: str = "mushroom_v28_exit_value_over_hold",
    entry: float = 50.0,
    exit_net: float = 53.0,
    hold_net: float = 51.0,
    fee: float = 0.5,
    count: int = 2,
) -> dict:
    return {
        "mushroom_v28_exit_reason": reason,
        "mushroom_v28_exit_target_cents": 54.0,
        "mushroom_v28_exit_entry_basis_cents": entry,
        "mushroom_v28_exit_net_cents": exit_net,
        "mushroom_v28_exit_hold_net_cents": hold_net,
        "mushroom_v28_exit_fee_cents": fee,
        "mushroom_v28_exit_count": count,
    }


class TradeLifecycleControllerTests(unittest.TestCase):
    def test_value_exit_below_toll_is_suppressed(self) -> None:
        ctrl = lifecycle()

        updated, defer = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            position_bucket="settlement_hold",
            fields=exit_fields(exit_net=53.0, hold_net=51.0),
        )

        self.assertFalse(defer)
        self.assertEqual(updated["mushroom_v28_exit_reason"], "")
        self.assertEqual(updated["mushroom_v28_lifecycle_action"], "suppress_below_exit_toll")
        self.assertTrue(updated["mushroom_v28_lifecycle_enforced"])

    def test_value_exit_above_toll_executes(self) -> None:
        ctrl = lifecycle()

        updated, defer = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            position_bucket="settlement_hold",
            fields=exit_fields(exit_net=55.0, hold_net=51.0),
        )

        self.assertFalse(defer)
        self.assertEqual(updated["mushroom_v28_exit_reason"], "mushroom_v28_exit_value_over_hold")
        self.assertEqual(updated["mushroom_v28_lifecycle_action"], "allow")

    def test_uncertain_bucket_delays_once_then_allows_persistent_raw_exit(self) -> None:
        ctrl = lifecycle(recheck_seconds=5.0)

        first, defer = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            position_bucket="uncertain",
            fields=exit_fields(reason="mushroom_v28_probability_reduce", exit_net=45.0, hold_net=45.0),
            now_monotonic=10.0,
        )
        self.assertTrue(defer)
        self.assertEqual(first["mushroom_v28_exit_reason"], "")
        self.assertEqual(first["mushroom_v28_lifecycle_action"], "delay_uncertain_recheck")

        second, defer = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            position_bucket="uncertain",
            fields=exit_fields(reason="mushroom_v28_probability_reduce", exit_net=45.0, hold_net=45.0),
            now_monotonic=16.0,
        )
        self.assertFalse(defer)
        self.assertEqual(second["mushroom_v28_exit_reason"], "mushroom_v28_probability_reduce")
        self.assertEqual(second["mushroom_v28_lifecycle_action"], "allow_after_uncertain_recheck")

    def test_collapse_safety_exit_is_non_overridable(self) -> None:
        ctrl = lifecycle()

        updated, defer = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            position_bucket="settlement_hold",
            fields=exit_fields(reason="mushroom_v28_probability_collapse_full", exit_net=10.0, hold_net=90.0),
        )

        self.assertFalse(defer)
        self.assertEqual(updated["mushroom_v28_exit_reason"], "mushroom_v28_probability_collapse_full")
        self.assertEqual(updated["mushroom_v28_lifecycle_action"], "allow_non_overridable")

    def test_cheap_contract_churn_exit_is_suppressed_unless_emergency(self) -> None:
        ctrl = lifecycle()

        updated, _ = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            position_bucket="fragile",
            fields=exit_fields(entry=12.0, exit_net=20.0, hold_net=10.0),
        )
        self.assertEqual(updated["mushroom_v28_exit_reason"], "")
        self.assertEqual(updated["mushroom_v28_lifecycle_action"], "suppress_cheap_contract_churn")

        emergency, _ = ctrl.apply_exit(
            market_ticker="KXBTC15M-TEST2",
            side="NO",
            position_bucket="fragile",
            fields=exit_fields(
                reason="mushroom_v28_probability_collapse_full",
                entry=12.0,
                exit_net=5.0,
                hold_net=80.0,
            ),
        )
        self.assertEqual(emergency["mushroom_v28_exit_reason"], "mushroom_v28_probability_collapse_full")

    def test_fragile_and_danger_cap_addons_but_not_first_entry(self) -> None:
        ctrl = lifecycle()

        clear, reason = ctrl.should_cap_addon(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            current_bucket="settlement_hold",
            current_count=0,
        )
        self.assertFalse(clear)
        self.assertEqual(reason, "")

        capped, reason = ctrl.should_cap_addon(
            market_ticker="KXBTC15M-TEST",
            side="NO",
            current_bucket="fragile",
            current_count=2,
        )
        self.assertTrue(capped)
        self.assertEqual(reason, "fragile_addon_cap")
        self.assertFalse(ctrl.has_pending_market("KXBTC15M-TEST"))

    def test_addon_cap_without_counterfactual_price_does_not_learn(self) -> None:
        ctrl = lifecycle()

        ctrl._append_pending(
            "KXBTC15M-TEST",
            {
                "kind": "addon_cap",
                "bucket": "danger",
                "side": "YES",
                "count": 2,
                "rewardable": False,
            },
        )
        outcome = ctrl.learn_from_settlement(market_ticker="KXBTC15M-TEST", result="YES")

        self.assertIsNotNone(outcome)
        self.assertEqual(outcome["reward_delta_cents"], 0.0)
        self.assertEqual(ctrl.state["buckets"]["danger"]["observations"], 0)

    def test_repeated_suppressed_exit_is_one_reward_observation(self) -> None:
        ctrl = lifecycle()

        for _ in range(5):
            ctrl.apply_exit(
                market_ticker="KXBTC15M-TEST",
                side="NO",
                position_bucket="settlement_hold",
                fields=exit_fields(exit_net=53.0, hold_net=51.0, count=2),
            )

        pending = ctrl.state["pending_decisions"]["KXBTC15M-TEST"]
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["seen_count"], 5)

        outcome = ctrl.learn_from_settlement(market_ticker="KXBTC15M-TEST", result="NO")

        self.assertIsNotNone(outcome)
        self.assertEqual(len(outcome["rewards"]), 1)
        self.assertEqual(outcome["reward_delta_cents"], 94.0)
        self.assertEqual(ctrl.state["buckets"]["settlement_hold"]["observations"], 1)

    def test_exit_reward_uses_total_position_cents(self) -> None:
        ctrl = lifecycle()

        ctrl._append_pending(
            "KXBTC15M-TEST",
            {
                "kind": "exit_change",
                "bucket": "settlement_hold",
                "side": "NO",
                "raw_exit_value_cents": 90.0,
                "count": 3,
            },
        )
        outcome = ctrl.learn_from_settlement(market_ticker="KXBTC15M-TEST", result="NO")

        self.assertIsNotNone(outcome)
        self.assertEqual(outcome["reward_delta_cents"], 30.0)

    def test_exit_reward_uses_actual_later_exit_when_available(self) -> None:
        ctrl = lifecycle()

        ctrl._append_pending(
            "KXBTC15M-TEST",
            {
                "kind": "exit_change",
                "bucket": "settlement_hold",
                "side": "NO",
                "raw_exit_value_cents": 60.0,
                "count": 3,
            },
        )
        outcome = ctrl.learn_from_settlement(
            market_ticker="KXBTC15M-TEST",
            result="NO",
            outcome_record={
                "side_cashflows": {
                    "no": {
                        "exit_qty": 3,
                        "exit_notional_cents": 210.0,
                        "exit_fee_cents": 6.0,
                    }
                }
            },
        )

        self.assertIsNotNone(outcome)
        self.assertEqual(outcome["reward_delta_cents"], 24.0)

    def test_addon_cap_logging_is_throttled_and_not_pending(self) -> None:
        ctrl = lifecycle()

        for _ in range(5):
            capped, reason = ctrl.should_cap_addon(
                market_ticker="KXBTC15M-TEST",
                side="YES",
                current_bucket="danger",
                current_count=2,
            )
            self.assertTrue(capped)
            self.assertEqual(reason, "danger_addon_cap")

        self.assertFalse(ctrl.has_pending_market("KXBTC15M-TEST"))
        lines = ctrl.log_path.read_text(encoding="utf-8").strip().splitlines()
        addon_lines = [line for line in lines if "lifecycle_addon_capped" in line]
        self.assertEqual(len(addon_lines), 1)

    def test_bucket_promotion_and_disable_thresholds(self) -> None:
        ctrl = lifecycle(promote_delta_cents=100.0, disable_bad_settles=3)
        for market in ("KXBTC15M-A", "KXBTC15M-B"):
            ctrl._append_pending(
                market,
                {
                    "kind": "exit_change",
                    "bucket": "settlement_hold",
                    "side": "NO",
                    "raw_exit_value_cents": 20.0,
                    "count": 2,
                    "fee_saved_cents": 1.0,
                },
            )
            ctrl.learn_from_settlement(market_ticker=market, result="NO")

        self.assertTrue(ctrl.state["buckets"]["settlement_hold"]["promoted"])

        for idx in range(3):
            market = f"KXBTC15M-LOSS{idx}"
            ctrl._append_pending(
                market,
                {
                    "kind": "exit_change",
                    "bucket": "fragile",
                    "side": "NO",
                    "raw_exit_value_cents": 90.0,
                    "count": 1,
                    "fee_saved_cents": 1.0,
                },
            )
            ctrl.learn_from_settlement(market_ticker=market, result="YES")

        self.assertTrue(ctrl.state["buckets"]["fragile"]["disabled"])
        self.assertEqual(ctrl.state["buckets"]["fragile"]["disable_reason"], "bad_settle_threshold")


if __name__ == "__main__":
    unittest.main()
