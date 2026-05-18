"""Chronological drift audit for frozen v28 reduce-exit suppression.

Research-only; no live bot changes or orders.

The blanket p_hold>=0.75 probability-reduce suppressor is still positive, but
its promotion blocker is loss-control cost. This report shows how the
suppressed-exit delta evolved over time so new harmful rows do not get hidden
inside the aggregate positive PnL.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_suppression_drift_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_suppression_drift_audit_latest.md"


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def side_won(row: dict[str, Any]) -> bool | None:
    side = str(row.get("side") or "")
    result = str(row.get("result") or "")
    if result not in {"yes", "no"} or side not in {"yes", "no"}:
        return None
    return side == result


def suppress_class(row: dict[str, Any]) -> str:
    won = side_won(row)
    if won is True:
        return "helpful_winner_recovery"
    if won is False:
        return "harmful_loss_control_cost"
    return "unknown_outcome"


def row_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = [suppress_class(row)]
    p_hold = as_float(row.get("p_hold"))
    drawdown = as_float(row.get("fair_drawdown_cents"))
    worst = as_float(row.get("worst_post_exit_hold_mark_cents"))
    delta = as_float(row.get("delta_cents")) or 0.0
    if p_hold is not None:
        if p_hold >= 0.79:
            tags.append("p_hold_ge_079")
        else:
            tags.append("p_hold_075_079")
    if drawdown is not None:
        if drawdown < 0:
            tags.append("favorable_fair_value")
        elif drawdown <= 2.5:
            tags.append("small_fair_drawdown")
        elif drawdown <= 5.0:
            tags.append("moderate_fair_drawdown")
        else:
            tags.append("large_fair_drawdown")
    if worst is not None and worst < 0:
        tags.append("post_exit_mark_full_loss")
    if delta < 0:
        tags.append("negative_delta")
    elif delta > 0:
        tags.append("positive_delta")
    return tags


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": side_won(row),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "p_hold": row.get("p_hold"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "current_cents": row.get("current_cents"),
        "hold_cents": row.get("hold_cents"),
        "delta_cents": row.get("delta_cents"),
        "worst_post_exit_hold_mark_cents": row.get("worst_post_exit_hold_mark_cents"),
        "class": suppress_class(row),
        "tags": row_tags(row),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [as_float(row.get("delta_cents")) or 0.0 for row in rows]
    helpful = [row for row in rows if side_won(row) is True]
    harmful = [row for row in rows if side_won(row) is False]
    return {
        "rows": len(rows),
        "net_delta_cents": sum(deltas),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "helpful_delta_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in helpful),
        "harmful_delta_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in harmful),
        "tag_counts": dict(sorted(Counter(tag for row in rows for tag in row_tags(row)).items())),
    }


def hour_key(row: dict[str, Any]) -> str:
    dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
    if dt is None:
        return "unknown"
    return dt.strftime("%Y-%m-%dT%H:00Z")


def build_cumulative(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    running = 0.0
    helpful = 0.0
    harmful = 0.0
    for idx, row in enumerate(rows, start=1):
        delta = as_float(row.get("delta_cents")) or 0.0
        running += delta
        if side_won(row) is True:
            helpful += delta
        elif side_won(row) is False:
            harmful += delta
        compact = compact_row(row)
        compact.update({
            "suppression_index": idx,
            "cumulative_delta_cents": running,
            "cumulative_helpful_delta_cents": helpful,
            "cumulative_harmful_delta_cents": harmful,
        })
        out.append(compact)
    return out


def interpretation(report: dict[str, Any]) -> list[str]:
    overall = report.get("overall") or {}
    before_latest = report.get("before_latest_suppression") or {}
    latest = report.get("latest_suppression") or {}
    harmful = report.get("harmful_suppressions") or []
    notes = [
        "This audit uses only the frozen reduce-suppression research rows; it does not alter exits or live trading.",
        (
            f"Blanket suppression remains positive at {overall.get('net_delta_cents')}c across "
            f"{overall.get('rows')} suppressed exits, but harmful rows cost "
            f"{overall.get('harmful_delta_cents')}c."
        ),
    ]
    if latest:
        notes.append(
            "Before the latest suppressed exit, the lane was "
            f"{before_latest.get('net_delta_cents')}c; the latest row added "
            f"{latest.get('delta_cents')}c and is tagged {latest.get('tags')}."
        )
    if harmful:
        worst = harmful[0]
        notes.append(
            "Worst harmful suppression is "
            f"{worst.get('market')} with delta {worst.get('delta_cents')}c, "
            f"p_hold {worst.get('p_hold')}, and fair drawdown {worst.get('fair_drawdown_cents')}c."
        )
    notes.append(
        "Next exit research should isolate the harmful probability-reduce states before broadening suppression."
    )
    return notes


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    rows = [
        row for row in (source.get("rows") or [])
        if isinstance(row, dict) and row.get("suppressed") is True
    ]
    rows.sort(key=lambda row: str(row.get("exit_ts") or row.get("entry_ts") or ""))
    by_hour: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_hour[hour_key(row)].append(row)
    harmful = sorted(
        [compact_row(row) for row in rows if side_won(row) is False],
        key=lambda row: as_float(row.get("delta_cents")) or 0.0,
    )
    cumulative = build_cumulative(rows)
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_path": str(SOURCE_JSON),
        "freeze": source.get("freeze") or {},
        "source_summary": source.get("summary") or {},
        "source_blockers": source.get("blockers") or [],
        "overall": summarize(rows),
        "before_latest_suppression": summarize(rows[:-1]) if rows else {},
        "latest_suppression": compact_row(rows[-1]) if rows else {},
        "last_three_suppressions": summarize(rows[-3:]) if rows else {},
        "hourly_summaries": {name: summarize(items) for name, items in sorted(by_hour.items())},
        "harmful_suppressions": harmful,
        "suppression_sequence": cumulative,
    }
    report["interpretation"] = interpretation(report)
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    latest = report.get("latest_suppression") or {}
    overall = report.get("overall") or {}
    lines = [
        "# v28 Exit Reduce Suppression Drift Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Candidate: `{(report.get('freeze') or {}).get('candidate')}`",
        f"- Suppressed exits/net delta: `{overall.get('rows')}/{fmt(overall.get('net_delta_cents'))}c`",
        f"- Helpful/harmful delta: `{fmt(overall.get('helpful_delta_cents'))}c/{fmt(overall.get('harmful_delta_cents'))}c`",
        f"- Latest suppressed row: `{latest.get('market')}` delta `{fmt(latest.get('delta_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Hourly Suppression Drift",
        "",
        "| hour | rows | net delta c | helpful | harmful | tags |",
        "|---|---:|---:|---:|---:|---|",
    ])
    for hour, summary in (report.get("hourly_summaries") or {}).items():
        lines.append(
            f"| {hour} | {summary.get('rows')} | {fmt(summary.get('net_delta_cents'))} | "
            f"{summary.get('helpful_rows')} | {summary.get('harmful_rows')} | {summary.get('tag_counts')} |"
        )
    lines.extend([
        "",
        "## Harmful Suppressions",
        "",
        "| market | side | result | exit_ts | p_hold | drawdown | current c | hold c | delta c | worst mark | tags |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("harmful_suppressions") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_ts')} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_cents'))} | {fmt(row.get('worst_post_exit_hold_mark_cents'))} | "
            f"{', '.join(row.get('tags') or [])} |"
        )
    lines.extend([
        "",
        "## Suppression Sequence",
        "",
        "| idx | market | exit_ts | class | delta c | cumulative c | p_hold | drawdown | tags |",
        "|---:|---|---|---|---:|---:|---:|---:|---|",
    ])
    for row in report.get("suppression_sequence") or []:
        lines.append(
            f"| {row.get('suppression_index')} | {row.get('market')} | {row.get('exit_ts')} | "
            f"{row.get('class')} | {fmt(row.get('delta_cents'))} | "
            f"{fmt(row.get('cumulative_delta_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
