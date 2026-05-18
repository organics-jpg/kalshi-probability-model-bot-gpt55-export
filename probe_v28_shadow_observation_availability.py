"""Shadow observation availability for frozen v28 research candidates.

Research-only. This probe does not touch live bot logic or place orders.

Several candidate scorecards can show zero strict-forward rows even while the
shadow loop is alive. This report separates denominator availability from
strategy quality by counting post-freeze shadow events, reconstructed trades,
exit-clock trades, and settled rows for each active frozen clock.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_common_clock_watch import parse_ts, row_ts
from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_shadow_observation_availability_latest.json"
OUT_MD = OUT_DIR / "v28_shadow_observation_availability_latest.md"

FREEZE_FILES = {
    "boundary_clock_feature_gate": OUT_DIR / "v28_boundary_clock_feature_gate_candidate_state.json",
    "dual_exit_book_gap_else_reduce": OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_state.json",
    "exit_book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_state.json",
    "exit_book_gap_loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_state.json",
    "exit_book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_state.json",
    "exit_reduce_drift_guard": OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_state.json",
    "exit_shallow_drawdown": OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_state.json",
    "exit_shallow_duration_lte52": OUT_DIR / "v28_frozen_exit_shallow_duration_watch_state.json",
    "exit_clip_separator_watch": OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json",
    "matched_unchanged_loss_guard_watch": OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json",
    "feature_gate_exit_bid_suppression": OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_state.json",
    "feature_gate_exit_bid_delayed_recheck": OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_state.json",
    "feature_gate_value_exit": OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_state.json",
    "value_exit_feature_side_guard": OUT_DIR / "v28_frozen_value_exit_feature_side_guard_state.json",
    "soft_frontier_midprice_delayed_recheck_exit": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_state.json",
    "soft_frontier_midprice_delayed_recheck_rescue": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_state.json",
    "feature_gate_size_shrink_delayed_recheck_exit": OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_exit_state.json",
    "feature_gate_size_shrink_delayed_recheck_rescue": OUT_DIR / "v28_feature_gate_size_shrink_delayed_recheck_rescue_state.json",
    "feature_gate_late_collapse_recheck_rescue": OUT_DIR / "v28_feature_gate_late_collapse_recheck_rescue_state.json",
    "feature_gate_dual_clock_recheck_rescue": OUT_DIR / "v28_feature_gate_dual_clock_recheck_rescue_state.json",
    "feature_gate_confirmed_dual_clock_fill": OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_state.json",
    "top_component_mix_portfolio": OUT_DIR / "v28_top_component_mix_portfolio_state.json",
    "top_component_false_negative_rescue_child": OUT_DIR / "v28_top_component_false_negative_rescue_child_state.json",
    "top_component_parent_fill_repair_child": OUT_DIR / "v28_top_component_parent_fill_repair_child_state.json",
    "exit_common_clock_residual_child": OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_state.json",
    "exit_common_clock_residual_child_book_gap_guard": OUT_DIR / "v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_state.json",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def freeze_ts_for(name: str, path: Path) -> str | None:
    payload = load_json(path)
    ts = payload.get("freeze_ts_utc") or payload.get("freeze_utc") or payload.get("created_utc")
    if not ts and isinstance(payload.get("state"), dict):
        ts = payload["state"].get("freeze_ts_utc")
    return str(ts) if ts else None


def event_ts(event: dict[str, Any]) -> datetime | None:
    return parse_ts(event.get("ts_wall") or event.get("timestamp") or event.get("ts"))


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("hold_gross_cents") is not None and row.get("actual_gross_cents") is not None


def summarize_window(name: str, freeze_ts: str | None, events: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    freeze_dt = parse_ts(freeze_ts)
    if freeze_dt is None:
        return {
            "clock": name,
            "freeze_ts_utc": freeze_ts,
            "blocker": "freeze_ts_missing_or_invalid",
        }

    post_events = [event for event in events if (ts := event_ts(event)) is not None and ts >= freeze_dt]
    post_entry_rows = [
        row
        for row in rows
        if (ts := parse_ts(row.get("entry_ts"))) is not None and ts >= freeze_dt
    ]
    post_exit_rows = [row for row in rows if (ts := row_ts(row)) is not None and ts >= freeze_dt]
    settled_entry_rows = [row for row in post_entry_rows if is_settled(row)]
    settled_exit_rows = [row for row in post_exit_rows if is_settled(row)]
    pending_exit_rows = [row for row in post_exit_rows if not is_settled(row)]

    event_counts = Counter(str(event.get("event_type") or "<blank>") for event in post_events)
    status_counts = Counter(str(row.get("status") or "<blank>") for row in post_exit_rows)
    result_counts = Counter(str(row.get("result") or "<blank>") for row in post_exit_rows)

    recent_pending = []
    for row in pending_exit_rows[-8:]:
        features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
        recent_pending.append(
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "entry_ts": row.get("entry_ts"),
                "exit_ts": row.get("exit_ts"),
                "status": row.get("status"),
                "result": row.get("result"),
                "actual_gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "exit_reason": features.get("mushroom_v28_exit_reason") or row.get("exit_reason"),
            }
        )

    if settled_exit_rows:
        blocker = None
    elif pending_exit_rows:
        blocker = "post_freeze_exit_rows_unsettled"
    elif post_entry_rows:
        blocker = "post_freeze_entries_without_exit_clock_rows"
    elif post_events:
        blocker = "post_freeze_events_without_reconstructed_candidate_rows"
    else:
        blocker = "no_post_freeze_shadow_events"

    return {
        "clock": name,
        "freeze_ts_utc": freeze_ts,
        "post_event_count": len(post_events),
        "post_event_counts": dict(sorted(event_counts.items())),
        "post_entry_trades": len(post_entry_rows),
        "post_exit_clock_trades": len(post_exit_rows),
        "settled_post_entry_trades": len(settled_entry_rows),
        "settled_post_exit_clock_trades": len(settled_exit_rows),
        "pending_post_exit_clock_trades": len(pending_exit_rows),
        "status_counts": dict(sorted(status_counts.items())),
        "result_counts": dict(sorted(result_counts.items())),
        "recent_pending_exit_rows": recent_pending,
        "blocker": blocker,
    }


def build_report() -> dict[str, Any]:
    events = read_events()
    trades = reconstruct_trades(events)
    rows = [score_trade(trade) for trade in trades]
    clocks = {
        name: freeze_ts_for(name, path)
        for name, path in FREEZE_FILES.items()
    }
    summaries = [summarize_window(name, ts, events, rows) for name, ts in clocks.items()]
    return {
        "generated_utc": utc_now_iso(),
        "shadow_events": len(events),
        "shadow_trades": len(rows),
        "clocks": summaries,
    }


def cents(value: Any) -> str:
    if value is None:
        return ""
    try:
        c = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{c:.0f}c (${c / 100.0:.2f})"


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# v28 Shadow Observation Availability",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Generated UTC: `{payload['generated_utc']}`",
        f"- Shadow events: `{payload['shadow_events']}`",
        f"- Reconstructed shadow trades: `{payload['shadow_trades']}`",
        "",
        "## Frozen Clocks",
        "",
        "| clock | freeze UTC | post events | post entries | post exit-clock rows | settled exit-clock rows | pending exit-clock rows | blocker |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["clocks"]:
        lines.append(
            "| {clock} | `{freeze}` | {events} | {entries} | {exit_rows} | {settled} | {pending} | {blocker} |".format(
                clock=row.get("clock"),
                freeze=row.get("freeze_ts_utc"),
                events=row.get("post_event_count", 0),
                entries=row.get("post_entry_trades", 0),
                exit_rows=row.get("post_exit_clock_trades", 0),
                settled=row.get("settled_post_exit_clock_trades", 0),
                pending=row.get("pending_post_exit_clock_trades", 0),
                blocker=row.get("blocker") or "",
            )
        )
    lines.extend(["", "## Pending Exit-Clock Rows", ""])
    for row in payload["clocks"]:
        pending = row.get("recent_pending_exit_rows") or []
        if not pending:
            continue
        lines.extend(
            [
                f"### {row.get('clock')}",
                "",
                "| market | side | entry UTC | exit UTC | status | result | actual | hold | exit reason |",
                "|---|---|---|---|---|---|---:|---:|---|",
            ]
        )
        for item in pending:
            lines.append(
                "| {market} | {side} | `{entry}` | `{exit}` | {status} | {result} | {actual} | {hold} | {reason} |".format(
                    market=item.get("market"),
                    side=item.get("side"),
                    entry=item.get("entry_ts"),
                    exit=item.get("exit_ts"),
                    status=item.get("status"),
                    result=item.get("result"),
                    actual=cents(item.get("actual_gross_cents")),
                    hold=cents(item.get("hold_gross_cents")),
                    reason=item.get("exit_reason"),
                )
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- Settled exit-clock rows are the denominator used by strict forward exit-policy scorecards.",
            "- Pending rows show that the shadow loop is collecting observations but market settlement is not yet available.",
            "- A missing or zero denominator is not promotion evidence; it is only a collection/readiness state.",
        ]
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_report()
    write_report(payload)
    print(OUT_MD)


if __name__ == "__main__":
    main()
