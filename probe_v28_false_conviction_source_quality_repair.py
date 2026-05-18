"""Source-quality repair diagnostic for the lead false-conviction lane.

Research-only; no live bot changes or orders.

Question:
    The early-boundary false-conviction repair lane is positive, but too much
    of its evidence is reconstructed. Can we preserve 75%+ coverage while
    prioritizing actual v28-approved rows, or is the current forward pool short
    of approved replacements?
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float, is_clean_repair, raw_edge, row_net_after_fee, summarize
from probe_v28_frozen_early_no_boundary_decay_repair_entry import (
    build_candidate,
    danger_reasons,
    future_surfaces,
    is_danger,
    load_or_create_state,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_false_conviction_source_quality_repair_latest.json"
OUT_MD = OUT_DIR / "v28_false_conviction_source_quality_repair_latest.md"

MAX_RECONSTRUCTED_SHARE = 0.35


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def recross(row: dict[str, Any]) -> float:
    return as_float(row.get("recross_hazard_score")) or 999.0


def abs_d(row: dict[str, Any]) -> float:
    return as_float(row.get("abs_d_sigma")) or 0.0


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def row_with_net(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **row,
        "raw_edge_prob": raw_edge(row),
        "net_gross_cents_after_entry_fee": row_net_after_fee(row),
    }


def candidate_pool(all_rows: list[dict[str, Any]], allowed_markets: set[str]) -> list[dict[str, Any]]:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in all_rows:
        ticker = market(row)
        if ticker not in allowed_markets:
            continue
        if is_clean_repair(row):
            by_market.setdefault(ticker, []).append(row_with_net(row))
    rows = []
    for ticker_rows in by_market.values():
        rows.append(rank_approved_first(ticker_rows)[0])
    return rows


def rank_approved_first(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            0 if source(row) == "approved_entry" else 1,
            -abs_d(row),
            recross(row),
            str(row.get("ts_wall") or ""),
        ),
    )


def rank_min_reconstructed(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            0 if source(row) == "approved_entry" else 1,
            -(as_float(row.get("p_side")) or 0.0),
            recross(row),
            str(row.get("ts_wall") or ""),
        ),
    )


def first_n_unique(rows: list[dict[str, Any]], count: int, blocked: set[str]) -> list[dict[str, Any]]:
    out = []
    seen = set(blocked)
    for row in rows:
        ticker = market(row)
        if not ticker or ticker in seen:
            continue
        out.append(row)
        seen.add(ticker)
        if len(out) >= count:
            break
    return out


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    reconstructed = sum(1 for row in rows if source(row) != "approved_entry")
    return reconstructed / len(rows)


def approved_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if source(row) == "approved_entry")


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
    all_rows, target, denominator = future_surfaces(str(state["freeze_ts_utc"]))
    base = build_candidate(all_rows, target, denominator)
    target_markets = {market(row) for row in target}
    danger_markets = {market(row) for row in base["danger"]}
    kept = [row_with_net(row) for row in target if market(row) not in danger_markets]
    kept_markets = {market(row) for row in kept}
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
    all_markets = {market(row) for row in all_rows if market(row)}
    allowed = all_markets - kept_markets
    pool = candidate_pool(all_rows, allowed)
    pool_missed = [row for row in pool if market(row) not in target_markets]
    pool_same_surface = [row for row in pool if market(row) in target_markets]

    scenarios = []
    for name, ranked_pool in [
        ("approved_first_missed_then_any", rank_approved_first(pool_missed) + rank_approved_first(pool_same_surface)),
        ("min_reconstructed_high_p", rank_min_reconstructed(pool_missed) + rank_min_reconstructed(pool_same_surface)),
        ("approved_only", [row for row in rank_approved_first(pool) if source(row) == "approved_entry"]),
    ]:
        repairs = first_n_unique(ranked_pool, needed, kept_markets)
        candidate = kept + repairs
        summary = summarize(candidate, denominator)
        scenario = {
            "scenario": name,
            "needed_repairs": needed,
            "repair_count": len(repairs),
            "candidate_summary": summary,
            "reconstructed_share": reconstructed_share(candidate),
            "approved_count": approved_count(candidate),
            "reconstructed_count": len(candidate) - approved_count(candidate),
            "passes_source_quality": (reconstructed_share(candidate) is not None and reconstructed_share(candidate) <= MAX_RECONSTRUCTED_SHARE),
            "passes_coverage": (summary.get("coverage_pct") is not None and float(summary["coverage_pct"]) >= COVERAGE_FLOOR),
            "repair_rows": [compact(row) for row in repairs],
        }
        scenario["blockers"] = blockers(scenario)
        scenarios.append(scenario)

    approved_pool = [row for row in pool if source(row) == "approved_entry"]
    return {
        "freeze": state,
        "future_denominator": denominator,
        "coverage_floor": COVERAGE_FLOOR,
        "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
        "kept_summary": summarize(kept, denominator),
        "danger_summary": summarize(base["danger"], denominator),
        "needed_repairs": needed,
        "pool_counts": {
            "clean_pool": len(pool),
            "approved_clean_pool": len(approved_pool),
            "reconstructed_clean_pool": len(pool) - len(approved_pool),
            "missed_market_clean_pool": len(pool_missed),
            "same_surface_clean_pool": len(pool_same_surface),
        },
        "scenarios": scenarios,
        "current_read": current_read(denominator, kept, needed, pool, scenarios),
    }


def blockers(scenario: dict[str, Any]) -> list[str]:
    out = []
    summary = scenario.get("candidate_summary") or {}
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents")) or 0.0
    if not scenario.get("passes_coverage"):
        out.append("coverage_too_low")
    if not scenario.get("passes_source_quality"):
        out.append("reconstructed_share_gt_35pct")
    if net <= 0:
        out.append("net_not_positive")
    return out


def current_read(
    denominator: int,
    kept: list[dict[str, Any]],
    needed: int,
    pool: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> list[str]:
    min_entries = ceil_entries_for_floor(denominator)
    approved_kept = approved_count(kept)
    max_recon = int(MAX_RECONSTRUCTED_SHARE * min_entries)
    required_approved = min_entries - max_recon
    approved_pool_available = sum(1 for row in pool if source(row) == "approved_entry")
    notes = [
        f"Coverage floor needs {min_entries} entries from denominator {denominator}; kept after danger skip is {len(kept)}, so repairs needed are {needed}.",
        f"To keep reconstructed share <=35%, at least {required_approved} of {min_entries} entries must be approved-entry rows.",
        f"Approved kept rows: {approved_kept}; approved clean repair rows currently available: {approved_pool_available}.",
    ]
    best = next((row for row in scenarios if row.get("passes_coverage") and row.get("passes_source_quality")), None)
    if best:
        notes.append(f"Source-quality feasible now via {best.get('scenario')}.")
    else:
        notes.append("Source-quality plus 75% coverage is not feasible with the current forward pool.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 False-Conviction Source-Quality Repair",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("current_read") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Pool",
        "",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Needed repairs: `{report.get('needed_repairs')}`",
        f"- Pool counts: `{report.get('pool_counts')}`",
        "",
        "## Scenarios",
        "",
        "| scenario | entries | settled | W/L | coverage | net c | approved/recon | recon share | source pass | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("scenarios") or []:
        summary = row.get("candidate_summary") or {}
        lines.append(
            f"| `{row.get('scenario')}` | {summary.get('entries')} | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {row.get('approved_count')}/{row.get('reconstructed_count')} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('passes_source_quality')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
