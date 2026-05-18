"""Denominator audit for frozen v28 exit-policy watches.

Research-only; no live bot changes or orders.

Several promising exit/state watches are frozen but have zero strict rows. This
probe separates "too new to have any base exit rows" from "base exit rows exist
but the watch-specific join/filter is not collecting rows".
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_exit_policy_common_clock_watch as cc


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_watch_denominator_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_watch_denominator_audit_latest.md"

WATCH_SPECIFIC_OVERLAP_LANES = {
    "soft_frontier_midprice_delayed_recheck_exit",
    "soft_frontier_midprice_delayed_recheck_rescue",
    "feature_gate_value_exit",
    "feature_gate_exit_bid_suppression",
    "feature_gate_exit_bid_delayed_recheck",
    "value_exit_feature_side_guard",
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


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def age_minutes(freeze_ts: Any, now: datetime) -> float | None:
    dt = parse_ts(freeze_ts)
    if dt is None:
        return None
    return max(0.0, (now - dt).total_seconds() / 60.0)


def base_exit_rows_after(freeze_ts: Any, base_rows: list[dict[str, Any]]) -> int:
    return len(cc.filter_snapshot(base_rows, str(freeze_ts) if freeze_ts else None))


def latest_base_ts(base_rows: list[dict[str, Any]]) -> str | None:
    values = [cc.row_ts(row) for row in base_rows]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return max(values).isoformat()


def status_read(row: dict[str, Any], base_after: int) -> str:
    lane = str(row.get("lane") or "")
    settled = int(fnum(row.get("settled")))
    suppressed = int(fnum(row.get("suppressed_exits")))
    status = str(row.get("status") or "")
    if settled == 0 and base_after == 0:
        return "too_new_no_base_exit_rows"
    if settled == 0 and base_after > 0 and lane in WATCH_SPECIFIC_OVERLAP_LANES:
        return "watch_specific_overlap_not_collecting"
    if settled == 0 and base_after > 0:
        return "watch_join_or_filter_not_collecting"
    if settled > 0 and suppressed == 0:
        return "denominator_collecting_rule_not_firing"
    if status == "positive_but_under_sample":
        return "collecting_positive_but_immature"
    if status.startswith("blocked"):
        return "collecting_blocked"
    return "collecting_watch_only"


def build_report() -> dict[str, Any]:
    dashboard = load_json(DASHBOARD_JSON)
    base_rows = cc.build_scored_rows()
    now = datetime.now(timezone.utc)
    rows = []
    for item in dashboard.get("rows") or []:
        if not isinstance(item, dict):
            continue
        freeze_ts = item.get("freeze_ts_utc")
        base_after = base_exit_rows_after(freeze_ts, base_rows)
        row = {
            "lane": item.get("lane"),
            "status": item.get("status"),
            "freeze_ts_utc": freeze_ts,
            "age_minutes": age_minutes(freeze_ts, now),
            "watch_settled": int(fnum(item.get("settled"))),
            "watch_suppressed": int(fnum(item.get("suppressed_exits"))),
            "base_exit_rows_after_freeze": base_after,
            "candidate_net_cents": fnum(item.get("candidate_net_cents")),
            "delta_vs_current_cents": fnum(item.get("delta_vs_current_cents")),
            "blockers": item.get("blockers") or [],
            "opportunity": item.get("opportunity") or {},
        }
        row["denominator_read"] = status_read(
            row | {
                "settled": item.get("settled"),
                "suppressed_exits": item.get("suppressed_exits"),
                "status": item.get("status"),
            },
            base_after,
        )
        rows.append(row)
    read_counts: dict[str, int] = {}
    for row in rows:
        read = str(row.get("denominator_read"))
        read_counts[read] = read_counts.get(read, 0) + 1
    report = {
        "generated_at_utc": utc_now_iso(),
        "dashboard_source": str(DASHBOARD_JSON),
        "base_exit_rows_total": len(base_rows),
        "latest_base_exit_ts_utc": latest_base_ts(base_rows),
        "denominator_read_counts": dict(sorted(read_counts.items())),
        "rows": rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    rows = report.get("rows") or []
    zero_base = [row for row in rows if row.get("denominator_read") == "too_new_no_base_exit_rows"]
    join_missing = [row for row in rows if row.get("denominator_read") == "watch_join_or_filter_not_collecting"]
    overlap_missing = [row for row in rows if row.get("denominator_read") == "watch_specific_overlap_not_collecting"]
    no_fire = [row for row in rows if row.get("denominator_read") == "denominator_collecting_rule_not_firing"]
    notes = [
        "Research-only denominator audit; it does not score or change a rule.",
        f"Base scored exit rows currently total {report.get('base_exit_rows_total')}.",
        f"Latest generic base exit timestamp is {report.get('latest_base_exit_ts_utc')}.",
        f"Too-new zero-row watches: {[row.get('lane') for row in zero_base]}.",
        f"Watch-specific overlap waits: {[row.get('lane') for row in overlap_missing]}.",
        f"Potential join/filter denominator issues: {[row.get('lane') for row in join_missing]}.",
        f"Collecting but no rule-fire watches: {[row.get('lane') for row in no_fire]}.",
    ]
    if not join_missing and not overlap_missing:
        notes.append("No zero-row watch currently has base exit rows after its freeze, so zero strict rows look time/recency driven rather than an obvious wiring break.")
    elif not join_missing:
        notes.append("No zero-row watch currently looks like an obvious wiring break; remaining zero-row watches are watch-specific overlap waits.")
    return notes


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if value is None:
        return "n/a"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Watch Denominator Audit",
        "",
        "Research-only denominator audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Base scored exit rows total: `{report.get('base_exit_rows_total')}`",
        f"- Latest base exit UTC: `{report.get('latest_base_exit_ts_utc')}`",
        f"- Denominator read counts: `{report.get('denominator_read_counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| lane | status | read | age min | watch rows | suppressed | base rows after freeze | net c | delta c | blockers |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('status')}` | `{row.get('denominator_read')}` | "
            f"{fmt(row.get('age_minutes'))} | {row.get('watch_settled')} | {row.get('watch_suppressed')} | "
            f"{row.get('base_exit_rows_after_freeze')} | {fmt(row.get('candidate_net_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
