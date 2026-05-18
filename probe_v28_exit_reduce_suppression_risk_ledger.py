"""Risk ledger for frozen v28 probability-reduce exit suppression.

Research-only; no live bot changes or orders.

The reduce-suppression candidate recovers clipped winners, but its blocker is
loss-control cost from suppressed exits that should have been respected. This
ledger classifies those suppressed rows so the exit repair can move toward a
physical rule instead of a blanket hold.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_suppression_risk_ledger_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_suppression_risk_ledger_latest.md"


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


def side_won(row: dict[str, Any]) -> bool | None:
    side = str(row.get("side") or "")
    result = str(row.get("result") or "")
    if not side or not result:
        return None
    if result not in {"yes", "no"}:
        return None
    return side == result


def suppressed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("suppressed") is True]


def row_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    won = side_won(row)
    p_hold = as_float(row.get("p_hold"))
    drawdown = as_float(row.get("fair_drawdown_cents"))
    worst = as_float(row.get("worst_post_exit_hold_mark_cents"))
    delta = as_float(row.get("delta_cents")) or 0.0
    entry = as_float(row.get("entry_cents"))
    if won is True:
        tags.append("winner_recovery")
    elif won is False:
        tags.append("loss_control_cost")
    else:
        tags.append("unknown_outcome")
    if p_hold is not None:
        if p_hold >= 0.79:
            tags.append("very_high_p_hold")
        elif p_hold >= 0.75:
            tags.append("marginal_p_hold")
    if drawdown is not None:
        if drawdown < 0:
            tags.append("favorable_fair_value")
        elif drawdown <= 2.5:
            tags.append("small_fair_drawdown")
        elif drawdown <= 5.0:
            tags.append("moderate_fair_drawdown")
        else:
            tags.append("large_fair_drawdown")
    if worst is not None:
        if worst < 0:
            tags.append("post_exit_mark_went_full_loss")
        elif entry is not None and worst < entry - 40:
            tags.append("large_adverse_mark_after_exit")
        elif entry is not None and worst < entry - 20:
            tags.append("moderate_adverse_mark_after_exit")
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
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "p_hold": row.get("p_hold"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "current_cents": row.get("current_cents"),
        "hold_cents": row.get("hold_cents"),
        "candidate_cents": row.get("candidate_cents"),
        "delta_cents": row.get("delta_cents"),
        "worst_post_exit_hold_mark_cents": row.get("worst_post_exit_hold_mark_cents"),
        "tags": row_tags(row),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [as_float(row.get("delta_cents")) or 0.0 for row in rows]
    current = [as_float(row.get("current_cents")) or 0.0 for row in rows]
    hold = [as_float(row.get("hold_cents")) or 0.0 for row in rows]
    p_holds = [as_float(row.get("p_hold")) for row in rows]
    p_holds = [value for value in p_holds if value is not None]
    drawdowns = [as_float(row.get("fair_drawdown_cents")) for row in rows]
    drawdowns = [value for value in drawdowns if value is not None]
    tags = Counter(tag for row in rows for tag in row_tags(row))
    return {
        "rows": len(rows),
        "net_delta_cents": sum(deltas),
        "current_cents": sum(current),
        "hold_cents": sum(hold),
        "avg_delta_cents": None if not rows else sum(deltas) / len(rows),
        "avg_p_hold": None if not p_holds else mean(p_holds),
        "avg_fair_drawdown_cents": None if not drawdowns else mean(drawdowns),
        "tag_counts": dict(sorted(tags.items())),
    }


def grouped_summaries(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        won = side_won(row)
        if won is True:
            groups["winner_recovery"].append(row)
        elif won is False:
            groups["loss_control_cost"].append(row)
        else:
            groups["unknown_outcome"].append(row)
        p_hold = as_float(row.get("p_hold"))
        if p_hold is not None:
            groups["p_hold_ge_079" if p_hold >= 0.79 else "p_hold_075_079"].append(row)
        drawdown = as_float(row.get("fair_drawdown_cents"))
        if drawdown is not None:
            if drawdown <= 2.5:
                groups["drawdown_lte_2p5"].append(row)
            elif drawdown <= 5.0:
                groups["drawdown_2p5_5"].append(row)
            else:
                groups["drawdown_gt_5"].append(row)
    return {name: summarize(items) for name, items in sorted(groups.items())}


def build_report() -> dict[str, Any]:
    payload = load_json(SOURCE_JSON)
    rows = [row for row in payload.get("rows") or [] if isinstance(row, dict)]
    suppressed = suppressed_rows(rows)
    harmful = [row for row in suppressed if side_won(row) is False]
    helpful = [row for row in suppressed if side_won(row) is True]
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_path": str(SOURCE_JSON),
        "freeze": payload.get("freeze") or {},
        "source_blockers": payload.get("blockers") or [],
        "all_rows_summary": summarize(rows),
        "suppressed_summary": summarize(suppressed),
        "helpful_suppressed_summary": summarize(helpful),
        "harmful_suppressed_summary": summarize(harmful),
        "suppressed_group_summaries": grouped_summaries(suppressed),
        "harmful_rows": [compact_row(row) for row in sorted(harmful, key=lambda item: as_float(item.get("delta_cents")) or 0.0)],
        "helpful_rows": [compact_row(row) for row in sorted(helpful, key=lambda item: as_float(item.get("delta_cents")) or 0.0, reverse=True)],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    suppressed = report.get("suppressed_summary") or {}
    helpful = report.get("helpful_suppressed_summary") or {}
    harmful = report.get("harmful_suppressed_summary") or {}
    groups = report.get("suppressed_group_summaries") or {}
    notes = [
        "This ledger classifies only already-frozen reduce-suppression rows; it does not change exit policy.",
        f"Suppressed exits net {suppressed.get('net_delta_cents')}c: helpful winner recovery {helpful.get('net_delta_cents')}c versus harmful loss-control cost {harmful.get('net_delta_cents')}c.",
    ]
    for group in ("p_hold_ge_079", "p_hold_075_079", "drawdown_lte_2p5", "drawdown_2p5_5", "drawdown_gt_5"):
        if group in groups:
            summary = groups[group]
            notes.append(
                f"{group}: rows {summary.get('rows')}, net delta {summary.get('net_delta_cents')}c, tags {summary.get('tag_counts')}."
            )
    notes.append("Promotion requires converting this into a forward-tested loss-control repair, because blanket suppression still has harmful rows.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| market | side | result | entry | exit | p_hold | drawdown | current c | hold c | delta c | worst mark | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('current_cents'))} | "
            f"{fmt(row.get('hold_cents'))} | {fmt(row.get('delta_cents'))} | "
            f"{fmt(row.get('worst_post_exit_hold_mark_cents'))} | {', '.join(row.get('tags') or [])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Reduce Suppression Risk Ledger",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Candidate: `{(report.get('freeze') or {}).get('candidate')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Group Summaries", ""])
    lines.extend(
        [
            "| group | rows | net delta c | avg p_hold | avg drawdown | tags |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for name, summary in (report.get("suppressed_group_summaries") or {}).items():
        lines.append(
            f"| {name} | {summary.get('rows')} | {fmt(summary.get('net_delta_cents'))} | "
            f"{fmt(summary.get('avg_p_hold'))} | {fmt(summary.get('avg_fair_drawdown_cents'))} | "
            f"{summary.get('tag_counts')} |"
        )
    lines.extend(["", "## Harmful Suppressed Rows", ""])
    write_rows(lines, report.get("harmful_rows") or [])
    lines.extend(["", "## Helpful Suppressed Rows", ""])
    write_rows(lines, report.get("helpful_rows") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
