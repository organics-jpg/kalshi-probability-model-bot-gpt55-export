from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUCKETS = ("settlement_hold", "scalp", "fragile", "danger", "uncertain")
NON_OVERRIDABLE_REASON_TOKENS = (
    "collapse",
    "collapse_full",
    "safety",
    "account",
    "mismatch",
    "stale",
    "source",
    "exchange",
    "kill",
)


@dataclass
class TradeLifecycleConfig:
    enabled: bool = False
    mode: str = "shadow"
    state_path: Path | str = Path("state/v28_trade_lifecycle_state.json")
    log_path: Path | str = Path("logs/v28_trade_lifecycle.ndjson")
    exit_toll_cents: float = 2.5
    recheck_seconds: float = 5.0
    cheap_entry_max_cents: float = 15.0
    promote_delta_cents: float = 100.0
    disable_bad_settles: int = 3
    min_promote_observations: int = 5

    @property
    def exit_enforce(self) -> bool:
        return self.enabled and self.mode in {"exit_only_enforce", "full_enforce"}

    @property
    def addon_enforce(self) -> bool:
        return self.enabled and self.mode in {"exit_only_enforce", "full_enforce"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finite_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(out):
        return default
    return out


def _finite_int(value: Any, default: int = 0) -> int:
    try:
        out = int(float(value))
    except (TypeError, ValueError):
        return default
    return out


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize_side(side: Any) -> str:
    text = str(side or "").upper()
    if text in {"YES", "NO"}:
        return text
    return ""


class TradeLifecycleController:
    """A small v28 overlay that learns when exits are worth their churn cost."""

    def __init__(self, config: TradeLifecycleConfig):
        self.config = config
        self.state_path = Path(config.state_path)
        self.log_path = Path(config.log_path)
        self.state: dict[str, Any] = self._default_state()
        self._rechecks: dict[str, dict[str, Any]] = {}
        self._addon_cap_log_keys: set[str] = set()
        self.load()

    def _default_state(self) -> dict[str, Any]:
        return {
            "version": 1,
            "created_at": _utc_now_iso(),
            "updated_at": _utc_now_iso(),
            "buckets": {bucket: self._new_bucket_state(bucket) for bucket in BUCKETS},
            "active_positions": {},
            "pending_decisions": {},
        }

    def _new_bucket_state(self, bucket: str) -> dict[str, Any]:
        return {
            "bucket": bucket,
            "observations": 0,
            "wins": 0,
            "losses": 0,
            "bad_settles": 0,
            "net_delta_cents": 0.0,
            "entry_quality_cents": 0.0,
            "exit_quality_cents": 0.0,
            "addon_impact_cents": 0.0,
            "fee_saved_cents": 0.0,
            "promoted": False,
            "disabled": False,
            "last_reward_at": "",
            "disable_reason": "",
            "rewarded_sample_keys": [],
            "bad_sample_keys": [],
        }

    def load(self) -> None:
        if not self.state_path.exists():
            self.save()
            return
        try:
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            self.log_event(
                "lifecycle_state_unreadable",
                {"path": str(self.state_path), "mode": self.config.mode},
            )
            raise
        if isinstance(loaded, dict):
            self.state = self._merge_state(loaded)

    def _merge_state(self, loaded: dict[str, Any]) -> dict[str, Any]:
        state = self._default_state()
        state.update({key: value for key, value in loaded.items() if key not in {"buckets"}})
        buckets = loaded.get("buckets") if isinstance(loaded.get("buckets"), dict) else {}
        for bucket in BUCKETS:
            merged = self._new_bucket_state(bucket)
            if isinstance(buckets.get(bucket), dict):
                merged.update(buckets[bucket])
            if not isinstance(merged.get("rewarded_sample_keys"), list):
                merged["rewarded_sample_keys"] = []
            if not isinstance(merged.get("bad_sample_keys"), list):
                merged["bad_sample_keys"] = []
            state["buckets"][bucket] = merged
        if not isinstance(state.get("active_positions"), dict):
            state["active_positions"] = {}
        if not isinstance(state.get("pending_decisions"), dict):
            state["pending_decisions"] = {}
        return state

    def save(self) -> None:
        self.state["updated_at"] = _utc_now_iso()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self.state, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def log_event(self, event: str, payload: dict[str, Any]) -> None:
        record = {
            "ts": _utc_now_iso(),
            "event": event,
            "enabled": bool(self.config.enabled),
            "mode": self.config.mode,
            **payload,
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def has_pending_market(self, market_ticker: str) -> bool:
        key = str(market_ticker or "")
        pending = self.state.get("pending_decisions", {})
        return isinstance(pending.get(key), list) and bool(pending.get(key))

    def active_bucket(self, market_ticker: str) -> str:
        active = self.state.get("active_positions", {})
        record = active.get(str(market_ticker or "")) if isinstance(active, dict) else None
        if isinstance(record, list):
            record = next((item for item in reversed(record) if isinstance(item, dict)), None)
        if isinstance(record, dict):
            bucket = str(record.get("bucket") or "")
            if bucket in BUCKETS:
                return bucket
        return "uncertain"

    def classify_entry_fill(
        self,
        *,
        market_ticker: str,
        side: str,
        count: float,
        entry_price_cents: float,
        entry_fee_cents: float,
        fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        fields = dict(fields or {})
        bucket, reason = self._classify_entry_bucket(fields, side, entry_price_cents)
        record = {
            "market_ticker": market_ticker,
            "side": _normalize_side(side),
            "count": _finite_float(count),
            "entry_price_cents": _finite_float(entry_price_cents),
            "entry_fee_cents": _finite_float(entry_fee_cents),
            "bucket": bucket,
            "reason": reason,
            "classified_at": _utc_now_iso(),
            "features": self._entry_feature_snapshot(fields, entry_price_cents),
        }
        active = self.state.setdefault("active_positions", {})
        key = str(market_ticker)
        existing = active.get(key)
        if isinstance(existing, list):
            records = [item for item in existing if isinstance(item, dict)]
        elif isinstance(existing, dict):
            records = [existing]
        else:
            records = []
        last = records[-1] if records else None
        if (
            isinstance(last, dict)
            and last.get("side") == record["side"]
            and _finite_float(record.get("count")) > _finite_float(last.get("count"))
        ):
            record["lot_id"] = last.get("lot_id") or f"{key}-lot-{len(records)}"
            records[-1] = record
        else:
            record["lot_id"] = f"{key}-lot-{len(records) + 1}-{int(time.time() * 1000)}"
            records.append(record)
        active[key] = records
        self.save()
        self.log_event("lifecycle_entry_classified", record)
        return record

    def _entry_feature_snapshot(
        self,
        fields: dict[str, Any],
        entry_price_cents: float,
    ) -> dict[str, Any]:
        return {
            "entry_price_cents": _finite_float(entry_price_cents),
            "edge_cents": self._first_float(
                fields,
                "mushroom_v28_phi_memory_adjusted_edge_cents",
                "mushroom_v28_edge_cents",
                "edge_cents",
            ),
            "raw_edge_cents": self._first_float(
                fields,
                "mushroom_v28_raw_edge_cents",
                "mushroom_v28_edge_cents",
                "edge_cents",
            ),
            "abs_d_sigma": abs(
                self._first_float(fields, "mushroom_v28_abs_d_sigma", "abs_d_sigma")
            ),
            "recross_hazard": self._first_float(
                fields,
                "mushroom_v28_recross_hazard",
                "recross_hazard",
            ),
            "p_side": self._first_float(
                fields,
                "mushroom_v28_phi_memory_adjusted_p_side",
                "mushroom_v28_p_side",
                "p_side",
            ),
            "vol_shock_ratio": self._first_float(
                fields,
                "mushroom_v28_vol_shock_ratio",
                "vol_shock_ratio",
                default=1.0,
            ),
        }

    def _classify_entry_bucket(
        self,
        fields: dict[str, Any],
        side: str,
        entry_price_cents: float,
    ) -> tuple[str, str]:
        features = self._entry_feature_snapshot(fields, entry_price_cents)
        edge = features["edge_cents"]
        raw_edge = features["raw_edge_cents"]
        p_side = features["p_side"]
        recross = features["recross_hazard"]
        abs_d = features["abs_d_sigma"]
        vol_shock = features["vol_shock_ratio"]
        cheap = entry_price_cents <= self.config.cheap_entry_max_cents

        if recross >= 0.85 or p_side <= 0.55 or edge <= 0:
            return "danger", "weak_probability_or_high_recross"
        if cheap:
            return "fragile", "cheap_contract_hold_bias"
        if recross >= 0.60 or vol_shock >= 1.25 or edge < self.config.exit_toll_cents:
            return "fragile", "low_margin_or_unstable_path"
        if raw_edge >= self.config.exit_toll_cents * 2.0 and 0.75 <= abs_d <= 1.10 and recross <= 0.45:
            return "settlement_hold", "strong_edge_clean_distance"
        if edge >= self.config.exit_toll_cents and entry_price_cents >= 75:
            return "scalp", "expensive_contract_exit_sensitive"
        if side:
            return "uncertain", "mixed_entry_context"
        return "uncertain", "missing_side"

    def should_cap_addon(
        self,
        *,
        market_ticker: str,
        side: str,
        current_bucket: str | None = None,
        current_count: float | None = None,
    ) -> tuple[bool, str]:
        if not self.config.addon_enforce:
            return False, ""
        bucket = current_bucket if current_bucket in BUCKETS else self.active_bucket(market_ticker)
        if bucket not in {"fragile", "danger"}:
            return False, ""
        payload = {
            "market_ticker": market_ticker,
            "side": _normalize_side(side),
            "bucket": bucket,
            "current_count": _finite_float(current_count, 0.0),
            "action": "cap_addon",
            "reason": f"{bucket}_addon_cap",
            "rewardable": False,
        }
        log_key = "|".join(
            [
                str(market_ticker),
                payload["side"],
                bucket,
                str(round(_finite_float(current_count, 0.0), 6)),
            ]
        )
        if log_key not in self._addon_cap_log_keys:
            self._addon_cap_log_keys.add(log_key)
            self.log_event("lifecycle_addon_capped", payload)
        return True, payload["reason"]

    def apply_exit(
        self,
        *,
        market_ticker: str,
        side: str,
        fields: dict[str, Any],
        position_bucket: str | None = None,
        now_monotonic: float | None = None,
    ) -> tuple[dict[str, Any], bool]:
        out = dict(fields)
        reason = str(out.get("mushroom_v28_exit_reason") or "")
        if not self.config.enabled or not reason:
            return out, False

        bucket = position_bucket if position_bucket in BUCKETS else self.active_bucket(market_ticker)
        if self._bucket_disabled(bucket):
            out.update(
                {
                    "mushroom_v28_lifecycle_bucket": bucket,
                    "mushroom_v28_lifecycle_action": "allow_bucket_disabled",
                    "mushroom_v28_lifecycle_enforced": False,
                }
            )
            self.log_event(
                "lifecycle_exit_decision",
                self._exit_log_payload(market_ticker, side, out, bucket, "allow_bucket_disabled"),
            )
            return out, False

        if self._is_non_overridable(reason):
            out.update(
                {
                    "mushroom_v28_lifecycle_bucket": bucket,
                    "mushroom_v28_lifecycle_action": "allow_non_overridable",
                    "mushroom_v28_lifecycle_enforced": False,
                }
            )
            self.log_event(
                "lifecycle_exit_decision",
                self._exit_log_payload(market_ticker, side, out, bucket, "allow_non_overridable"),
            )
            return out, False

        entry_basis = self._first_float(
            out,
            "mushroom_v28_exit_entry_basis_cents",
            "mushroom_v28_entry_basis_cents",
            "entry_basis_cents",
        )
        exit_net = self._first_float(out, "mushroom_v28_exit_net_cents", "exit_net_cents")
        hold_net = self._first_float(
            out,
            "mushroom_v28_exit_hold_net_cents",
            "mushroom_v28_hold_net_cents",
            "hold_net_cents",
        )
        exit_fee = self._first_float(out, "mushroom_v28_exit_fee_cents", "exit_fee_cents")
        exit_margin = exit_net - hold_net
        effective_toll = max(self.config.exit_toll_cents, exit_fee + 0.5)
        promoted = self._bucket_promoted(bucket)
        action = "allow"
        enforced = False
        defer = False

        if entry_basis <= self.config.cheap_entry_max_cents and self._is_churn_exit(reason):
            action = "suppress_cheap_contract_churn"
            enforced = self.config.exit_enforce
        elif reason.endswith("value_over_hold") and exit_margin < effective_toll and not promoted:
            action = "suppress_below_exit_toll"
            enforced = self.config.exit_enforce
        elif bucket == "settlement_hold" and self._is_reduce_exit(reason) and exit_margin < effective_toll and not promoted:
            action = "suppress_settlement_hold_reduce_churn"
            enforced = self.config.exit_enforce
        elif bucket == "uncertain" and self._is_reduce_exit(reason):
            action, enforced, defer = self._uncertain_recheck_action(
                market_ticker=market_ticker,
                side=side,
                reason=reason,
                now_monotonic=now_monotonic,
            )

        out.update(
            {
                "mushroom_v28_lifecycle_bucket": bucket,
                "mushroom_v28_lifecycle_action": action,
                "mushroom_v28_lifecycle_exit_margin_cents": exit_margin,
                "mushroom_v28_lifecycle_effective_toll_cents": effective_toll,
                "mushroom_v28_lifecycle_promoted": promoted,
                "mushroom_v28_lifecycle_enforced": bool(enforced),
            }
        )
        payload = self._exit_log_payload(market_ticker, side, out, bucket, action)
        if action.startswith("suppress") or action.startswith("delay"):
            decision_count = self._first_float(
                out,
                "position_count",
                "mushroom_v28_exit_count",
                "mushroom_v28_exit_target_count",
                "mushroom_v28_position_count",
                default=1.0,
            )
            self._append_pending(
                market_ticker,
                {
                    "kind": "exit_change",
                    "market_ticker": market_ticker,
                    "bucket": bucket,
                    "side": _normalize_side(side),
                    "raw_reason": reason,
                    "action": action,
                    "enforced": bool(enforced),
                    "raw_exit_value_cents": exit_net,
                    "raw_hold_net_cents": hold_net,
                    "raw_exit_fee_cents": exit_fee,
                    "fee_saved_cents": max(0.0, exit_fee) * max(1.0, decision_count),
                    "entry_basis_cents": entry_basis,
                    "count": decision_count,
                    "ts": _utc_now_iso(),
                },
            )
            self.save()

        self.log_event("lifecycle_exit_decision", payload)
        if enforced and action.startswith("suppress"):
            out["mushroom_v28_exit_reason_before_lifecycle"] = reason
            out["mushroom_v28_exit_reason"] = ""
            out["mushroom_v28_exit_target_cents_before_lifecycle"] = out.get("mushroom_v28_exit_target_cents")
            out["mushroom_v28_exit_target_cents"] = None
            return out, False
        if enforced and defer:
            out["mushroom_v28_exit_reason_before_lifecycle"] = reason
            out["mushroom_v28_exit_reason"] = ""
            out["mushroom_v28_exit_target_cents_before_lifecycle"] = out.get("mushroom_v28_exit_target_cents")
            out["mushroom_v28_exit_target_cents"] = None
            return out, True
        return out, False

    def _uncertain_recheck_action(
        self,
        *,
        market_ticker: str,
        side: str,
        reason: str,
        now_monotonic: float | None,
    ) -> tuple[str, bool, bool]:
        now = float(time.monotonic() if now_monotonic is None else now_monotonic)
        key = f"{market_ticker}|{_normalize_side(side)}|{reason}"
        record = self._rechecks.get(key)
        if record is None:
            self._rechecks[key] = {"first_seen": now, "last_seen": now}
            return "delay_uncertain_recheck", self.config.exit_enforce, True
        record["last_seen"] = now
        elapsed = now - _finite_float(record.get("first_seen"))
        if elapsed < self.config.recheck_seconds:
            return "delay_uncertain_recheck", self.config.exit_enforce, True
        self._rechecks.pop(key, None)
        return "allow_after_uncertain_recheck", False, False

    def _exit_log_payload(
        self,
        market_ticker: str,
        side: str,
        fields: dict[str, Any],
        bucket: str,
        action: str,
    ) -> dict[str, Any]:
        return {
            "market_ticker": market_ticker,
            "side": _normalize_side(side),
            "bucket": bucket,
            "action": action,
            "raw_reason": fields.get("mushroom_v28_exit_reason"),
            "target_cents": fields.get("mushroom_v28_exit_target_cents"),
            "exit_net_cents": fields.get("mushroom_v28_exit_net_cents"),
            "hold_net_cents": fields.get("mushroom_v28_exit_hold_net_cents"),
            "exit_margin_cents": fields.get("mushroom_v28_lifecycle_exit_margin_cents"),
            "effective_toll_cents": fields.get("mushroom_v28_lifecycle_effective_toll_cents"),
            "enforced": fields.get("mushroom_v28_lifecycle_enforced"),
        }

    def learn_from_settlement(
        self,
        *,
        market_ticker: str,
        result: str,
        actual_pnl_cents: float | None = None,
        outcome_record: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        pending = self.state.setdefault("pending_decisions", {}).pop(str(market_ticker), [])
        active = self.state.setdefault("active_positions", {}).pop(str(market_ticker), None)
        if isinstance(active, list):
            active_records = [item for item in active if isinstance(item, dict)]
        elif isinstance(active, dict):
            active_records = [active]
        else:
            active_records = []
        if not pending and not active_records:
            self.save()
            return None

        result_side = _normalize_side(result)
        total_delta = 0.0
        component_totals = {
            "entry_quality_cents": 0.0,
            "exit_quality_cents": 0.0,
            "addon_impact_cents": 0.0,
            "fee_saved_cents": 0.0,
        }
        rewards: list[dict[str, Any]] = []
        for decision in pending:
            if not isinstance(decision, dict):
                continue
            reward = self._decision_reward(decision, result_side, outcome_record)
            if reward is None:
                continue
            bucket = reward["bucket"]
            if not self._apply_bucket_reward(bucket, reward):
                continue
            rewards.append(reward)
            total_delta += reward["delta_cents"]
            for key in component_totals:
                component_totals[key] += _finite_float(reward.get(key), 0.0)

        if active_records and not rewards:
            active_record = active_records[-1]
            bucket = str(active_record.get("bucket") or "uncertain")
            if bucket not in BUCKETS:
                bucket = "uncertain"
            side = _normalize_side(active_record.get("side"))
            entry_price = _finite_float(active_record.get("entry_price_cents"))
            entry_fee = _finite_float(active_record.get("entry_fee_cents"))
            count = _finite_float(active_record.get("count"), 1.0)
            settle = 100.0 if side == result_side else 0.0
            realized_delta = ((settle - entry_price) * count) - entry_fee
            clipped_delta = _clamp(realized_delta, -300.0, 300.0)
            reward = {
                "kind": "entry_settlement",
                "bucket": bucket,
                "sample_key": "|".join(
                    [
                        "entry_settlement",
                        str(market_ticker),
                        str(active_record.get("lot_id") or ""),
                        bucket,
                        side,
                    ]
                ),
                "delta_cents": clipped_delta,
                "entry_quality_cents": clipped_delta,
                "exit_quality_cents": 0.0,
                "addon_impact_cents": 0.0,
                "fee_saved_cents": 0.0,
                "side": side,
                "result": result_side,
            }
            if self._apply_bucket_reward(bucket, reward):
                rewards.append(reward)
                total_delta += clipped_delta
                component_totals["entry_quality_cents"] += clipped_delta

        self.save()
        payload = {
            "market_ticker": market_ticker,
            "result": result_side,
            "actual_pnl_cents": actual_pnl_cents,
            "outcome_record": outcome_record,
            "reward_delta_cents": total_delta,
            "rewards": rewards,
            **component_totals,
        }
        self.log_event("lifecycle_settlement_reward", payload)
        return payload

    def _decision_reward(
        self,
        decision: dict[str, Any],
        result_side: str,
        outcome_record: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        kind = str(decision.get("kind") or "")
        bucket = str(decision.get("bucket") or "uncertain")
        if bucket not in BUCKETS:
            bucket = "uncertain"
        side = _normalize_side(decision.get("side"))
        count = max(1.0, _finite_float(decision.get("count"), 1.0))
        settlement_value = (100.0 if side == result_side else 0.0) * count
        if kind == "exit_change":
            raw_exit_value = _finite_float(decision.get("raw_exit_value_cents")) * count
            lifecycle_value = self._lifecycle_value_after_exit_decision_cents(
                decision,
                result_side,
                outcome_record,
                count,
            )
            delta = _clamp(lifecycle_value - raw_exit_value, -300.0, 300.0)
            return {
                "kind": kind,
                "bucket": bucket,
                "sample_key": str(decision.get("sample_key") or decision.get("decision_key") or ""),
                "delta_cents": delta,
                "entry_quality_cents": 0.0,
                "exit_quality_cents": delta,
                "addon_impact_cents": 0.0,
                "fee_saved_cents": _finite_float(decision.get("fee_saved_cents")),
                "side": side,
                "result": result_side,
            }
        if kind == "addon_cap":
            if not bool(decision.get("rewardable")):
                return None
            entry_price = _finite_float(decision.get("entry_price_cents"))
            entry_fee = _finite_float(decision.get("entry_fee_cents"))
            if entry_price <= 0:
                return None
            raw_addon_pnl = settlement_value - ((entry_price + entry_fee) * count)
            delta = _clamp(-raw_addon_pnl, -300.0, 300.0)
            return {
                "kind": kind,
                "bucket": bucket,
                "sample_key": str(decision.get("sample_key") or decision.get("decision_key") or ""),
                "delta_cents": delta,
                "entry_quality_cents": 0.0,
                "exit_quality_cents": 0.0,
                "addon_impact_cents": delta,
                "fee_saved_cents": 0.0,
                "side": side,
                "result": result_side,
            }
        return None

    def _lifecycle_value_after_exit_decision_cents(
        self,
        decision: dict[str, Any],
        result_side: str,
        outcome_record: dict[str, Any] | None,
        count: float,
    ) -> float:
        side = _normalize_side(decision.get("side"))
        settlement_value_per_contract = 100.0 if side == result_side else 0.0
        if isinstance(outcome_record, dict):
            side_cashflows = outcome_record.get("side_cashflows")
            side_record = None
            if isinstance(side_cashflows, dict):
                side_record = side_cashflows.get(side.lower())
            if isinstance(side_record, dict):
                exit_qty = _finite_float(side_record.get("exit_qty"))
                if exit_qty > 0:
                    exit_notional = _finite_float(side_record.get("exit_notional_cents"))
                    exit_fee = _finite_float(side_record.get("exit_fee_cents"))
                    avg_exit_net = (exit_notional - exit_fee) / exit_qty
                    exited_count = min(count, exit_qty)
                    settled_count = max(0.0, count - exited_count)
                    return (avg_exit_net * exited_count) + (settlement_value_per_contract * settled_count)
        return settlement_value_per_contract * count

    def _apply_bucket_reward(self, bucket: str, reward: dict[str, Any]) -> bool:
        state = self.state.setdefault("buckets", {}).setdefault(bucket, self._new_bucket_state(bucket))
        rewarded_keys = state.setdefault("rewarded_sample_keys", [])
        if not isinstance(rewarded_keys, list):
            rewarded_keys = []
            state["rewarded_sample_keys"] = rewarded_keys
        sample_key = str(reward.get("sample_key") or "")
        if sample_key and sample_key in rewarded_keys:
            return False
        if sample_key:
            rewarded_keys.append(sample_key)
            if len(rewarded_keys) > 1000:
                del rewarded_keys[:-1000]
        delta = _finite_float(reward.get("delta_cents"))
        state["observations"] = _finite_int(state.get("observations")) + 1
        state["net_delta_cents"] = _finite_float(state.get("net_delta_cents")) + delta
        state["entry_quality_cents"] = _finite_float(state.get("entry_quality_cents")) + _finite_float(
            reward.get("entry_quality_cents")
        )
        state["exit_quality_cents"] = _finite_float(state.get("exit_quality_cents")) + _finite_float(
            reward.get("exit_quality_cents")
        )
        state["addon_impact_cents"] = _finite_float(state.get("addon_impact_cents")) + _finite_float(
            reward.get("addon_impact_cents")
        )
        state["fee_saved_cents"] = _finite_float(state.get("fee_saved_cents")) + _finite_float(
            reward.get("fee_saved_cents")
        )
        if delta > 0:
            state["wins"] = _finite_int(state.get("wins")) + 1
        elif delta < 0:
            state["losses"] = _finite_int(state.get("losses")) + 1
            bad_keys = state.setdefault("bad_sample_keys", [])
            if not isinstance(bad_keys, list):
                bad_keys = []
                state["bad_sample_keys"] = bad_keys
            bad_key = sample_key or f"{reward.get('kind')}|{bucket}|{state['observations']}"
            if bad_key not in bad_keys:
                bad_keys.append(bad_key)
            state["bad_settles"] = len(bad_keys)
        min_promote = max(1, int(self.config.min_promote_observations))
        if (
            _finite_float(state.get("net_delta_cents")) >= self.config.promote_delta_cents
            and _finite_int(state.get("observations")) >= min_promote
        ):
            state["promoted"] = True
        if (
            _finite_int(state.get("bad_settles")) >= self.config.disable_bad_settles
            and _finite_float(state.get("net_delta_cents")) < 0
        ):
            state["disabled"] = True
            state["disable_reason"] = "bad_settle_threshold"
        state["last_reward_at"] = _utc_now_iso()
        return True

    def _append_pending(self, market_ticker: str, decision: dict[str, Any]) -> None:
        key = str(market_ticker)
        pending = self.state.setdefault("pending_decisions", {}).setdefault(key, [])
        if not isinstance(pending, list):
            pending = []
            self.state.setdefault("pending_decisions", {})[key] = pending
        decision = dict(decision)
        decision["market_ticker"] = key
        decision_key = self._pending_decision_key(key, decision)
        decision["decision_key"] = decision_key
        decision["sample_key"] = decision_key
        now = _utc_now_iso()
        for existing in pending:
            if isinstance(existing, dict) and existing.get("decision_key") == decision_key:
                existing["seen_count"] = _finite_int(existing.get("seen_count"), 1) + 1
                existing["latest_seen_ts"] = now
                return
        decision.setdefault("first_seen_ts", now)
        decision.setdefault("latest_seen_ts", decision.get("ts") or now)
        decision.setdefault("seen_count", 1)
        pending.append(decision)

    def _pending_decision_key(self, market_ticker: str, decision: dict[str, Any]) -> str:
        parts = [
            str(decision.get("kind") or ""),
            str(market_ticker),
            str(decision.get("bucket") or ""),
            _normalize_side(decision.get("side")),
            str(decision.get("raw_reason") or ""),
            str(decision.get("action") or ""),
            str(round(max(1.0, _finite_float(decision.get("count"), 1.0)), 6)),
        ]
        return "|".join(parts)

    def _bucket_state(self, bucket: str) -> dict[str, Any]:
        buckets = self.state.setdefault("buckets", {})
        if bucket not in buckets or not isinstance(buckets.get(bucket), dict):
            buckets[bucket] = self._new_bucket_state(bucket)
        return buckets[bucket]

    def _bucket_promoted(self, bucket: str) -> bool:
        return bool(self._bucket_state(bucket).get("promoted"))

    def _bucket_disabled(self, bucket: str) -> bool:
        return bool(self._bucket_state(bucket).get("disabled"))

    def _is_non_overridable(self, reason: str) -> bool:
        text = str(reason or "").lower()
        return any(token in text for token in NON_OVERRIDABLE_REASON_TOKENS)

    def _is_churn_exit(self, reason: str) -> bool:
        text = str(reason or "").lower()
        return "value_over_hold" in text or "reduce" in text or "drawdown" in text

    def _is_reduce_exit(self, reason: str) -> bool:
        text = str(reason or "").lower()
        return "reduce" in text or "value_over_hold" in text or "drawdown" in text

    def _first_float(self, fields: dict[str, Any], *keys: str, default: float = 0.0) -> float:
        for key in keys:
            if key in fields and fields.get(key) is not None:
                return _finite_float(fields.get(key), default)
        return default

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": bool(self.config.enabled),
            "mode": self.config.mode,
            "exit_toll_cents": self.config.exit_toll_cents,
            "recheck_seconds": self.config.recheck_seconds,
            "cheap_entry_max_cents": self.config.cheap_entry_max_cents,
            "promote_delta_cents": self.config.promote_delta_cents,
            "disable_bad_settles": self.config.disable_bad_settles,
            "min_promote_observations": self.config.min_promote_observations,
            "state_path": str(self.state_path),
            "log_path": str(self.log_path),
            "buckets": self.state.get("buckets", {}),
            "active_positions": self.state.get("active_positions", {}),
            "pending_market_count": len(self.state.get("pending_decisions", {}) or {}),
        }

    def to_jsonable_config(self) -> dict[str, Any]:
        config_dict = asdict(self.config)
        config_dict["state_path"] = str(config_dict["state_path"])
        config_dict["log_path"] = str(config_dict["log_path"])
        return config_dict
