"""Replay recent v28 logs with the lifecycle exit overlay.

This is an offline probe. It does not place orders or mutate live bot state.
It replays filled-entry telemetry into a temporary lifecycle controller, then
applies the lifecycle overlay to observed v28 exit signals and compares changed
exit decisions against known settlement results when available.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from v28_trade_lifecycle import TradeLifecycleConfig, TradeLifecycleController


ROOT = Path(__file__).resolve().parent
SOURCE_TAG = os.getenv(
    "V28_LIFECYCLE_REPLAY_LOG_SOURCE_TAG",
    "live_mushroom_v28_common_clock_phi_reward_memory_size2_live",
)
OUTPUT_TAG = os.getenv(
    "V28_LIFECYCLE_REPLAY_OUTPUT_TAG",
    f"{SOURCE_TAG}_lifecycle_overlay_replay",
)
LOG_DIR = ROOT / "logs" / SOURCE_TAG
STATE_DIR = ROOT / "state" / SOURCE_TAG
OUT_DIR = ROOT / "stats" / OUTPUT_TAG


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def side(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"yes", "no"}:
        return text
    return ""


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


def load_outcomes(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if isinstance(record, dict) and record.get("market"):
            out[str(record["market"])] = record
    return out


def settlement_value_cents(outcome: dict[str, Any], contract_side: str, qty: float) -> float | None:
    result = side(outcome.get("settlement_result"))
    if not result:
        return None
    return (100.0 if result == contract_side else 0.0) * qty


def build_controller() -> TradeLifecycleController:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (OUT_DIR / "v28_trade_lifecycle_replay_state.json", OUT_DIR / "v28_trade_lifecycle_replay.ndjson"):
        if path.exists():
            path.unlink()
    return TradeLifecycleController(
        TradeLifecycleConfig(
            enabled=True,
            mode="exit_only_enforce",
            state_path=OUT_DIR / "v28_trade_lifecycle_replay_state.json",
            log_path=OUT_DIR / "v28_trade_lifecycle_replay.ndjson",
            exit_toll_cents=number(os.getenv("MUSHROOM_V28_LIFECYCLE_EXIT_TOLL_CENTS"), 2.5),
            recheck_seconds=number(os.getenv("MUSHROOM_V28_LIFECYCLE_RECHECK_SECONDS"), 5.0),
            cheap_entry_max_cents=number(os.getenv("MUSHROOM_V28_LIFECYCLE_CHEAP_ENTRY_MAX_CENTS"), 15.0),
            promote_delta_cents=number(os.getenv("MUSHROOM_V28_LIFECYCLE_PROMOTE_DELTA_CENTS"), 100.0),
            disable_bad_settles=int(number(os.getenv("MUSHROOM_V28_LIFECYCLE_DISABLE_BAD_SETTLES"), 3)),
        )
    )


def main() -> None:
    events = load_events(LOG_DIR / "execution_events.ndjson")
    outcomes = load_outcomes(STATE_DIR / "recent_market_outcomes.json")
    controller = build_controller()
    seen_entry_markets: set[str] = set()
    changed_exits: list[dict[str, Any]] = []
    raw_exits = 0
    lifecycle_allows = 0

    for event in events:
        event_type = str(event.get("event_type") or "")
        market = str(event.get("market") or "")
        event_side = side(event.get("side") or event.get("mushroom_v28_side"))
        if not market or not event_side:
            continue
        if event_type == "fill_full" and market not in seen_entry_markets:
            entry_price = number(
                event.get("actual_fill_price_cents")
                or event.get("trigger_price_cents")
                or event.get("mushroom_v28_ask_cents")
            )
            if entry_price <= 0:
                continue
            controller.classify_entry_fill(
                market_ticker=market,
                side=event_side,
                count=number(event.get("fill_count") or event.get("cumulative_fill_count"), 1.0),
                entry_price_cents=entry_price,
                entry_fee_cents=number(event.get("actual_fee_cents") or event.get("mushroom_v28_fee_cents")),
                fields=event,
            )
            seen_entry_markets.add(market)
            continue
        if event_type != "exit_signal_seen":
            continue
        raw_reason = str(event.get("mushroom_v28_exit_reason") or "")
        if not raw_reason:
            continue
        raw_exits += 1
        updated, defer = controller.apply_exit(
            market_ticker=market,
            side=event_side,
            fields=dict(event),
            position_bucket=controller.active_bucket(market),
            now_monotonic=number(event.get("ts_mono")),
        )
        action = str(updated.get("mushroom_v28_lifecycle_action") or "")
        if updated.get("mushroom_v28_exit_reason"):
            lifecycle_allows += 1
        if action.startswith("suppress") or action.startswith("delay") or defer:
            qty = number(event.get("mushroom_v28_exit_target_count") or event.get("position_size"), 1.0)
            raw_exit_value = number(event.get("mushroom_v28_exit_net_cents")) * qty
            settle_value = settlement_value_cents(outcomes.get(market, {}), event_side, qty)
            changed_exits.append(
                {
                    "market": market,
                    "side": event_side,
                    "bucket": updated.get("mushroom_v28_lifecycle_bucket"),
                    "action": action,
                    "raw_reason": raw_reason,
                    "qty": qty,
                    "raw_exit_value_cents": round(raw_exit_value, 4),
                    "settlement_value_cents": None if settle_value is None else round(settle_value, 4),
                    "known_settlement_delta_cents": None
                    if settle_value is None
                    else round(settle_value - raw_exit_value, 4),
                }
            )

    known_deltas = [
        row["known_settlement_delta_cents"]
        for row in changed_exits
        if row["known_settlement_delta_cents"] is not None
    ]
    unique_changed: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in changed_exits:
        key = (
            row.get("market"),
            row.get("side"),
            row.get("action"),
            row.get("raw_reason"),
            row.get("qty"),
            row.get("raw_exit_value_cents"),
        )
        unique_changed.setdefault(key, row)
    unique_known_deltas = [
        row["known_settlement_delta_cents"]
        for row in unique_changed.values()
        if row["known_settlement_delta_cents"] is not None
    ]
    summary = {
        "source_tag": SOURCE_TAG,
        "events_scanned": len(events),
        "entry_markets_classified": len(seen_entry_markets),
        "raw_exit_signals": raw_exits,
        "lifecycle_allowed_exit_signals": lifecycle_allows,
        "lifecycle_changed_exit_signals": len(changed_exits),
        "lifecycle_unique_changed_exit_signals": len(unique_changed),
        "known_changed_exit_deltas_cents": {
            "count": len(known_deltas),
            "sum": round(sum(known_deltas), 4),
            "avg": round(sum(known_deltas) / len(known_deltas), 4) if known_deltas else 0.0,
        },
        "known_unique_changed_exit_deltas_cents": {
            "count": len(unique_known_deltas),
            "sum": round(sum(unique_known_deltas), 4),
            "avg": round(sum(unique_known_deltas) / len(unique_known_deltas), 4) if unique_known_deltas else 0.0,
        },
        "changed_exits": changed_exits,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
