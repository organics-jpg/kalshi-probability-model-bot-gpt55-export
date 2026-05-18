"""Path-contradiction diagnostic for the frozen v28 +5pp FV challenger.

The raw-p50 calibrated FV candidate can select an early broad side before the
stricter v28 live/shadow strategy would approve anything. This report checks
whether later actual v28 approvals in the same market agree with or contradict
that early selected side.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_calibrated_fv_forward_monitor import OUT_JSON as MONITOR_JSON
from probe_v28_frozen_forward_candidates import parse_ts
from probe_v28_reactivated_shadow_status import read_events


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_calibrated_fv_path_contradiction_latest.json"
OUT_MD = OUT_DIR / "v28_calibrated_fv_path_contradiction_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def approval_events() -> list[dict[str, Any]]:
    approvals: list[dict[str, Any]] = []
    for event in read_events():
        if event.get("event_type") != "mushroom_v28_approved":
            continue
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        if not market or side not in {"yes", "no"}:
            continue
        approvals.append(event)
    return sorted(approvals, key=lambda row: str(row.get("ts_wall") or ""))


def selected_forward_rows(monitor: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in monitor.get("clean_details") or []:
        selected = item.get("selected_row") or {}
        if not selected:
            continue
        rows.append({**selected, "market": item.get("market")})
    return rows


def later_approvals(selected: dict[str, Any], approvals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    market = str(selected.get("market") or "")
    selected_ts = parse_ts(selected.get("ts_wall"))
    if selected_ts is None:
        return []
    rows = []
    for event in approvals:
        if str(event.get("market") or "") != market:
            continue
        event_ts = parse_ts(event.get("ts_wall"))
        if event_ts is None or event_ts < selected_ts:
            continue
        rows.append(event)
    return rows


def summarize_selected(selected: dict[str, Any], approvals: list[dict[str, Any]]) -> dict[str, Any]:
    selected_side = str(selected.get("side") or "").lower()
    selected_ts = parse_ts(selected.get("ts_wall"))
    later = later_approvals(selected, approvals)
    compact_later = []
    for event in later:
        event_ts = parse_ts(event.get("ts_wall"))
        delay = None
        if selected_ts is not None and event_ts is not None:
            delay = (event_ts - selected_ts).total_seconds()
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        compact_later.append({
            "ts_wall": event.get("ts_wall"),
            "delay_seconds": delay,
            "side": side,
            "same_side": side == selected_side,
            "p_side": as_float(event.get("mushroom_v28_p_side")),
            "ask_cents": as_float(event.get("mushroom_v28_ask_cents")),
            "edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
            "seconds_to_close": as_float(event.get("mushroom_v28_seconds_to_close")),
        })
    opposite = [row for row in compact_later if row["same_side"] is False]
    same = [row for row in compact_later if row["same_side"] is True]
    return {
        "market": selected.get("market"),
        "selected_ts": selected.get("ts_wall"),
        "selected_side": selected_side,
        "selected_p_raw": selected.get("p_raw"),
        "selected_p_plus05": selected.get("p_plus05"),
        "selected_ask_prob": selected.get("ask_prob"),
        "selected_raw_edge_prob": selected.get("raw_edge_prob"),
        "selected_side_won": selected.get("side_won"),
        "selected_net_cents": selected.get("net_gross_cents_after_entry_fee"),
        "later_approval_count": len(compact_later),
        "later_same_side_count": len(same),
        "later_opposite_side_count": len(opposite),
        "has_later_opposite_approval": bool(opposite),
        "first_later_approval": compact_later[0] if compact_later else None,
        "first_later_opposite_approval": opposite[0] if opposite else None,
        "later_approvals": compact_later,
    }


def build_report() -> dict[str, Any]:
    monitor = load_json(MONITOR_JSON)
    selected = selected_forward_rows(monitor)
    approvals = approval_events()
    rows = [summarize_selected(row, approvals) for row in selected]
    settled_rows = [row for row in rows if row.get("selected_side_won") is not None]
    contradiction_rows = [row for row in rows if row.get("has_later_opposite_approval")]
    settled_contradictions = [row for row in contradiction_rows if row.get("selected_side_won") is not None]
    return {
        "source_monitor": str(MONITOR_JSON),
        "freeze_ts": monitor.get("freeze_ts"),
        "selected_rows": len(rows),
        "settled_rows": len(settled_rows),
        "later_opposite_approval_rows": len(contradiction_rows),
        "settled_later_opposite_approval_rows": len(settled_contradictions),
        "settled_later_opposite_selected_wins": sum(1 for row in settled_contradictions if row.get("selected_side_won") is True),
        "settled_later_opposite_selected_losses": sum(1 for row in settled_contradictions if row.get("selected_side_won") is False),
        "blockers": ["settled_contradiction_sample_lt_5"] if len(settled_contradictions) < 5 else [],
        "rows": rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Calibrated FV Path Contradiction",
        "",
        "Checks whether later actual v28 approvals contradict the early raw-p50 calibrated FV selected side.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Selected rows: `{report.get('selected_rows')}`",
        f"- Settled rows: `{report.get('settled_rows')}`",
        f"- Rows with later opposite v28 approval: `{report.get('later_opposite_approval_rows')}`",
        f"- Settled contradiction W/L for early selected side: `{report.get('settled_later_opposite_selected_wins')}/{report.get('settled_later_opposite_selected_losses')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "| market | selected side | p raw | ask | won | net c | later approvals | later opposite | first opposite delay | first opposite side/p/ask |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in report.get("rows") or []:
        opp = row.get("first_later_opposite_approval") or {}
        lines.append(
            f"| {row.get('market')} | {row.get('selected_side')} | {fmt(row.get('selected_p_raw'))} | "
            f"{fmt(row.get('selected_ask_prob'))} | {row.get('selected_side_won')} | "
            f"{fmt(row.get('selected_net_cents'))} | {row.get('later_approval_count')} | "
            f"{row.get('later_opposite_side_count')} | {fmt(opp.get('delay_seconds'))} | "
            f"{opp.get('side')}/{fmt(opp.get('p_side'))}/{fmt(opp.get('ask_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
