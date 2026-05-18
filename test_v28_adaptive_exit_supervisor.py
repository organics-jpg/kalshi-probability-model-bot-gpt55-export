from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from v28_adaptive_exit_supervisor import (
    AdaptiveExitSupervisor,
    AdaptiveExitSupervisorConfig,
    CHEAP_NO_COLLAPSE_BUCKET,
)


def supervisor(config: AdaptiveExitSupervisorConfig | None = None) -> AdaptiveExitSupervisor:
    root = Path(tempfile.mkdtemp())
    return AdaptiveExitSupervisor(
        config=config or AdaptiveExitSupervisorConfig(enabled=True, mode="enforce", recheck_seconds=5.0),
        state_path=root / "state.json",
        log_path=root / "events.ndjson",
    )


def collapse_fields(*, side: str = "no", qty: int = 2, entry: float = 10.0, p_hold: float = 0.20) -> dict:
    return {
        "mushroom_v28_side": side,
        "mushroom_v28_exit_reason": "mushroom_v28_probability_collapse_full",
        "mushroom_v28_exit_target_count": qty,
        "mushroom_v28_position_count": qty,
        "mushroom_v28_entry_basis_cents": entry,
        "mushroom_v28_exit_bid_cents": 8.0,
        "mushroom_v28_exit_fee_cents": 1.0,
        "mushroom_v28_p_hold": p_hold,
    }


class AdaptiveExitSupervisorTests(unittest.TestCase):
    def test_cheap_no_collapse_rechecks_then_converts_full_exit_to_reduce(self) -> None:
        ctrl = supervisor()

        first, defer = ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(), now_monotonic=10.0)
        self.assertTrue(defer)
        self.assertEqual(first["mushroom_v28_exit_reason"], "")
        self.assertEqual(first["mushroom_v28_adaptive_exit_action"], "recheck_defer")

        second, defer = ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(), now_monotonic=16.0)
        self.assertFalse(defer)
        self.assertEqual(second["mushroom_v28_exit_reason"], "mushroom_v28_adaptive_collapse_reduce")
        self.assertEqual(second["mushroom_v28_exit_target_count"], 1)
        self.assertEqual(second["mushroom_v28_adaptive_exit_bucket"], CHEAP_NO_COLLAPSE_BUCKET)

    def test_protected_runner_holds_remaining_one_lot_after_reduce(self) -> None:
        ctrl = supervisor(AdaptiveExitSupervisorConfig(enabled=True, mode="enforce", recheck_seconds=0.0))
        ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(qty=2), now_monotonic=10.0)
        ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(qty=2), now_monotonic=11.0)

        runner, defer = ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(qty=1), now_monotonic=12.0)

        self.assertFalse(defer)
        self.assertEqual(runner["mushroom_v28_exit_reason"], "")
        self.assertEqual(runner["mushroom_v28_exit_target_count"], 0)
        self.assertEqual(runner["mushroom_v28_adaptive_exit_action"], "protect_runner_hold")

    def test_yes_side_collapse_is_observed_but_not_changed(self) -> None:
        ctrl = supervisor(AdaptiveExitSupervisorConfig(enabled=True, mode="enforce", recheck_seconds=0.0))

        updated, defer = ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(side="yes"), now_monotonic=10.0)

        self.assertFalse(defer)
        self.assertEqual(updated["mushroom_v28_exit_reason"], "mushroom_v28_probability_collapse_full")
        self.assertFalse(updated["mushroom_v28_adaptive_exit_qualified"])

    def test_settlement_reward_disables_live_bucket_after_bad_live_evidence(self) -> None:
        ctrl = supervisor(
            AdaptiveExitSupervisorConfig(
                enabled=True,
                mode="enforce",
                recheck_seconds=0.0,
                disable_min_observations=1,
                disable_delta_cents=-5.0,
            )
        )
        ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(qty=2, entry=10.0, p_hold=0.20), now_monotonic=10.0)
        ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(qty=2, entry=10.0, p_hold=0.20), now_monotonic=11.0)

        outcome = ctrl.learn_from_settlement(market="KXBTC15M-TEST", result="yes")

        self.assertTrue(outcome["updated"])
        bucket = ctrl.state["buckets"][CHEAP_NO_COLLAPSE_BUCKET]
        self.assertTrue(bucket["disabled"])
        self.assertEqual(bucket["disable_reason"], "live_delta_guard")

    def test_shadow_disabled_bucket_records_counterfactual_without_live_change(self) -> None:
        ctrl = supervisor(AdaptiveExitSupervisorConfig(enabled=True, mode="enforce", recheck_seconds=0.0))
        ctrl.state["buckets"][CHEAP_NO_COLLAPSE_BUCKET] = {
            "observations": 3,
            "delta_cents": -200.0,
            "wins": 0,
            "losses": 3,
            "live_observations": 3,
            "live_delta_cents": -200.0,
            "disabled": True,
            "disable_reason": "live_delta_guard",
            "disabled_shadow_observations": 0,
            "disabled_shadow_delta_cents": 0.0,
        }

        updated, defer = ctrl.apply_exit(market="KXBTC15M-TEST", fields=collapse_fields(), now_monotonic=10.0)

        self.assertFalse(defer)
        self.assertEqual(updated["mushroom_v28_exit_reason"], "mushroom_v28_probability_collapse_full")
        self.assertEqual(updated["mushroom_v28_adaptive_exit_action"], "shadow_disabled")
        rows = [json.loads(line) for line in ctrl.log_path.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(row.get("event_type") == "adaptive_exit_decision" for row in rows))


if __name__ == "__main__":
    unittest.main()
