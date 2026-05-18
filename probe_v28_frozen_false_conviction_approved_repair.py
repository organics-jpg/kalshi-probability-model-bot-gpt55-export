"""Frozen approved-heavy repair for the false-conviction lane.

Research-only; no live bot changes or orders.

Frozen rule:
    Start from the target-coverage policy. Remove the early-boundary
    false-conviction danger rows from the early-NO boundary-decay candidate.
    Restore the 75% coverage floor using clean repair rows, prioritizing rows
    that were actual v28 approved-entry opportunities. This tests whether the
    false-conviction idea survives the source-quality problem.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float, is_clean_repair, raw_edge, row_net_after_fee, summarize
from probe_v28_frozen_early_no_boundary_decay_repair_entry import (
    danger_reasons,
    future_surfaces,
    is_danger,
)
from probe_v28_frozen_forward_candidates import parse_ts


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_false_conviction_approved_repair_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_false_conviction_approved_repair_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_false_conviction_approved_repair_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35


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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "skip_false_conviction_repair_approved_heavy",
        "coverage_floor": COVERAGE_FLOOR,
        "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
        "base_policy": "raw_p50_turbulence_valve_edge4_p60_recross75_near25",
        "danger_rule": "early NO boundary decay OR cheap near-boundary turbulence",
        "repair_rule": "clean repair rows ranked approved-entry first, then far boundary / low recross",
        "physics": "If false-conviction filtering is real, the replacement rows should not require mostly rejected-actionable reconstruction; approved-entry replacements are a stricter source-quality test.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def recross(row: dict[str, Any]) -> float:
    return as_float(row.get("recross_hazard_score")) or 999.0


def abs_d(row: dict[str, Any]) -> float:
    return as_float(row.get("abs_d_sigma")) or 0.0


def with_net(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **row,
        "raw_edge_prob": raw_edge(row),
        "net_gross_cents_after_entry_fee": row_net_after_fee(row),
    }


def repair_rank(row: dict[str, Any]) -> tuple[int, float, float, str]:
    return (
        0 if source(row) == "approved_entry" else 1,
        -abs_d(row),
        recross(row),
        str(row.get("ts_wall") or ""),
    )


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def clean_pool_by_market(all_rows: list[dict[str, Any]], allowed_markets: set[str]) -> list[dict[str, Any]]:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in all_rows:
        ticker = market(row)
        if ticker not in allowed_markets:
            continue
        if is_clean_repair(row):
            by_market.setdefault(ticker, []).append(with_net(row))
    out = []
    for rows in by_market.values():
        out.append(sorted(rows, key=repair_rank)[0])
    return sorted(out, key=repair_rank)


def choose_repairs(pool: list[dict[str, Any]], needed: int, blocked_markets: set[str]) -> list[dict[str, Any]]:
    out = []
    seen = set(blocked_markets)
    approved_first = [row for row in pool if source(row) == "approved_entry"]
    remainder = [row for row in pool if source(row) != "approved_entry"]
    for row in approved_first + remainder:
        ticker = market(row)
        if not ticker or ticker in seen:
            continue
        out.append(row)
        seen.add(ticker)
        if len(out) >= needed:
            break
    return out


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if source(row) != "approved_entry") / len(rows)


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "danger_reasons": danger_reasons(row),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    # Validate timestamp format early; future_surfaces performs the actual market filtering.
    parse_ts(str(state["freeze_ts_utc"]))
    all_rows, target, denominator = future_surfaces(str(state["freeze_ts_utc"]))
    danger = [row for row in target if is_danger(row)]
    danger_markets = {market(row) for row in danger}
    kept = [with_net(row) for row in target if market(row) not in danger_markets]
    kept_markets = {market(row) for row in kept}
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
    all_markets = {market(row) for row in all_rows if market(row)}
    pool = clean_pool_by_market(all_rows, all_markets - kept_markets)
    repairs = choose_repairs(pool, needed, kept_markets)
    candidate = kept + repairs
    summary = summarize(candidate, denominator)
    recon = reconstructed_share(candidate)
    blockers = []
    if int(as_float(summary.get("settled")) or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if summary.get("coverage_pct") is None or float(summary["coverage_pct"]) < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if float(summary.get("net_cents") or 0.0) <= 0:
        blockers.append("net_not_positive")
    if recon is None or recon > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "needed_repairs": needed,
        "target_summary": summarize(target, denominator),
        "danger_summary": summarize(danger, denominator),
        "kept_summary": summarize(kept, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": summary,
        "reconstructed_share": recon,
        "approved_count": sum(1 for row in candidate if source(row) == "approved_entry"),
        "reconstructed_count": sum(1 for row in candidate if source(row) != "approved_entry"),
        "pool_counts": {
            "clean_pool": len(pool),
            "approved_clean_pool": sum(1 for row in pool if source(row) == "approved_entry"),
            "reconstructed_clean_pool": sum(1 for row in pool if source(row) != "approved_entry"),
        },
        "danger_rows": [compact(row) for row in danger],
        "repair_rows": [compact(row) for row in repairs],
        "blockers": blockers,
        "candidate_live_ready": not blockers,
        "interpretation": interpretation(summary, recon, blockers, denominator),
    }


def interpretation(summary: dict[str, Any], recon: float | None, blockers: list[str], denominator: int) -> list[str]:
    return [
        f"Frozen approved-heavy candidate denominator {denominator}, entries {summary.get('entries')}, settled {summary.get('settled')}, coverage {summary.get('coverage_pct')}, net {summary.get('net_cents')}c.",
        f"Reconstructed share is {recon}.",
        f"Blockers: {', '.join(blockers) or 'none'}.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    candidate = report.get("candidate_summary") or {}
    repairs = report.get("repair_summary") or {}
    lines = [
        "# v28 Frozen False-Conviction Approved Repair",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Live ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summary",
        "",
        f"- Candidate entries/settled/coverage/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt(candidate.get('coverage_pct'))}/{fmt(candidate.get('net_cents'))}c`",
        f"- Candidate W/L: `{candidate.get('wins')}/{candidate.get('losses')}`",
        f"- Approved/reconstructed count: `{report.get('approved_count')}/{report.get('reconstructed_count')}`",
        f"- Reconstructed share: `{fmt(report.get('reconstructed_share'))}`",
        f"- Repair entries/settled/net: `{repairs.get('entries')}/{repairs.get('settled')}/{fmt(repairs.get('net_cents'))}c`",
        f"- Pool counts: `{report.get('pool_counts')}`",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
