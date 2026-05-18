from __future__ import annotations

import json
import math
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHEAP_NO_COLLAPSE_BUCKET = "cheap_no_collapse_le15"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        result = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(result):
        return default
    return result


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


@dataclass(frozen=True)
class AdaptiveExitSupervisorConfig:
    enabled: bool = False
    mode: str = "shadow"
    cheap_no_entry_max_cents: float = 15.0
    reduce_fraction: float = 0.5
    recheck_seconds: float = 5.0
    panic_p_hold_floor: float = 0.03
    disable_min_observations: int = 3
    disable_delta_cents: float = -150.0
    restore_min_observations: int = 5
    restore_delta_cents: float = 150.0

    @property
    def enforce(self) -> bool:
        return self.enabled and self.mode.strip().lower() == "enforce"


class AdaptiveExitSupervisor:
    """Narrow live guard for v28 collapse exits.

    This intentionally does not learn broad entry/exit strategy behavior. It only
    tests one observed failure mode: cheap NO `probability_collapse_full` exits
    that have been giving up large settlement convexity.
    """

    def __init__(self, *, config: AdaptiveExitSupervisorConfig, state_path: Path, log_path: Path) -> None:
        self.config = config
        self.state_path = Path(state_path)
        self.log_path = Path(log_path)
        self.state_unreadable = False
        self._save_lock = threading.RLock()
        self._rechecks: dict[str, float] = {}
        self.state = self._load_state()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if self.config.enabled:
            self.save()
            self.log_event(
                "adaptive_exit_startup",
                effective_mode=self.effective_mode(),
                mode=self.config.mode,
                cheap_no_entry_max_cents=float(self.config.cheap_no_entry_max_cents),
                reduce_fraction=float(self.config.reduce_fraction),
                recheck_seconds=float(self.config.recheck_seconds),
                panic_p_hold_floor=float(self.config.panic_p_hold_floor),
            )

    def _default_state(self) -> dict[str, Any]:
        now = utc_now_iso()
        return {
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "buckets": {},
            "pending_markets": {},
            "protected_runners": {},
        }

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self._default_state()
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            self.state_unreadable = True
            return self._default_state()
        if not isinstance(raw, dict):
            self.state_unreadable = True
            return self._default_state()
        raw.setdefault("buckets", {})
        raw.setdefault("pending_markets", {})
        raw.setdefault("protected_runners", {})
        return raw

    def save(self) -> None:
        if self.state_unreadable:
            return
        with self._save_lock:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state["updated_at"] = utc_now_iso()
            payload = json.dumps(self.state, indent=2, sort_keys=True)
            for attempt in range(5):
                tmp_path = ""
                try:
                    with tempfile.NamedTemporaryFile(
                        "w",
                        encoding="utf-8",
                        dir=str(self.state_path.parent),
                        delete=False,
                    ) as tmp:
                        tmp.write(payload)
                        tmp.flush()
                        os.fsync(tmp.fileno())
                        tmp_path = tmp.name
                    os.replace(tmp_path, self.state_path)
                    return
                except OSError:
                    if tmp_path:
                        try:
                            Path(tmp_path).unlink(missing_ok=True)
                        except OSError:
                            pass
                    time.sleep(0.05 * (attempt + 1))

    def log_event(self, event_type: str, **payload: Any) -> None:
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts_wall": utc_now_iso(), "event_type": event_type, **payload}, sort_keys=True, default=str) + "\n")

    def effective_mode(self) -> str:
        if not self.config.enabled:
            return "disabled"
        if self.state_unreadable:
            return "shadow"
        return "enforce" if self.config.enforce else "shadow"

    def _bucket_state(self, bucket: str) -> dict[str, Any]:
        buckets = self.state.setdefault("buckets", {})
        state = buckets.setdefault(
            bucket,
            {
                "observations": 0,
                "delta_cents": 0.0,
                "wins": 0,
                "losses": 0,
                "live_observations": 0,
                "live_delta_cents": 0.0,
                "disabled": False,
                "disable_reason": "",
                "disabled_shadow_observations": 0,
                "disabled_shadow_delta_cents": 0.0,
            },
        )
        return state

    def _is_bucket_disabled(self, bucket: str) -> bool:
        return coerce_bool(self._bucket_state(bucket).get("disabled"))

    def _runner_key(self, market: str, side: str) -> str:
        return f"{str(market).strip()}:{str(side).strip().lower()}"

    def _record_pending(self, *, market: str, decision: dict[str, Any]) -> None:
        if not market or self.state_unreadable:
            return
        pending = self.state.setdefault("pending_markets", {})
        bucket = pending.setdefault(market, {"decisions": [], "first_seen": utc_now_iso(), "last_seen": utc_now_iso()})
        bucket["last_seen"] = utc_now_iso()
        decisions = bucket.setdefault("decisions", [])
        key = (
            decision.get("bucket"),
            decision.get("side"),
            decision.get("raw_reason"),
            int(coerce_float(decision.get("raw_qty"), 0.0)),
            int(coerce_float(decision.get("adjusted_target_count"), 0.0)),
            coerce_bool(decision.get("enforced")),
            str(decision.get("action") or ""),
        )
        for existing in decisions[-8:]:
            existing_key = (
                existing.get("bucket"),
                existing.get("side"),
                existing.get("raw_reason"),
                int(coerce_float(existing.get("raw_qty"), 0.0)),
                int(coerce_float(existing.get("adjusted_target_count"), 0.0)),
                coerce_bool(existing.get("enforced")),
                str(existing.get("action") or ""),
            )
            if existing_key == key:
                return
        decisions.append(decision)
        bucket["decisions"] = decisions[-64:]
        if len(pending) > 512:
            for key_to_drop in sorted(pending.keys())[:-512]:
                pending.pop(key_to_drop, None)
        self.save()

    def apply_exit(
        self,
        *,
        market: str,
        fields: dict[str, Any],
        now_monotonic: float | None = None,
    ) -> tuple[dict[str, Any], bool]:
        if not self.config.enabled:
            return fields, False
        now = time.monotonic() if now_monotonic is None else float(now_monotonic)
        side = str(fields.get("mushroom_v28_side") or "").strip().lower()
        raw_reason = str(fields.get("mushroom_v28_exit_reason") or "")
        raw_target_count = max(0, int(coerce_float(fields.get("mushroom_v28_exit_target_count"), 0.0)))
        qty = max(0, int(coerce_float(fields.get("mushroom_v28_position_count"), raw_target_count)))
        entry_basis = coerce_float(fields.get("mushroom_v28_entry_basis_cents"), 0.0)
        bid = coerce_float(fields.get("mushroom_v28_exit_bid_cents"), 0.0)
        fee = coerce_float(fields.get("mushroom_v28_exit_fee_cents"), 0.0)
        p_hold = coerce_float(fields.get("mushroom_v28_p_hold"), 1.0)
        bucket = ""
        qualified = (
            raw_reason == "mushroom_v28_probability_collapse_full"
            and side == "no"
            and 0.0 < entry_basis <= float(self.config.cheap_no_entry_max_cents)
            and qty > 0
            and raw_target_count > 0
        )
        if qualified:
            bucket = CHEAP_NO_COLLAPSE_BUCKET
        bucket_state = self._bucket_state(bucket) if bucket else {}
        disabled = bool(bucket and self._is_bucket_disabled(bucket))
        protected_key = self._runner_key(market, side)
        protected = coerce_bool(self.state.setdefault("protected_runners", {}).get(protected_key))
        effective_mode = self.effective_mode()
        enforced = effective_mode == "enforce" and qualified and not disabled and p_hold > float(self.config.panic_p_hold_floor)
        reduce_count = min(qty, max(1, int(math.ceil(qty * float(self.config.reduce_fraction))))) if qty > 0 else 0
        action = "observe"
        adjusted_reason = raw_reason
        adjusted_target = raw_target_count
        defer = False
        if qualified:
            if enforced and qty <= 1 and protected:
                action = "protect_runner_hold"
                adjusted_reason = ""
                adjusted_target = 0
            elif enforced and reduce_count < qty:
                recheck_key = f"{self._runner_key(market, side)}:{raw_reason}:{qty}:{int(entry_basis)}"
                first_seen = self._rechecks.get(recheck_key)
                if first_seen is None:
                    self._rechecks[recheck_key] = now
                    action = "recheck_defer"
                    adjusted_reason = ""
                    adjusted_target = 0
                    defer = True
                elif now - first_seen < float(self.config.recheck_seconds):
                    action = "recheck_wait"
                    adjusted_reason = ""
                    adjusted_target = 0
                    defer = True
                else:
                    action = "collapse_to_reduce"
                    adjusted_reason = "mushroom_v28_adaptive_collapse_reduce"
                    adjusted_target = reduce_count
                    self._rechecks.pop(recheck_key, None)
                    self.state.setdefault("protected_runners", {})[protected_key] = True
            elif disabled:
                action = "shadow_disabled"
            elif p_hold <= float(self.config.panic_p_hold_floor):
                action = "panic_full_exit"
            else:
                action = "shadow_reduce" if effective_mode == "shadow" and reduce_count < qty else "raw_full"
            if not defer and action in {"collapse_to_reduce", "protect_runner_hold", "shadow_reduce", "shadow_disabled"}:
                held_count = max(0, qty - adjusted_target)
                if action in {"shadow_reduce", "shadow_disabled"}:
                    held_count = max(0, qty - reduce_count)
                self._record_pending(
                    market=market,
                    decision={
                        "bucket": bucket,
                        "side": side,
                        "raw_reason": raw_reason,
                        "action": action,
                        "enforced": action in {"collapse_to_reduce", "protect_runner_hold"},
                        "raw_qty": qty,
                        "raw_target_count": raw_target_count,
                        "adjusted_target_count": adjusted_target if action != "shadow_disabled" else reduce_count,
                        "held_count": held_count,
                        "entry_basis_cents": entry_basis,
                        "bid_cents": bid,
                        "fee_cents_per_contract": fee,
                        "p_hold": p_hold,
                    },
                )
            if action in {"recheck_defer", "recheck_wait", "collapse_to_reduce", "protect_runner_hold"}:
                fields["mushroom_v28_exit_reason"] = adjusted_reason
                fields["mushroom_v28_exit_target_count"] = adjusted_target
                self.save()

        fields.update(
            {
                "mushroom_v28_adaptive_exit_enabled": bool(self.config.enabled),
                "mushroom_v28_adaptive_exit_mode": self.config.mode,
                "mushroom_v28_adaptive_exit_effective_mode": effective_mode,
                "mushroom_v28_adaptive_exit_bucket": bucket,
                "mushroom_v28_adaptive_exit_bucket_disabled": disabled,
                "mushroom_v28_adaptive_exit_bucket_observations": int(coerce_float(bucket_state.get("observations"), 0.0)) if bucket_state else 0,
                "mushroom_v28_adaptive_exit_bucket_delta_cents": round(coerce_float(bucket_state.get("delta_cents"), 0.0), 4) if bucket_state else 0.0,
                "mushroom_v28_adaptive_exit_qualified": bool(qualified),
                "mushroom_v28_adaptive_exit_action": action,
                "mushroom_v28_adaptive_exit_raw_reason": raw_reason,
                "mushroom_v28_adaptive_exit_raw_target_count": raw_target_count,
                "mushroom_v28_adaptive_exit_adjusted_reason": adjusted_reason,
                "mushroom_v28_adaptive_exit_adjusted_target_count": adjusted_target,
                "mushroom_v28_adaptive_exit_reduce_target_count": reduce_count,
                "mushroom_v28_adaptive_exit_protected_runner": bool(protected),
                "mushroom_v28_adaptive_exit_panic_floor": float(self.config.panic_p_hold_floor),
            }
        )
        if qualified or raw_reason == "mushroom_v28_probability_collapse_full":
            self.log_event(
                "adaptive_exit_decision",
                market=market,
                side=side,
                bucket=bucket,
                qualified=qualified,
                action=action,
                raw_reason=raw_reason,
                raw_target_count=raw_target_count,
                adjusted_reason=adjusted_reason,
                adjusted_target_count=adjusted_target,
                reduce_target_count=reduce_count,
                qty=qty,
                entry_basis_cents=round(entry_basis, 6),
                bid_cents=round(bid, 6),
                fee_cents_per_contract=round(fee, 6),
                p_hold=round(p_hold, 6),
                effective_mode=effective_mode,
                bucket_disabled=disabled,
                defer=defer,
            )
        return fields, defer

    def learn_from_settlement(self, *, market: str, result: str) -> dict[str, Any]:
        normalized = str(result or "").strip().lower()
        if normalized not in {"yes", "no", "void"}:
            return {"updated": False, "reason": "unresolved_result"}
        if self.state_unreadable:
            return {"updated": False, "reason": "state_unreadable"}
        pending = self.state.setdefault("pending_markets", {})
        bucket = pending.pop(market, None)
        decisions = list((bucket or {}).get("decisions") or [])
        total_delta = 0.0
        used = 0
        if normalized != "void":
            for decision in decisions:
                decision_bucket = str(decision.get("bucket") or "")
                if not decision_bucket:
                    continue
                side = str(decision.get("side") or "").strip().lower()
                if side not in {"yes", "no"}:
                    continue
                raw_qty = max(1, int(coerce_float(decision.get("raw_qty"), 1.0)))
                adjusted_target = max(0, min(raw_qty, int(coerce_float(decision.get("adjusted_target_count"), 0.0))))
                held_count = max(0, min(raw_qty, int(coerce_float(decision.get("held_count"), raw_qty - adjusted_target))))
                entry_basis = coerce_float(decision.get("entry_basis_cents"), 0.0)
                bid = coerce_float(decision.get("bid_cents"), 0.0)
                fee = coerce_float(decision.get("fee_cents_per_contract"), 0.0)
                if entry_basis <= 0 or bid <= 0:
                    continue
                settlement = 100.0 if normalized == side else 0.0
                raw_full_pnl = (bid - entry_basis - fee) * raw_qty
                adjusted_pnl = (bid - entry_basis - fee) * adjusted_target + (settlement - entry_basis) * held_count
                delta = adjusted_pnl - raw_full_pnl
                stats = self._bucket_state(decision_bucket)
                stats["observations"] = int(coerce_float(stats.get("observations"), 0.0)) + 1
                stats["delta_cents"] = round(coerce_float(stats.get("delta_cents"), 0.0) + delta, 4)
                if delta > 0:
                    stats["wins"] = int(coerce_float(stats.get("wins"), 0.0)) + 1
                elif delta < 0:
                    stats["losses"] = int(coerce_float(stats.get("losses"), 0.0)) + 1
                if coerce_bool(decision.get("enforced")):
                    stats["live_observations"] = int(coerce_float(stats.get("live_observations"), 0.0)) + 1
                    stats["live_delta_cents"] = round(coerce_float(stats.get("live_delta_cents"), 0.0) + delta, 4)
                elif coerce_bool(stats.get("disabled")):
                    stats["disabled_shadow_observations"] = int(coerce_float(stats.get("disabled_shadow_observations"), 0.0)) + 1
                    stats["disabled_shadow_delta_cents"] = round(coerce_float(stats.get("disabled_shadow_delta_cents"), 0.0) + delta, 4)
                self._maybe_update_bucket_mode(decision_bucket, stats)
                used += 1
                total_delta += delta
        for key in list(self.state.setdefault("protected_runners", {}).keys()):
            if str(key).startswith(f"{market}:"):
                self.state["protected_runners"].pop(key, None)
        self.save()
        self.log_event(
            "adaptive_exit_settlement",
            market=market,
            result=normalized,
            decision_count=len(decisions),
            used_decision_count=used,
            delta_cents=round(total_delta, 4),
            buckets=self.state.get("buckets", {}),
        )
        return {
            "updated": bool(decisions),
            "decision_count": len(decisions),
            "used_decision_count": used,
            "delta_cents": round(total_delta, 4),
        }

    def _maybe_update_bucket_mode(self, bucket: str, stats: dict[str, Any]) -> None:
        disabled = coerce_bool(stats.get("disabled"))
        live_obs = int(coerce_float(stats.get("live_observations"), 0.0))
        live_delta = coerce_float(stats.get("live_delta_cents"), 0.0)
        if not disabled and live_obs >= int(self.config.disable_min_observations) and live_delta <= float(self.config.disable_delta_cents):
            stats["disabled"] = True
            stats["disable_reason"] = "live_delta_guard"
            stats["disabled_shadow_observations"] = 0
            stats["disabled_shadow_delta_cents"] = 0.0
            self.log_event(
                "adaptive_exit_bucket_disabled",
                bucket=bucket,
                live_observations=live_obs,
                live_delta_cents=round(live_delta, 4),
            )
            return
        if disabled:
            shadow_obs = int(coerce_float(stats.get("disabled_shadow_observations"), 0.0))
            shadow_delta = coerce_float(stats.get("disabled_shadow_delta_cents"), 0.0)
            if shadow_obs >= int(self.config.restore_min_observations) and shadow_delta >= float(self.config.restore_delta_cents):
                stats["disabled"] = False
                stats["disable_reason"] = ""
                stats["live_observations"] = 0
                stats["live_delta_cents"] = 0.0
                stats["disabled_shadow_observations"] = 0
                stats["disabled_shadow_delta_cents"] = 0.0
                self.log_event(
                    "adaptive_exit_bucket_restored",
                    bucket=bucket,
                    shadow_observations=shadow_obs,
                    shadow_delta_cents=round(shadow_delta, 4),
                )
