"""Opportunity audit for frozen exit reduce geometry suppression.

Research-only; no live bot changes or orders.

The frozen side-geometry reduce suppressor can look inactive because either
probability-reduce exits are absent, p_hold is below threshold, or the
side/drawdown geometry rejects otherwise eligible base suppressions. This
report separates those cases and quantifies the current cost of geometry
strictness versus the base p_hold suppressor on post-freeze rows.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.md"

P_HOLD_FLOOR = 0.75


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
    side = str(row.get("side") or "").lower()
    result = str(row.get("result") or "").lower()
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def is_probability_reduce(row: dict[str, Any]) -> bool:
    return str(row.get("exit_reason") or "") == "mushroom_v28_probability_reduce"


def base_candidate(row: dict[str, Any]) -> bool:
    return is_probability_reduce(row) and (as_float(row.get("p_hold")) or 0.0) >= P_HOLD_FLOOR


def geometry_pass(row: dict[str, Any]) -> bool:
    side = str(row.get("side") or "").lower()
    drawdown = as_float(row.get("fair_drawdown_cents"))
    if drawdown is None:
        return False
    if side == "yes":
        return drawdown >= 0.0
    if side == "no":
        return drawdown <= 0.0
    return False


def fail_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    p_hold = as_float(row.get("p_hold"))
    drawdown = as_float(row.get("fair_drawdown_cents"))
    side = str(row.get("side") or "").lower()
    if not is_probability_reduce(row):
        reasons.append("not_probability_reduce")
    if p_hold is None:
        reasons.append("p_hold_missing")
    elif p_hold < P_HOLD_FLOOR:
        reasons.append("p_hold_below_floor")
    if drawdown is None:
        reasons.append("fair_drawdown_missing")
    elif side == "yes" and drawdown < 0:
        reasons.append("yes_negative_drawdown_reject")
    elif side == "no" and drawdown > 0:
        reasons.append("no_positive_drawdown_reject")
    elif side not in {"yes", "no"}:
        reasons.append("side_missing")
    return reasons


def row_delta_if_suppressed(row: dict[str, Any]) -> float:
    current = as_float(row.get("current_cents")) or 0.0
    hold = as_float(row.get("hold_cents")) or 0.0
    return hold - current


def digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": side_won(row),
        "exit_reason": row.get("exit_reason"),
        "p_hold": as_float(row.get("p_hold")),
        "fair_drawdown_cents": as_float(row.get("fair_drawdown_cents")),
        "current_cents": as_float(row.get("current_cents")),
        "hold_cents": as_float(row.get("hold_cents")),
        "delta_if_suppressed_cents": row_delta_if_suppressed(row),
        "fail_reasons": fail_reasons(row),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "net_delta_if_suppressed_cents": sum(row_delta_if_suppressed(row) for row in rows),
        "winners": sum(1 for row in rows if side_won(row) is True),
        "losers": sum(1 for row in rows if side_won(row) is False),
        "positive_delta_rows": sum(1 for row in rows if row_delta_if_suppressed(row) > 0),
        "negative_delta_rows": sum(1 for row in rows if row_delta_if_suppressed(row) < 0),
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    rows = [row for row in source.get("rows") or [] if isinstance(row, dict)]
    reduce_rows = [row for row in rows if is_probability_reduce(row)]
    base_rows = [row for row in reduce_rows if base_candidate(row)]
    geometry_rows = [row for row in base_rows if geometry_pass(row)]
    rejected_by_geometry = [row for row in base_rows if not geometry_pass(row)]
    reason_counts: Counter[str] = Counter()
    for row in rows:
        reason_counts.update(fail_reasons(row) or ["would_suppress"])

    strictness_cost = sum(row_delta_if_suppressed(row) for row in rejected_by_geometry)
    blockers = []
    if len(rows) < 30:
        blockers.append("settled_lt_30")
    if len(geometry_rows) < 30:
        blockers.append("geometry_suppressed_decisions_lt_30")
    if sum(row_delta_if_suppressed(row) for row in geometry_rows) <= 0:
        blockers.append("geometry_delta_not_positive")
    if strictness_cost > 0:
        blockers.append("geometry_rejected_positive_base_opportunity")

    interpretation = [
        "This audit explains frozen geometry opportunity only; it does not change any exit rule.",
        f"Post-freeze rows {len(rows)}, probability-reduce rows {len(reduce_rows)}, base p_hold candidates {len(base_rows)}, geometry would-suppress rows {len(geometry_rows)}.",
        f"Geometry rejected {len(rejected_by_geometry)} base p_hold candidates for {strictness_cost}c net base opportunity cost.",
        f"Blockers {blockers}.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(SOURCE_JSON),
        "freeze": source.get("freeze") or {},
        "summary": {
            "post_freeze_rows": len(rows),
            "probability_reduce_rows": len(reduce_rows),
            "base_p_hold_candidates": len(base_rows),
            "geometry_would_suppress_rows": len(geometry_rows),
            "geometry_rejected_base_candidates": len(rejected_by_geometry),
            "geometry_rejected_base_delta_cents": strictness_cost,
            "reason_counts": dict(reason_counts),
            "geometry_summary": summarize(geometry_rows),
            "rejected_by_geometry_summary": summarize(rejected_by_geometry),
            "blockers": blockers,
        },
        "geometry_rows": [digest(row) for row in geometry_rows],
        "rejected_by_geometry_rows": [digest(row) for row in rejected_by_geometry],
        "near_miss_rows": [digest(row) for row in rows if not base_candidate(row)][:20],
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    lines = [
        "# v28 Exit Reduce Geometry Opportunity",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ])
    for key in [
        "post_freeze_rows",
        "probability_reduce_rows",
        "base_p_hold_candidates",
        "geometry_would_suppress_rows",
        "geometry_rejected_base_candidates",
        "geometry_rejected_base_delta_cents",
    ]:
        lines.append(f"| {key} | {fmt(summary.get(key))} |")
    lines.extend([
        "",
        f"- Reason counts: `{summary.get('reason_counts')}`",
        f"- Blockers: `{', '.join(summary.get('blockers') or []) or 'none'}`",
        "",
        "## Geometry Would-Suppress Rows",
        "",
        "| market | side | result | p_hold | drawdown | current c | hold c | delta c |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("geometry_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} |"
        )
    lines.extend([
        "",
        "## Rejected Base P-Hold Candidates",
        "",
        "| market | side | result | p_hold | drawdown | current c | hold c | delta c | fail reasons |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rejected_by_geometry_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} | {', '.join(row.get('fail_reasons') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
