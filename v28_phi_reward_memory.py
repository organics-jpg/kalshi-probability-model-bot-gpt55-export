from __future__ import annotations

import json
import math
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PHI = (1.0 + math.sqrt(5.0)) / 2.0
TREND_WINDOWS_MINUTES = (5, 15, 60, 180, 1440)
TREND_LABELS = ("5m", "15m", "1h", "3h", "1d")
FEATURE_NAMES = (
    "bias",
    "phi_trend_side",
    "phi_trend_abs",
    "trend_5m_side",
    "trend_15m_side",
    "trend_1h_side",
    "edge_margin",
    "edge_near_floor",
    "abs_d_center",
    "abs_d_high",
    "recross_hazard",
    "volshock",
    "book_age_ratio",
    "ask_level",
    "seconds_to_close",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, float(value)))


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


def phi_trend_weights() -> dict[str, float]:
    raw = [PHI ** -i for i in range(len(TREND_LABELS))]
    total = sum(raw)
    return {label: weight / total for label, weight in zip(TREND_LABELS, raw)}


def weighted_phi_trend(trends: dict[str, float]) -> float:
    weights = phi_trend_weights()
    return sum(weights[label] * coerce_float(trends.get(label), 0.0) for label in TREND_LABELS)


def compute_trend_context_from_engine(engine: Any) -> dict[str, float]:
    """Return sigma-normalized BTC trend features for fixed phi windows."""
    try:
        spot = float(engine.current_spot())
    except Exception:
        return {label: 0.0 for label in TREND_LABELS} | {"phi": 0.0}
    trends: dict[str, float] = {}
    for label, minutes in zip(TREND_LABELS, TREND_WINDOWS_MINUTES):
        try:
            past = float(engine.get_close_lag(int(minutes)))
            sigma = float(engine.current_sigma_dollars(float(minutes), spot=spot))
        except Exception:
            past = float("nan")
            sigma = float("nan")
        if not math.isfinite(past) or past <= 0 or not math.isfinite(sigma) or sigma <= 0:
            trends[label] = 0.0
        else:
            z_move = (spot - past) / max(1e-9, sigma)
            trends[label] = clamp(math.tanh(z_move / 2.0), -1.0, 1.0)
    trends["phi"] = clamp(weighted_phi_trend(trends), -1.0, 1.0)
    return trends


@dataclass(frozen=True)
class PhiRewardMemoryConfig:
    enabled: bool = False
    mode: str = "shadow"
    max_entry_correction_cents: float = 1.0
    max_exit_correction_cents: float = 2.0
    allow_add_entries: bool = True
    allow_size_increase: bool = True
    allow_side_flip_live: bool = False
    kill_switch: bool = False
    kill_net_pnl_dollars: float = -4.0
    kill_loss_cluster: int = 6
    report_interval_seconds: float = 900.0
    decay_period_seconds: float = 6.0 * 60.0 * 60.0
    learn_rate: float = 0.006
    regularization: float = 0.015
    max_weight_cents: float = 2.0
    reward_clip_cents: float = 200.0
    near_edge_min_cents: float = 2.0
    near_depth_ratio_min: float = 6.0
    required_depth_ratio: float = 8.0
    near_abs_d_min: float = 0.75
    near_abs_d_max: float = 1.15
    rich_exit_recheck_bid_cents: int = 80
    rich_exit_recheck_seconds: float = 5.0
    unfilled_signal_label_cents: float = 5.0

    @property
    def enforce(self) -> bool:
        return self.enabled and self.mode.strip().lower() == "enforce"


class PhiRewardMemoryController:
    def __init__(self, *, config: PhiRewardMemoryConfig, state_path: Path, log_path: Path) -> None:
        self.config = config
        self.state_path = Path(state_path)
        self.log_path = Path(log_path)
        self.state_unreadable = False
        self._save_lock = threading.RLock()
        self.state = self._load_state()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _default_state(self) -> dict[str, Any]:
        now = utc_now_iso()
        return {
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "weights_cents": {name: 0.0 for name in FEATURE_NAMES},
            "observations": 0,
            "settled_markets": {},
            "pending_markets": {},
            "net_pnl_dollars": 0.0,
            "loss_cluster": 0,
            "downgraded": False,
            "downgrade_reason": "",
            "last_decay_monotonic": time.monotonic(),
            "last_report_monotonic": 0.0,
        }

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self._default_state()
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            self.state_unreadable = True
            state = self._default_state()
            state["downgraded"] = True
            state["downgrade_reason"] = "memory_state_unreadable"
            return state
        if not isinstance(raw, dict):
            self.state_unreadable = True
            state = self._default_state()
            state["downgraded"] = True
            state["downgrade_reason"] = "memory_state_corrupt"
            return state
        weights = raw.get("weights_cents")
        if not isinstance(weights, dict):
            weights = {}
        raw["weights_cents"] = {name: coerce_float(weights.get(name), 0.0) for name in FEATURE_NAMES}
        raw.setdefault("settled_markets", {})
        raw.setdefault("pending_markets", {})
        raw.setdefault("observations", 0)
        raw.setdefault("net_pnl_dollars", 0.0)
        raw.setdefault("loss_cluster", 0)
        raw.setdefault("downgraded", False)
        raw.setdefault("downgrade_reason", "")
        raw.setdefault("last_decay_monotonic", time.monotonic())
        raw.setdefault("last_report_monotonic", 0.0)
        return raw

    def save(self) -> None:
        if self.state_unreadable:
            return
        with self._save_lock:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state["updated_at"] = utc_now_iso()
            payload = json.dumps(self.state, indent=2, sort_keys=True)
            last_error: Exception | None = None
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
                except OSError as exc:
                    last_error = exc
                    if tmp_path:
                        try:
                            Path(tmp_path).unlink(missing_ok=True)
                        except OSError:
                            pass
                    time.sleep(0.05 * (attempt + 1))
            self.state["downgraded"] = True
            self.state["downgrade_reason"] = "memory_state_write_failed"
            try:
                self._append_event(
                    {
                        "ts_wall": utc_now_iso(),
                        "event_type": "state_save_error",
                        "state_path": str(self.state_path),
                        "error": repr(last_error),
                        "downgraded": True,
                        "downgrade_reason": "memory_state_write_failed",
                    }
                )
            except OSError:
                pass

    def log_event(self, event_type: str, **payload: Any) -> None:
        row = {
            "ts_wall": utc_now_iso(),
            "event_type": event_type,
            **payload,
        }
        self._append_event(row)

    def _append_event(self, row: dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")

    def maybe_emit_report(self) -> None:
        interval = max(60.0, float(self.config.report_interval_seconds))
        now_mono = time.monotonic()
        last = coerce_float(self.state.get("last_report_monotonic"), 0.0)
        if last > 0 and now_mono - last < interval:
            return
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=interval)
        summary = {
            "entry_decisions": 0,
            "entry_raw_approved": 0,
            "entry_adjusted_approved": 0,
            "entry_explores": 0,
            "entry_skips": 0,
            "exit_decisions": 0,
            "exit_raw_signals": 0,
            "exit_adjusted_signals": 0,
            "exit_adjusted_holds": 0,
            "settlement_updates": 0,
            "reward_delta_cents": 0.0,
        }
        if self.log_path.exists():
            with self.log_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        row = json.loads(line)
                        ts = datetime.fromisoformat(str(row.get("ts_wall")).replace("Z", "+00:00"))
                    except Exception:
                        continue
                    if ts < cutoff:
                        continue
                    event_type = str(row.get("event_type") or "")
                    if event_type == "entry_decision":
                        summary["entry_decisions"] += 1
                        if coerce_bool(row.get("raw_approved")):
                            summary["entry_raw_approved"] += 1
                        if coerce_bool(row.get("adjusted_approved")):
                            summary["entry_adjusted_approved"] += 1
                        if row.get("action") == "explore":
                            summary["entry_explores"] += 1
                        if row.get("action") == "skip":
                            summary["entry_skips"] += 1
                    elif event_type == "exit_decision":
                        summary["exit_decisions"] += 1
                        if row.get("raw_reason"):
                            summary["exit_raw_signals"] += 1
                        if row.get("adjusted_reason"):
                            summary["exit_adjusted_signals"] += 1
                        elif row.get("raw_reason"):
                            summary["exit_adjusted_holds"] += 1
                    elif event_type == "settlement_reward":
                        summary["settlement_updates"] += 1
                        summary["reward_delta_cents"] += coerce_float(row.get("reward_delta_cents"), 0.0)
        summary["reward_delta_cents"] = round(float(summary["reward_delta_cents"]), 4)
        self._append_event(
            {
                "ts_wall": utc_now_iso(),
                "event_type": "report_15m",
                "window_seconds": interval,
                "effective_mode": self.effective_mode(),
                "state": self.memory_status_fields(),
                "summary": summary,
            }
        )
        self.state["last_report_monotonic"] = now_mono
        self.save()

    def effective_mode(self) -> str:
        if not self.config.enabled:
            return "disabled"
        if self.config.kill_switch:
            return "shadow"
        if self.state_unreadable:
            return "shadow"
        if coerce_bool(self.state.get("downgraded")):
            return "shadow"
        return "enforce" if self.config.enforce else "shadow"

    def memory_status_fields(self) -> dict[str, Any]:
        return {
            "mushroom_v28_phi_memory_enabled": bool(self.config.enabled),
            "mushroom_v28_phi_memory_mode": self.config.mode,
            "mushroom_v28_phi_memory_effective_mode": self.effective_mode(),
            "mushroom_v28_phi_memory_state_unreadable": bool(self.state_unreadable),
            "mushroom_v28_phi_memory_downgraded": coerce_bool(self.state.get("downgraded")),
            "mushroom_v28_phi_memory_downgrade_reason": str(self.state.get("downgrade_reason") or ""),
            "mushroom_v28_phi_memory_observations": int(self.state.get("observations") or 0),
            "mushroom_v28_phi_memory_loss_cluster": int(self.state.get("loss_cluster") or 0),
            "mushroom_v28_phi_memory_net_pnl_dollars": round(coerce_float(self.state.get("net_pnl_dollars"), 0.0), 4),
            "mushroom_v28_phi_memory_entry_correction_cap_cents": float(self.config.max_entry_correction_cents),
            "mushroom_v28_phi_memory_exit_correction_cap_cents": float(self.config.max_exit_correction_cents),
        }

    def apply_time_decay(self) -> None:
        if self.state_unreadable:
            return
        now = time.monotonic()
        last = coerce_float(self.state.get("last_decay_monotonic"), now)
        elapsed = max(0.0, now - last)
        if elapsed <= 0.0:
            return
        period = max(1.0, float(self.config.decay_period_seconds))
        factor = PHI ** (-(elapsed / period))
        if factor >= 0.9999:
            return
        weights = self.state.get("weights_cents", {})
        for name in FEATURE_NAMES:
            weights[name] = clamp(coerce_float(weights.get(name), 0.0) * factor, -self.config.max_weight_cents, self.config.max_weight_cents)
        self.state["weights_cents"] = weights
        self.state["last_decay_monotonic"] = now
        self.save()

    def build_features(self, *, kind: str, fields: dict[str, Any], trends: dict[str, float]) -> dict[str, float]:
        side = str(fields.get("mushroom_v28_side") or fields.get("side") or "").lower()
        side_sign = 1.0 if side == "yes" else -1.0
        phi_trend = coerce_float(trends.get("phi"), weighted_phi_trend(trends))
        edge = coerce_float(fields.get("mushroom_v28_edge_cents"), 0.0)
        min_edge = max(0.01, coerce_float(fields.get("mushroom_v28_min_edge_cents"), 3.0))
        abs_d = coerce_float(fields.get("mushroom_v28_abs_d_sigma"), 0.0)
        recross = coerce_float(fields.get("mushroom_v28_feature_gate_recross_hazard_score"), 0.0)
        volshock = coerce_float(fields.get("mushroom_v28_volshock"), 0.0)
        ask = coerce_float(fields.get("mushroom_v28_ask_cents") or fields.get("mushroom_v28_exit_bid_cents"), 0.0)
        book_age = coerce_float(fields.get("mushroom_v28_book_age_ms"), 0.0)
        max_book_age = max(1.0, coerce_float(fields.get("mushroom_v28_max_book_age_ms"), 750.0))
        seconds_to_close = coerce_float(fields.get("mushroom_v28_seconds_to_close"), 0.0)
        if kind == "exit":
            edge = coerce_float(fields.get("mushroom_v28_exit_net_cents"), 0.0) - coerce_float(
                fields.get("mushroom_v28_hold_net_cents"),
                0.0,
            )
        return {
            "bias": 1.0,
            "phi_trend_side": clamp(side_sign * phi_trend, -1.0, 1.0),
            "phi_trend_abs": clamp(abs(phi_trend), 0.0, 1.0),
            "trend_5m_side": clamp(side_sign * coerce_float(trends.get("5m"), 0.0), -1.0, 1.0),
            "trend_15m_side": clamp(side_sign * coerce_float(trends.get("15m"), 0.0), -1.0, 1.0),
            "trend_1h_side": clamp(side_sign * coerce_float(trends.get("1h"), 0.0), -1.0, 1.0),
            "edge_margin": clamp((edge - min_edge) / 10.0, -1.0, 1.0),
            "edge_near_floor": clamp((min_edge - edge) / max(1.0, min_edge), 0.0, 1.0),
            "abs_d_center": clamp(1.0 - abs(abs_d - 0.95) / 0.35, -1.0, 1.0),
            "abs_d_high": clamp((abs_d - 1.0) / 0.5, 0.0, 1.0),
            "recross_hazard": clamp(recross / 1.5, 0.0, 1.0),
            "volshock": clamp(volshock / 3.0, -1.0, 1.0),
            "book_age_ratio": clamp(book_age / max_book_age, 0.0, 1.5),
            "ask_level": clamp((ask - 75.0) / 25.0, -1.0, 1.0),
            "seconds_to_close": clamp(math.log1p(max(0.0, seconds_to_close) / 60.0) / math.log1p(15.0), 0.0, 1.0),
        }

    def raw_correction_cents(self, *, features: dict[str, float]) -> float:
        self.apply_time_decay()
        weights = self.state.get("weights_cents", {})
        return sum(coerce_float(weights.get(name), 0.0) * coerce_float(features.get(name), 0.0) for name in FEATURE_NAMES)

    def correction_cents(self, *, kind: str, features: dict[str, float]) -> float:
        raw = self.raw_correction_cents(features=features)
        cap = self.config.max_exit_correction_cents if kind == "exit" else self.config.max_entry_correction_cents
        return clamp(raw, -float(cap), float(cap))

    def entry_near_pass(self, fields: dict[str, Any], adjusted_edge: float) -> tuple[bool, list[str], dict[str, Any]]:
        hard_checks = {
            "book": fields.get("mushroom_v28_book_ok"),
            "btc": fields.get("mushroom_v28_btc_ok"),
            "time": fields.get("mushroom_v28_time_ok"),
            "ask": fields.get("mushroom_v28_ask_ok"),
            "risk": fields.get("mushroom_v28_risk_ok"),
            "balance": fields.get("mushroom_v28_balance_ok"),
        }
        hard_ok = all(coerce_bool(value) for value in hard_checks.values()) and not str(fields.get("mushroom_v28_block_reason") or "")
        if not hard_ok:
            return False, [f"hard_{name}" for name, value in hard_checks.items() if not coerce_bool(value)], {"hard_ok": False}

        min_edge = coerce_float(fields.get("mushroom_v28_min_edge_cents"), 3.0)
        edge_pass = adjusted_edge >= min_edge
        edge_near = self.config.near_edge_min_cents <= adjusted_edge < min_edge
        depth_count = max(0.0, coerce_float(fields.get("mushroom_v28_depth_count"), 0.0))
        target_count = max(1.0, coerce_float(fields.get("mushroom_v28_target_count"), 1.0))
        depth_ratio = coerce_float(fields.get("mushroom_v28_depth_ratio"), float("nan"))
        if not math.isfinite(depth_ratio):
            depth_ratio = depth_count / target_count
        if fields.get("mushroom_v28_depth_ratio_ok") is None:
            depth_pass = depth_ratio >= self.config.required_depth_ratio
        else:
            depth_pass = coerce_bool(fields.get("mushroom_v28_depth_ratio_ok"))
        depth_near = self.config.near_depth_ratio_min <= depth_ratio < self.config.required_depth_ratio
        abs_d = abs(coerce_float(fields.get("mushroom_v28_abs_d_sigma"), 0.0))
        exact_abs_min = coerce_float(fields.get("mushroom_v28_feature_gate_abs_d_min"), 0.80)
        exact_abs_max = coerce_float(fields.get("mushroom_v28_feature_gate_abs_d_max"), 1.10)
        if exact_abs_max <= 0.0:
            exact_abs_max = self.config.near_abs_d_max
        abs_pass = exact_abs_min <= abs_d <= exact_abs_max
        abs_near = self.config.near_abs_d_min <= abs_d <= self.config.near_abs_d_max

        misses: list[str] = []
        if not edge_pass:
            if edge_near:
                misses.append("edge_near")
            else:
                misses.append("edge_far")
        if not depth_pass:
            if depth_near:
                misses.append("depth_near")
            else:
                misses.append("depth_far")
        if not abs_pass:
            if abs_near:
                misses.append("abs_d_near")
            else:
                misses.append("abs_d_far")
        far_misses = [miss for miss in misses if miss.endswith("_far")]
        near_misses = [miss for miss in misses if miss.endswith("_near")]
        near_pass = not far_misses and len(near_misses) <= 1
        details = {
            "hard_ok": True,
            "depth_ratio": round(depth_ratio, 6),
            "edge_pass": edge_pass,
            "edge_near": edge_near,
            "depth_pass": depth_pass,
            "depth_near": depth_near,
            "abs_d_pass": abs_pass,
            "abs_d_near": abs_near,
            "miss_count": len(misses),
        }
        return near_pass, misses, details

    def apply_entry(self, *, market: str, fields: dict[str, Any], trends: dict[str, float]) -> dict[str, Any]:
        status = self.memory_status_fields()
        fields.update(status)
        if not self.config.enabled or fields.get("mushroom_v28_status") != "ok":
            return fields

        raw_approved = coerce_bool(fields.get("mushroom_v28_approved"))
        raw_edge = coerce_float(fields.get("mushroom_v28_edge_cents"), 0.0)
        fair_side = coerce_float(fields.get("mushroom_v28_fair_side_cents"), 0.0)
        ask = coerce_float(fields.get("mushroom_v28_ask_cents"), 0.0)
        fee = coerce_float(fields.get("mushroom_v28_fee_cents"), 0.0)
        slippage = coerce_float(fields.get("mushroom_v28_slippage_cents"), 0.0)
        buffer = coerce_float(fields.get("mushroom_v28_model_buffer_cents"), 0.0)
        min_edge = coerce_float(fields.get("mushroom_v28_min_edge_cents"), 3.0)
        raw_target_count = max(0, int(coerce_float(fields.get("mushroom_v28_target_count"), 0.0)))
        features = self.build_features(kind="entry", fields=fields, trends=trends)
        correction = self.correction_cents(kind="entry", features=features)
        adjusted_fair = fair_side + correction
        adjusted_edge = raw_edge + correction
        adjusted_model_max = int(math.floor(adjusted_fair - fee - slippage - buffer - min_edge))
        adjusted_model_max = max(1, min(99, adjusted_model_max))
        adjusted_edge_ok = adjusted_edge >= min_edge
        adjusted_price_ok = ask <= adjusted_model_max
        near_pass, near_misses, near_details = self.entry_near_pass(fields, adjusted_edge)
        effective_mode = self.effective_mode()

        adjusted_approved = raw_approved
        action = "keep" if raw_approved else "none"
        if raw_approved and (not adjusted_edge_ok or not adjusted_price_ok):
            adjusted_approved = False
            action = "skip"
        elif (not raw_approved) and near_pass and self.config.allow_add_entries:
            adjusted_approved = True
            action = "explore"

        enforced = effective_mode == "enforce"
        final_approved = adjusted_approved if enforced else raw_approved
        final_edge = adjusted_edge if enforced else raw_edge
        final_model_max = adjusted_model_max if enforced else int(fields.get("mushroom_v28_model_max_buy_price_cents") or adjusted_model_max)
        if action == "explore" and enforced:
            final_model_max = max(final_model_max, int(round(ask)))

        fields.update(
            {
                "mushroom_v28_phi_memory_raw_approved": raw_approved,
                "mushroom_v28_phi_memory_adjusted_approved": adjusted_approved,
                "mushroom_v28_phi_memory_enforced": bool(enforced),
                "mushroom_v28_phi_memory_entry_action": action,
                "mushroom_v28_phi_memory_correction_cents": round(correction, 6),
                "mushroom_v28_phi_memory_adjusted_edge_cents": round(adjusted_edge, 6),
                "mushroom_v28_phi_memory_adjusted_fair_side_cents": round(adjusted_fair, 6),
                "mushroom_v28_phi_memory_adjusted_model_max_buy_price_cents": adjusted_model_max,
                "mushroom_v28_phi_memory_near_pass": bool(near_pass),
                "mushroom_v28_phi_memory_near_pass_misses": near_misses,
                "mushroom_v28_phi_memory_depth_ratio": near_details.get("depth_ratio"),
                "mushroom_v28_phi_memory_near_edge_min_cents": float(self.config.near_edge_min_cents),
                "mushroom_v28_phi_memory_near_depth_ratio_min": float(self.config.near_depth_ratio_min),
                "mushroom_v28_phi_memory_required_depth_ratio": float(self.config.required_depth_ratio),
                "mushroom_v28_phi_memory_near_abs_d_min": float(self.config.near_abs_d_min),
                "mushroom_v28_phi_memory_near_abs_d_max": float(self.config.near_abs_d_max),
                "mushroom_v28_phi_memory_trends": {key: round(coerce_float(value), 6) for key, value in trends.items()},
                "mushroom_v28_phi_memory_features": {key: round(value, 6) for key, value in features.items()},
            }
        )
        if enforced:
            fields["mushroom_v28_approved"] = bool(final_approved)
            fields["mushroom_v28_edge_cents"] = round(final_edge, 6)
            fields["mushroom_v28_net_edge_cents"] = round(final_edge, 6)
            fields["mushroom_v28_model_max_buy_price_cents"] = int(final_model_max)
            fields["mushroom_v28_edge_ok"] = bool(final_edge >= min_edge or (action == "explore" and near_pass))
            fields["mushroom_v28_model_price_ok"] = bool(ask <= final_model_max or (action == "explore" and near_pass))

        decision = {
            "kind": "entry",
            "side": str(fields.get("mushroom_v28_side") or ""),
            "features": features,
            "raw_would_trade": raw_approved,
            "memory_would_trade": adjusted_approved,
            "enforced": enforced,
            "action": action,
            "ask_cents": ask,
            "fee_cents_per_contract": fee,
            "qty": max(1, raw_target_count),
            "raw_edge_cents": raw_edge,
            "adjusted_edge_cents": adjusted_edge,
        }
        self._record_pending_decision(market=market, decision=decision)
        self.log_event(
            "entry_decision",
            market=market,
            side=fields.get("mushroom_v28_side"),
            kind=decision["kind"],
            features={key: round(value, 6) for key, value in features.items()},
            raw_would_trade=decision["raw_would_trade"],
            memory_would_trade=decision["memory_would_trade"],
            raw_approved=raw_approved,
            adjusted_approved=adjusted_approved,
            enforced=enforced,
            action=action,
            ask_cents=round(ask, 6),
            fee_cents_per_contract=round(fee, 6),
            qty=decision["qty"],
            correction_cents=round(correction, 6),
            raw_edge_cents=round(raw_edge, 6),
            adjusted_edge_cents=round(adjusted_edge, 6),
            near_pass=near_pass,
            near_misses=near_misses,
            trends=fields.get("mushroom_v28_phi_memory_trends"),
        )
        self.maybe_emit_report()
        return fields

    def apply_exit(self, *, market: str, fields: dict[str, Any], trends: dict[str, float]) -> dict[str, Any]:
        fields.update(self.memory_status_fields())
        if not self.config.enabled:
            return fields
        raw_reason = str(fields.get("mushroom_v28_exit_reason") or "")
        raw_target_count = max(0, int(coerce_float(fields.get("mushroom_v28_exit_target_count"), 0.0)))
        features = self.build_features(kind="exit", fields=fields, trends=trends)
        raw_exit_correction = self.raw_correction_cents(features=features)
        live_exit_cap = float(self.config.max_exit_correction_cents)
        correction = clamp(raw_exit_correction, -live_exit_cap, live_exit_cap)
        shadow_exit_cap = 2.0 if live_exit_cap <= 0.0 else live_exit_cap
        shadow_correction = clamp(raw_exit_correction, -shadow_exit_cap, shadow_exit_cap)
        fair_hold = coerce_float(fields.get("mushroom_v28_fair_hold_cents"), 0.0)
        p_hold = coerce_float(fields.get("mushroom_v28_p_hold"), 0.0)
        exit_net = coerce_float(fields.get("mushroom_v28_exit_net_cents"), 0.0)
        hold_buffer = coerce_float(fields.get("mushroom_v28_exit_hold_buffer_cents"), 1.0)
        hysteresis = coerce_float(fields.get("mushroom_v28_exit_hysteresis_cents"), 0.25)
        entry_basis = coerce_float(fields.get("mushroom_v28_entry_basis_cents"), 0.0)
        qty = max(1, int(coerce_float(fields.get("mushroom_v28_position_count"), raw_target_count or 1)))

        def project_exit(exit_correction: float) -> dict[str, Any]:
            projected_fair = fair_hold + exit_correction
            projected_p_hold = clamp(p_hold + (exit_correction / 100.0), 0.0, 1.0)
            projected_hold_net = projected_fair - hold_buffer
            projected_drawdown = max(0.0, entry_basis - projected_fair) if entry_basis > 0 else 0.0
            projected_reason = ""
            projected_target_count = 0
            if exit_net >= projected_hold_net + hysteresis:
                projected_reason = "mushroom_v28_exit_value_over_hold"
                projected_target_count = qty
            elif projected_p_hold <= coerce_float(fields.get("mushroom_v28_exit_full_p_hold_floor"), 0.72):
                projected_reason = "mushroom_v28_probability_collapse_full"
                projected_target_count = qty
            elif entry_basis > 0 and projected_drawdown >= coerce_float(fields.get("mushroom_v28_exit_full_drawdown_cents"), 15.0):
                projected_reason = "mushroom_v28_fair_drawdown_full"
                projected_target_count = qty
            elif projected_p_hold <= coerce_float(fields.get("mushroom_v28_exit_reduce_p_hold_floor"), 0.80):
                projected_reason = "mushroom_v28_probability_reduce"
                projected_target_count = max(1, int(math.ceil(qty * coerce_float(fields.get("mushroom_v28_exit_reduce_fraction"), 0.5))))
            elif entry_basis > 0 and projected_drawdown >= coerce_float(fields.get("mushroom_v28_exit_fair_drawdown_cents"), 8.0):
                projected_reason = "mushroom_v28_fair_drawdown_reduce"
                projected_target_count = max(1, int(math.ceil(qty * coerce_float(fields.get("mushroom_v28_exit_reduce_fraction"), 0.5))))
            projected_target_count = min(qty, projected_target_count)
            return {
                "fair": projected_fair,
                "p_hold": projected_p_hold,
                "hold_net": projected_hold_net,
                "drawdown": projected_drawdown,
                "reason": projected_reason,
                "target_count": projected_target_count,
            }

        live_projection = project_exit(correction)
        shadow_projection = project_exit(shadow_correction)
        adjusted_fair = live_projection["fair"]
        adjusted_p_hold = live_projection["p_hold"]
        adjusted_hold_net = live_projection["hold_net"]
        adjusted_drawdown = live_projection["drawdown"]
        reason = live_projection["reason"]
        target_count = live_projection["target_count"]
        adjusted_exits = bool(reason and target_count > 0)
        shadow_exits = bool(shadow_projection["reason"] and shadow_projection["target_count"] > 0)
        effective_mode = self.effective_mode()
        enforced = effective_mode == "enforce"
        fields.update(
            {
                "mushroom_v28_phi_memory_raw_exit_reason": raw_reason,
                "mushroom_v28_phi_memory_adjusted_exit_reason": reason,
                "mushroom_v28_phi_memory_adjusted_exit_target_count": target_count,
                "mushroom_v28_phi_memory_exit_action": "exit" if adjusted_exits else "hold",
                "mushroom_v28_phi_memory_enforced": bool(enforced),
                "mushroom_v28_phi_memory_correction_cents": round(correction, 6),
                "mushroom_v28_phi_memory_adjusted_fair_hold_cents": round(adjusted_fair, 6),
                "mushroom_v28_phi_memory_adjusted_p_hold": round(adjusted_p_hold, 6),
                "mushroom_v28_phi_memory_adjusted_hold_net_cents": round(adjusted_hold_net, 6),
                "mushroom_v28_phi_memory_adjusted_fair_drawdown_cents": round(adjusted_drawdown, 6),
                "mushroom_v28_phi_memory_shadow_exit_reason": shadow_projection["reason"],
                "mushroom_v28_phi_memory_shadow_exit_target_count": shadow_projection["target_count"],
                "mushroom_v28_phi_memory_shadow_exit_action": "exit" if shadow_exits else "hold",
                "mushroom_v28_phi_memory_shadow_exit_correction_cents": round(shadow_correction, 6),
                "mushroom_v28_phi_memory_trends": {key: round(coerce_float(value), 6) for key, value in trends.items()},
                "mushroom_v28_phi_memory_features": {key: round(value, 6) for key, value in features.items()},
            }
        )
        if enforced:
            fields["mushroom_v28_exit_reason"] = reason
            fields["mushroom_v28_exit_target_count"] = target_count
            fields["mushroom_v28_p_hold"] = round(adjusted_p_hold, 6)
            fields["mushroom_v28_fair_hold_cents"] = round(adjusted_fair, 6)
            fields["mushroom_v28_hold_net_cents"] = round(adjusted_hold_net, 6)
            fields["mushroom_v28_fair_drawdown_cents"] = round(adjusted_drawdown, 6)
        exit_fee = coerce_float(fields.get("mushroom_v28_exit_fee_cents"), 0.0)
        exit_bid = coerce_float(fields.get("mushroom_v28_exit_bid_cents"), 0.0)
        decision = {
            "kind": "exit",
            "side": str(fields.get("mushroom_v28_side") or ""),
            "features": features,
            "raw_would_trade": bool(raw_reason and raw_target_count > 0),
            "memory_would_trade": adjusted_exits,
            "enforced": enforced,
            "action": fields.get("mushroom_v28_phi_memory_exit_action"),
            "bid_cents": exit_bid,
            "entry_basis_cents": entry_basis,
            "fee_cents_per_contract": exit_fee,
            "qty": max(1, raw_target_count or target_count or qty),
            "raw_reason": raw_reason,
            "adjusted_reason": reason,
        }
        self._record_pending_decision(market=market, decision=decision)
        self.log_event(
            "exit_decision",
            market=market,
            side=fields.get("mushroom_v28_side"),
            kind=decision["kind"],
            features={key: round(value, 6) for key, value in features.items()},
            raw_would_trade=decision["raw_would_trade"],
            memory_would_trade=decision["memory_would_trade"],
            raw_reason=raw_reason,
            adjusted_reason=reason,
            shadow_memory_would_trade=shadow_exits,
            shadow_adjusted_reason=shadow_projection["reason"],
            shadow_adjusted_target_count=shadow_projection["target_count"],
            shadow_correction_cents=round(shadow_correction, 6),
            enforced=enforced,
            action=decision["action"],
            bid_cents=round(exit_bid, 6),
            entry_basis_cents=round(entry_basis, 6),
            fee_cents_per_contract=round(exit_fee, 6),
            qty=decision["qty"],
            correction_cents=round(correction, 6),
            raw_target_count=raw_target_count,
            adjusted_target_count=target_count,
            trends=fields.get("mushroom_v28_phi_memory_trends"),
        )
        self.maybe_emit_report()
        return fields

    def _record_pending_decision(self, *, market: str, decision: dict[str, Any]) -> None:
        if not market or self.state_unreadable:
            return
        if not self._decision_has_trade(decision):
            return
        pending = self.state.setdefault("pending_markets", {})
        bucket = pending.setdefault(market, {"decisions": [], "first_seen": utc_now_iso(), "last_seen": utc_now_iso()})
        bucket["last_seen"] = utc_now_iso()
        decisions = bucket.setdefault("decisions", [])
        if decisions and self._decision_key(decisions[-1]) == self._decision_key(decision):
            return
        decisions.append(decision)
        bucket["decisions"] = decisions[-128:]
        if len(pending) > 512:
            for key in sorted(pending.keys())[:-512]:
                pending.pop(key, None)
        self.save()

    def _decision_has_trade(self, decision: dict[str, Any]) -> bool:
        return coerce_bool(decision.get("raw_would_trade")) or coerce_bool(decision.get("memory_would_trade"))

    def _decision_final_would_trade(self, decision: dict[str, Any]) -> bool:
        return (
            coerce_bool(decision.get("memory_would_trade"))
            if coerce_bool(decision.get("enforced"))
            else coerce_bool(decision.get("raw_would_trade"))
        )

    def _decision_key(self, decision: dict[str, Any]) -> tuple[Any, ...]:
        return (
            str(decision.get("kind") or ""),
            str(decision.get("side") or ""),
            str(decision.get("action") or ""),
            coerce_bool(decision.get("raw_would_trade")),
            coerce_bool(decision.get("memory_would_trade")),
            round(coerce_float(decision.get("ask_cents"), 0.0), 4),
            round(coerce_float(decision.get("bid_cents"), 0.0), 4),
            round(coerce_float(decision.get("entry_basis_cents"), 0.0), 4),
            int(coerce_float(decision.get("qty"), 0.0)),
            str(decision.get("raw_reason") or ""),
            str(decision.get("adjusted_reason") or ""),
        )

    def _unfilled_label_key(self, decision: dict[str, Any]) -> tuple[Any, ...]:
        return (
            str(decision.get("kind") or ""),
            str(decision.get("side") or ""),
            str(decision.get("action") or ""),
            coerce_bool(decision.get("raw_would_trade")),
            coerce_bool(decision.get("memory_would_trade")),
            str(decision.get("raw_reason") or ""),
            str(decision.get("adjusted_reason") or ""),
        )

    def _decision_from_log_row(self, row: dict[str, Any]) -> dict[str, Any] | None:
        kind = str(row.get("kind") or "").strip().lower()
        if kind not in {"entry", "exit"}:
            event_type = str(row.get("event_type") or "")
            if event_type == "entry_decision":
                kind = "entry"
            elif event_type == "exit_decision":
                kind = "exit"
            else:
                return None
        raw_trade = coerce_bool(row.get("raw_would_trade"))
        memory_trade = coerce_bool(row.get("memory_would_trade"))
        if "raw_would_trade" not in row and kind == "entry":
            raw_trade = coerce_bool(row.get("raw_approved"))
        if "memory_would_trade" not in row and kind == "entry":
            memory_trade = coerce_bool(row.get("adjusted_approved"))
        if "raw_would_trade" not in row and kind == "exit":
            raw_trade = bool(row.get("raw_reason"))
        if "memory_would_trade" not in row and kind == "exit":
            memory_trade = bool(row.get("adjusted_reason"))
        decision: dict[str, Any] = {
            "kind": kind,
            "side": str(row.get("side") or ""),
            "features": row.get("features") if isinstance(row.get("features"), dict) else {},
            "raw_would_trade": raw_trade,
            "memory_would_trade": memory_trade,
            "enforced": coerce_bool(row.get("enforced")),
            "action": row.get("action") or ("keep" if kind == "entry" and raw_trade else ""),
            "fee_cents_per_contract": coerce_float(row.get("fee_cents_per_contract"), 0.0),
            "qty": max(1, int(coerce_float(row.get("qty"), 1.0))),
        }
        if kind == "entry":
            decision.update(
                {
                    "ask_cents": coerce_float(row.get("ask_cents"), 0.0),
                    "raw_edge_cents": coerce_float(row.get("raw_edge_cents"), 0.0),
                    "adjusted_edge_cents": coerce_float(row.get("adjusted_edge_cents"), 0.0),
                }
            )
            if coerce_float(decision.get("ask_cents"), 0.0) <= 0:
                return None
        else:
            decision.update(
                {
                    "bid_cents": coerce_float(row.get("bid_cents"), 0.0),
                    "entry_basis_cents": coerce_float(row.get("entry_basis_cents"), 0.0),
                    "raw_reason": str(row.get("raw_reason") or ""),
                    "adjusted_reason": str(row.get("adjusted_reason") or ""),
                }
            )
            if coerce_float(decision.get("entry_basis_cents"), 0.0) <= 0:
                return None
        return decision if self._decision_has_trade(decision) else None

    def _recover_pending_decisions_from_log(self, market: str) -> list[dict[str, Any]]:
        if not market or not self.log_path.exists():
            return []
        recovered: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        try:
            with self.log_path.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if str(row.get("market") or "") != market:
                        continue
                    if str(row.get("event_type") or "") not in {"entry_decision", "exit_decision"}:
                        continue
                    decision = self._decision_from_log_row(row)
                    if decision is None:
                        continue
                    key = self._decision_key(decision)
                    if key in seen:
                        continue
                    seen.add(key)
                    recovered.append(decision)
        except OSError as exc:
            self.log_event("decision_recovery_error", market=market, error=str(exc))
            return []
        return recovered[-128:]

    def has_pending_market(self, market: str) -> bool:
        pending = self.state.get("pending_markets", {})
        return isinstance(pending, dict) and market in pending

    def _entry_pnl_cents(self, *, decision: dict[str, Any], settlement_result: str) -> float:
        side = str(decision.get("side") or "").lower()
        qty = max(1, int(coerce_float(decision.get("qty"), 1.0)))
        ask = coerce_float(decision.get("ask_cents"), 0.0)
        fee = coerce_float(decision.get("fee_cents_per_contract"), 0.0)
        if side not in {"yes", "no"} or ask <= 0:
            return 0.0
        payout = 100.0 if settlement_result == side else 0.0
        return (payout - ask - fee) * qty

    def _exit_pnl_cents(self, *, decision: dict[str, Any], settlement_result: str) -> tuple[float, float]:
        side = str(decision.get("side") or "").lower()
        qty = max(1, int(coerce_float(decision.get("qty"), 1.0)))
        bid = coerce_float(decision.get("bid_cents"), 0.0)
        basis = coerce_float(decision.get("entry_basis_cents"), 0.0)
        fee = coerce_float(decision.get("fee_cents_per_contract"), 0.0)
        if side not in {"yes", "no"} or basis <= 0:
            return 0.0, 0.0
        exit_pnl = (bid - basis - fee) * qty if bid > 0 else 0.0
        hold_payout = 100.0 if settlement_result == side else 0.0
        hold_pnl = (hold_payout - basis) * qty
        return exit_pnl, hold_pnl

    def _coerce_outcome_record(self, outcome_record: Any) -> dict[str, Any]:
        if outcome_record is None:
            return {}
        if isinstance(outcome_record, dict):
            return outcome_record
        to_dict = getattr(outcome_record, "to_dict", None)
        if callable(to_dict):
            try:
                parsed = to_dict()
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}
        try:
            parsed = dict(vars(outcome_record))
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def _execution_attribution_context(
        self,
        *,
        outcome_record: Any,
        settlement_result: str,
        actual_pnl_dollars: float | None,
    ) -> dict[str, Any]:
        record = self._coerce_outcome_record(outcome_record)
        side_cashflows = record.get("side_cashflows") if isinstance(record.get("side_cashflows"), dict) else {}

        def side_context(side_key: str, bucket: dict[str, Any]) -> dict[str, Any]:
            side_norm = str(side_key or "").strip().lower()
            entry_qty_side = max(0, int(coerce_float(bucket.get("entry_qty"), 0.0)))
            exit_qty_side = max(0, int(coerce_float(bucket.get("exit_qty"), 0.0)))
            entry_notional = coerce_float(bucket.get("entry_notional_cents"), 0.0)
            exit_notional = coerce_float(bucket.get("exit_notional_cents"), 0.0)
            entry_basis_side = entry_notional / float(entry_qty_side) if entry_qty_side > 0 else 0.0
            exit_fill_side = exit_notional / float(exit_qty_side) if exit_qty_side > 0 else 0.0
            entry_fee_side = coerce_float(bucket.get("entry_fee_cents"), 0.0)
            exit_fee_side = coerce_float(bucket.get("exit_fee_cents"), 0.0)
            entry_fee_per_contract_side = (entry_fee_side / float(entry_qty_side)) if entry_qty_side > 0 else 0.0
            exit_fee_per_contract_side = (exit_fee_side / float(exit_qty_side)) if exit_qty_side > 0 else 0.0
            entry_pnl_per_contract_side = 0.0
            if entry_qty_side > 0 and entry_basis_side > 0 and side_norm in {"yes", "no"}:
                payout = 100.0 if settlement_result == side_norm else 0.0
                entry_pnl_per_contract_side = payout - entry_basis_side - entry_fee_per_contract_side
            exit_pnl_per_contract_side = 0.0
            hold_pnl_per_contract_side = 0.0
            if exit_qty_side > 0 and entry_basis_side > 0 and side_norm in {"yes", "no"}:
                exit_pnl_per_contract_side = exit_fill_side - entry_basis_side - exit_fee_per_contract_side
                hold_payout = 100.0 if settlement_result == side_norm else 0.0
                hold_pnl_per_contract_side = hold_payout - entry_basis_side
            return {
                "record_available": bool(record),
                "traded": coerce_bool(record.get("traded")),
                "outcome_type": str(record.get("outcome_type") or ""),
                "side": side_norm,
                "entry_qty": entry_qty_side,
                "entry_remaining_qty": entry_qty_side,
                "entry_fill_cents": entry_basis_side,
                "entry_fee_cents": entry_fee_side,
                "entry_pnl_per_contract_cents": entry_pnl_per_contract_side,
                "exit_qty": exit_qty_side,
                "exit_remaining_qty": exit_qty_side,
                "exit_fill_cents": exit_fill_side,
                "exit_fee_cents": exit_fee_side,
                "exit_pnl_per_contract_cents": exit_pnl_per_contract_side,
                "exit_hold_pnl_per_contract_cents": hold_pnl_per_contract_side,
                "ioc_zero_fill_count": max(0, int(coerce_float(record.get("ioc_zero_fill_count"), 0.0))),
            }

        by_side: dict[str, dict[str, Any]] = {}
        if isinstance(side_cashflows, dict):
            for side_key, bucket in side_cashflows.items():
                side_norm = str(side_key or "").strip().lower()
                if side_norm not in {"yes", "no"} or not isinstance(bucket, dict):
                    continue
                by_side[side_norm] = side_context(side_norm, bucket)

        side = str(record.get("side") or "").strip().lower()
        entry_qty = max(0, int(coerce_float(record.get("entry_qty"), 0.0)))
        exit_qty = max(0, int(coerce_float(record.get("exit_qty"), 0.0)))
        actual_pnl = (
            coerce_float(actual_pnl_dollars, 0.0)
            if actual_pnl_dollars is not None
            else coerce_float(record.get("pnl_dollars"), 0.0)
        )
        entry_basis = coerce_float(record.get("entry_fill_cents"), 0.0)
        entry_fee = coerce_float(record.get("entry_fee_cents"), 0.0)
        entry_fee_per_contract = (entry_fee / float(entry_qty)) if entry_qty > 0 else 0.0
        entry_pnl_per_contract = 0.0
        if entry_qty > 0 and entry_basis > 0 and side in {"yes", "no"}:
            entry_payout = 100.0 if settlement_result == side else 0.0
            entry_pnl_per_contract = entry_payout - entry_basis - entry_fee_per_contract
        exit_fill = coerce_float(record.get("exit_fill_cents"), 0.0)
        exit_fee = coerce_float(record.get("exit_fee_cents"), 0.0)
        exit_fee_per_contract = (exit_fee / float(exit_qty)) if exit_qty > 0 else 0.0
        exit_pnl_per_contract = 0.0
        hold_pnl_per_contract = 0.0
        if exit_qty > 0 and entry_basis > 0 and side in {"yes", "no"}:
            exit_pnl_per_contract = exit_fill - entry_basis - exit_fee_per_contract
            hold_payout = 100.0 if settlement_result == side else 0.0
            hold_pnl_per_contract = hold_payout - entry_basis
        return {
            "record_available": bool(record),
            "traded": coerce_bool(record.get("traded")),
            "outcome_type": str(record.get("outcome_type") or ""),
            "side": side,
            "entry_qty": entry_qty,
            "entry_remaining_qty": entry_qty,
            "entry_fill_cents": entry_basis,
            "entry_fee_cents": entry_fee,
            "entry_pnl_per_contract_cents": entry_pnl_per_contract,
            "exit_qty": exit_qty,
            "exit_remaining_qty": exit_qty,
            "exit_fill_cents": exit_fill,
            "exit_fee_cents": exit_fee,
            "exit_pnl_per_contract_cents": exit_pnl_per_contract,
            "exit_hold_pnl_per_contract_cents": hold_pnl_per_contract,
            "ioc_zero_fill_count": max(0, int(coerce_float(record.get("ioc_zero_fill_count"), 0.0))),
            "actual_pnl_dollars": actual_pnl,
            "by_side": by_side,
        }

    def _entry_settlement_label_cents(self, *, decision: dict[str, Any], settlement_result: str) -> float:
        side = str(decision.get("side") or "").strip().lower()
        if side not in {"yes", "no"} or settlement_result not in {"yes", "no"}:
            return 0.0
        qty = max(1, int(coerce_float(decision.get("qty"), 1.0)))
        label = float(self.config.unfilled_signal_label_cents) * float(qty)
        return label if settlement_result == side else -label

    def _exit_settlement_label_cents(self, *, decision: dict[str, Any], settlement_result: str) -> float:
        side = str(decision.get("side") or "").strip().lower()
        if side not in {"yes", "no"} or settlement_result not in {"yes", "no"}:
            return 0.0
        qty = max(1, int(coerce_float(decision.get("qty"), 1.0)))
        label = float(self.config.unfilled_signal_label_cents) * float(qty)
        return -label if settlement_result == side else label

    def _attribute_entry_decision_reward(
        self,
        *,
        decision: dict[str, Any],
        settlement_result: str,
        execution: dict[str, Any],
        unfilled_label_seen: set[tuple[Any, ...]],
    ) -> dict[str, Any] | None:
        raw_trade = coerce_bool(decision.get("raw_would_trade"))
        memory_trade = coerce_bool(decision.get("memory_would_trade"))
        if not raw_trade and not memory_trade:
            return None
        final_trade = self._decision_final_would_trade(decision)
        decision_qty = max(1, int(coerce_float(decision.get("qty"), 1.0)))
        decision_side = str(decision.get("side") or "").strip().lower()
        side_execution = execution
        by_side = execution.get("by_side")
        if isinstance(by_side, dict) and decision_side in by_side:
            side_execution = by_side[decision_side]
        record_side = str(side_execution.get("side") or "").strip().lower()
        can_attach_fill = (
            final_trade
            and int(side_execution.get("entry_remaining_qty") or 0) > 0
            and coerce_float(side_execution.get("entry_fill_cents"), 0.0) > 0
            and (not record_side or record_side == decision_side)
        )
        if can_attach_fill:
            attributed_qty = min(decision_qty, int(side_execution.get("entry_remaining_qty") or 0))
            side_execution["entry_remaining_qty"] = max(0, int(side_execution.get("entry_remaining_qty") or 0) - attributed_qty)
            actual_pnl = float(side_execution.get("entry_pnl_per_contract_cents") or 0.0) * float(attributed_qty)
            raw_pnl = actual_pnl if raw_trade else 0.0
            memory_pnl = actual_pnl if memory_trade else 0.0
            return {
                "mode": "actual_entry_fill",
                "raw_pnl_cents": raw_pnl,
                "memory_pnl_cents": memory_pnl,
                "delta_cents": memory_pnl - raw_pnl,
                "attributed_qty": attributed_qty,
                "actual_fill": True,
                "label": False,
            }

        label_key = ("entry", *self._unfilled_label_key(decision))
        if label_key in unfilled_label_seen:
            return None
        unfilled_label_seen.add(label_key)
        label_pnl = self._entry_settlement_label_cents(decision=decision, settlement_result=settlement_result)
        raw_pnl = label_pnl if raw_trade else 0.0
        memory_pnl = label_pnl if memory_trade else 0.0
        return {
            "mode": "settlement_label_unfilled_entry",
            "raw_pnl_cents": raw_pnl,
            "memory_pnl_cents": memory_pnl,
            "delta_cents": memory_pnl - raw_pnl,
            "attributed_qty": 0,
            "actual_fill": False,
            "label": True,
        }

    def _attribute_exit_decision_reward(
        self,
        *,
        decision: dict[str, Any],
        settlement_result: str,
        execution: dict[str, Any],
        unfilled_label_seen: set[tuple[Any, ...]],
    ) -> dict[str, Any] | None:
        raw_trade = coerce_bool(decision.get("raw_would_trade"))
        memory_trade = coerce_bool(decision.get("memory_would_trade"))
        if not raw_trade and not memory_trade:
            return None
        final_trade = self._decision_final_would_trade(decision)
        decision_qty = max(1, int(coerce_float(decision.get("qty"), 1.0)))
        decision_side = str(decision.get("side") or "").strip().lower()
        side_execution = execution
        by_side = execution.get("by_side")
        if isinstance(by_side, dict) and decision_side in by_side:
            side_execution = by_side[decision_side]
        record_side = str(side_execution.get("side") or "").strip().lower()
        can_attach_fill = (
            final_trade
            and int(side_execution.get("exit_remaining_qty") or 0) > 0
            and coerce_float(side_execution.get("exit_fill_cents"), 0.0) > 0
            and coerce_float(side_execution.get("entry_fill_cents"), 0.0) > 0
            and (not record_side or record_side == decision_side)
        )
        if can_attach_fill:
            attributed_qty = min(decision_qty, int(side_execution.get("exit_remaining_qty") or 0))
            side_execution["exit_remaining_qty"] = max(0, int(side_execution.get("exit_remaining_qty") or 0) - attributed_qty)
            exit_pnl = float(side_execution.get("exit_pnl_per_contract_cents") or 0.0) * float(attributed_qty)
            hold_pnl = float(side_execution.get("exit_hold_pnl_per_contract_cents") or 0.0) * float(attributed_qty)
            raw_pnl = exit_pnl if raw_trade else hold_pnl
            memory_pnl = exit_pnl if memory_trade else hold_pnl
            return {
                "mode": "actual_exit_fill_vs_hold",
                "raw_pnl_cents": raw_pnl,
                "memory_pnl_cents": memory_pnl,
                "delta_cents": memory_pnl - raw_pnl,
                "attributed_qty": attributed_qty,
                "actual_fill": True,
                "label": False,
            }

        label_key = ("exit", *self._unfilled_label_key(decision))
        if label_key in unfilled_label_seen:
            return None
        unfilled_label_seen.add(label_key)
        label_pnl = self._exit_settlement_label_cents(decision=decision, settlement_result=settlement_result)
        raw_pnl = label_pnl if raw_trade else 0.0
        memory_pnl = label_pnl if memory_trade else 0.0
        return {
            "mode": "settlement_label_unfilled_exit",
            "raw_pnl_cents": raw_pnl,
            "memory_pnl_cents": memory_pnl,
            "delta_cents": memory_pnl - raw_pnl,
            "attributed_qty": 0,
            "actual_fill": False,
            "label": True,
        }

    def learn_from_settlement(
        self,
        *,
        market: str,
        result: str,
        actual_pnl_dollars: float | None = None,
        outcome_record: Any = None,
    ) -> dict[str, Any]:
        normalized = str(result or "").strip().lower()
        if normalized not in {"yes", "no", "void"}:
            return {"updated": False, "reason": "unresolved_result"}
        if self.state_unreadable:
            return {"updated": False, "reason": "state_unreadable"}
        settled = self.state.setdefault("settled_markets", {})
        if market in settled:
            return {"updated": False, "reason": "already_settled"}
        pending = self.state.setdefault("pending_markets", {})
        bucket = pending.pop(market, None)
        decisions = list((bucket or {}).get("decisions") or [])
        recovered_decisions = 0
        if not any(self._decision_has_trade(decision) for decision in decisions):
            recovered = self._recover_pending_decisions_from_log(market)
            if recovered:
                decisions = recovered
                recovered_decisions = len(recovered)
        total_delta_cents = 0.0
        used_decisions = 0
        actual_fill_decisions = 0
        unfilled_label_decisions = 0
        entry_fill_attributed_qty = 0
        exit_fill_attributed_qty = 0
        attribution_mode_counts: dict[str, int] = {}
        reward_by_kind_cents: dict[str, float] = {}
        reward_by_action_cents: dict[str, float] = {}
        unfilled_label_seen: set[tuple[Any, ...]] = set()
        execution = self._execution_attribution_context(
            outcome_record=outcome_record,
            settlement_result=normalized,
            actual_pnl_dollars=actual_pnl_dollars,
        )
        if normalized != "void":
            for decision in decisions:
                kind = str(decision.get("kind") or "")
                if kind == "entry":
                    attribution = self._attribute_entry_decision_reward(
                        decision=decision,
                        settlement_result=normalized,
                        execution=execution,
                        unfilled_label_seen=unfilled_label_seen,
                    )
                elif kind == "exit":
                    attribution = self._attribute_exit_decision_reward(
                        decision=decision,
                        settlement_result=normalized,
                        execution=execution,
                        unfilled_label_seen=unfilled_label_seen,
                    )
                else:
                    continue
                if not attribution:
                    continue
                delta_cents = coerce_float(attribution.get("delta_cents"), 0.0)
                total_delta_cents += delta_cents
                used_decisions += 1
                mode = str(attribution.get("mode") or "unknown")
                attribution_mode_counts[mode] = attribution_mode_counts.get(mode, 0) + 1
                reward_by_kind_cents[kind] = reward_by_kind_cents.get(kind, 0.0) + delta_cents
                action_key = str(decision.get("action") or kind or "unknown")
                reward_by_action_cents[action_key] = reward_by_action_cents.get(action_key, 0.0) + delta_cents
                if coerce_bool(attribution.get("actual_fill")):
                    actual_fill_decisions += 1
                    if kind == "entry":
                        entry_fill_attributed_qty += int(coerce_float(attribution.get("attributed_qty"), 0.0))
                    elif kind == "exit":
                        exit_fill_attributed_qty += int(coerce_float(attribution.get("attributed_qty"), 0.0))
                if coerce_bool(attribution.get("label")):
                    unfilled_label_decisions += 1
                if abs(delta_cents) > 1e-9:
                    self._update_weights(decision.get("features") or {}, delta_cents)
        actual_pnl = coerce_float(execution.get("actual_pnl_dollars"), 0.0)
        self.state["net_pnl_dollars"] = round(coerce_float(self.state.get("net_pnl_dollars"), 0.0) + actual_pnl, 4)
        if actual_pnl < 0:
            self.state["loss_cluster"] = int(self.state.get("loss_cluster") or 0) + 1
        elif actual_pnl > 0:
            self.state["loss_cluster"] = 0
        self._maybe_downgrade()
        settled[market] = {
            "result": normalized,
            "resolved_at": utc_now_iso(),
            "decision_count": len(decisions),
            "used_decision_count": used_decisions,
            "recovered_decision_count": recovered_decisions,
            "actual_fill_decision_count": actual_fill_decisions,
            "unfilled_label_decision_count": unfilled_label_decisions,
            "entry_fill_attributed_qty": entry_fill_attributed_qty,
            "exit_fill_attributed_qty": exit_fill_attributed_qty,
            "attribution_mode_counts": dict(sorted(attribution_mode_counts.items())),
            "reward_by_kind_cents": {
                key: round(value, 4) for key, value in sorted(reward_by_kind_cents.items())
            },
            "reward_by_action_cents": {
                key: round(value, 4) for key, value in sorted(reward_by_action_cents.items())
            },
            "outcome_entry_qty": int(execution.get("entry_qty") or 0),
            "outcome_exit_qty": int(execution.get("exit_qty") or 0),
            "outcome_ioc_zero_fill_count": int(execution.get("ioc_zero_fill_count") or 0),
            "reward_delta_cents": round(total_delta_cents, 4),
            "actual_pnl_dollars": round(actual_pnl, 4),
        }
        if len(settled) > 1024:
            for key in sorted(settled.keys())[:-1024]:
                settled.pop(key, None)
        self.save()
        self.log_event(
            "settlement_reward",
            market=market,
            result=normalized,
            decision_count=len(decisions),
            used_decision_count=used_decisions,
            recovered_decision_count=recovered_decisions,
            actual_fill_decision_count=actual_fill_decisions,
            unfilled_label_decision_count=unfilled_label_decisions,
            entry_fill_attributed_qty=entry_fill_attributed_qty,
            exit_fill_attributed_qty=exit_fill_attributed_qty,
            attribution_mode_counts=dict(sorted(attribution_mode_counts.items())),
            reward_by_kind_cents={
                key: round(value, 4) for key, value in sorted(reward_by_kind_cents.items())
            },
            reward_by_action_cents={
                key: round(value, 4) for key, value in sorted(reward_by_action_cents.items())
            },
            outcome_entry_qty=int(execution.get("entry_qty") or 0),
            outcome_exit_qty=int(execution.get("exit_qty") or 0),
            outcome_ioc_zero_fill_count=int(execution.get("ioc_zero_fill_count") or 0),
            reward_delta_cents=round(total_delta_cents, 4),
            actual_pnl_dollars=round(actual_pnl, 4),
            downgraded=coerce_bool(self.state.get("downgraded")),
            downgrade_reason=str(self.state.get("downgrade_reason") or ""),
        )
        self.maybe_emit_report()
        return {
            "updated": True,
            "decision_count": len(decisions),
            "used_decision_count": used_decisions,
            "recovered_decision_count": recovered_decisions,
            "actual_fill_decision_count": actual_fill_decisions,
            "unfilled_label_decision_count": unfilled_label_decisions,
            "entry_fill_attributed_qty": entry_fill_attributed_qty,
            "exit_fill_attributed_qty": exit_fill_attributed_qty,
            "attribution_mode_counts": dict(sorted(attribution_mode_counts.items())),
            "reward_by_kind_cents": {
                key: round(value, 4) for key, value in sorted(reward_by_kind_cents.items())
            },
            "reward_by_action_cents": {
                key: round(value, 4) for key, value in sorted(reward_by_action_cents.items())
            },
            "reward_delta_cents": round(total_delta_cents, 4),
            "actual_pnl_dollars": round(actual_pnl, 4),
        }

    def _update_weights(self, features: dict[str, Any], reward_delta_cents: float) -> None:
        clipped_reward = clamp(reward_delta_cents, -self.config.reward_clip_cents, self.config.reward_clip_cents)
        weights = self.state.setdefault("weights_cents", {name: 0.0 for name in FEATURE_NAMES})
        for name in FEATURE_NAMES:
            value = coerce_float(features.get(name), 0.0)
            current = coerce_float(weights.get(name), 0.0)
            shrink = current * float(self.config.regularization)
            update = float(self.config.learn_rate) * clipped_reward * value
            weights[name] = round(clamp(current + update - shrink, -self.config.max_weight_cents, self.config.max_weight_cents), 8)
        self.state["observations"] = int(self.state.get("observations") or 0) + 1

    def _maybe_downgrade(self) -> None:
        if self.config.kill_switch:
            self.state["downgraded"] = True
            self.state["downgrade_reason"] = "manual_kill_switch"
            return
        if coerce_float(self.state.get("net_pnl_dollars"), 0.0) <= float(self.config.kill_net_pnl_dollars):
            self.state["downgraded"] = True
            self.state["downgrade_reason"] = "net_pnl_kill"
            return
        if int(self.state.get("loss_cluster") or 0) >= int(self.config.kill_loss_cluster):
            self.state["downgraded"] = True
            self.state["downgrade_reason"] = "loss_cluster_kill"
