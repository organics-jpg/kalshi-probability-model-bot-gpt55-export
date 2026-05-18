"""Frozen forward validator for weak-reversal residual repair.

Research-only; no live bot changes or orders.

This freezes the current best discovery policy:
    weak_reversal_skip_edge_5_8pp_no_repair_farthest_boundary

The validator scores only markets after its freeze timestamp, so the attractive
discovery result cannot silently keep moving as new rows arrive.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import apply_policy
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, POLICY, summarize
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_weak_boundary_reversal_bakeoff import run_variant
from probe_v28_weak_reversal_residual_repair import (
    ceil_entries_for_floor,
    compact_key,
    edge_between,
    net_ready,
    repair_pool,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FREEZE_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_repair_freeze.json"
OUT_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_weak_reversal_residual_repair_latest.md"

FROZEN_POLICY = "weak_reversal_skip_edge_5_8pp_no_repair_farthest_boundary"


def ensure_freeze() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if FREEZE_JSON.exists():
        return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    payload = {
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "policy": FROZEN_POLICY,
        "base_target_policy": POLICY,
        "weak_reversal": {
            "p_max": 0.60,
            "recross_floor": 0.75,
            "abs_d_max": 0.25,
            "max_delay": 240.0,
            "no_replacement_mode": "abstain",
        },
        "residual_skip": {
            "side": "no",
            "raw_edge_low": 0.05,
            "raw_edge_high": 0.08,
            "repair_scorer": "farthest_boundary",
        },
    }
    FREEZE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_surfaces(freeze: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, set[str]]:
    freeze_dt = parse_ts(freeze.get("freeze_ts_utc"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets), forward_markets


def skip_residual(row: dict[str, Any]) -> bool:
    return str(row.get("side")) == "no" and edge_between(row, 0.05, 0.08)


def build_report() -> dict[str, Any]:
    freeze = ensure_freeze()
    all_rows, target, denominator, forward_markets = build_surfaces(freeze)
    weak_base = run_variant(
        all_rows=all_rows,
        target=target,
        denominator=denominator,
        forward_markets=forward_markets,
        p_max=0.60,
        recross_floor=0.75,
        abs_d_max=0.25,
        max_delay=240.0,
        no_replacement_mode="abstain",
    )
    base_rows = [net_ready(row) for row in weak_base.get("candidate_rows") or []]
    skipped = [row for row in base_rows if skip_residual(row)]
    skipped_keys = {compact_key(row) for row in skipped}
    kept = [row for row in base_rows if compact_key(row) not in skipped_keys]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
    target_markets = {str(row.get("market") or "") for row in target}
    unavailable = {str(row.get("market") or "") for row in kept + skipped} | target_markets
    repairs = repair_pool(all_rows, unavailable, forward_markets, needed)
    candidate = kept + repairs
    candidate_summary = summarize(candidate, denominator)
    blockers = []
    if candidate_summary.get("settled", 0) < 30:
        blockers.append("settled_lt_30")
    if float(candidate_summary.get("net_cents") or 0.0) <= 0:
        blockers.append("net_not_positive")
    coverage = candidate_summary.get("coverage_pct")
    if coverage is None or float(coverage) < COVERAGE_FLOOR:
        blockers.append("coverage_below_floor")
    return {
        "diagnostic": "frozen_weak_reversal_residual_repair",
        "freeze": freeze,
        "future_denominator": denominator,
        "policy": FROZEN_POLICY,
        "target_summary": summarize(target, denominator),
        "weak_reversal_summary": weak_base.get("candidate_summary"),
        "skipped_summary": summarize(skipped, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_weak_reversal_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float((weak_base.get("candidate_summary") or {}).get("net_cents") or 0.0),
        "needed_repairs": needed,
        "chosen_repairs": len(repairs),
        "blockers": blockers,
        "live_ready": not blockers,
        "interpretation": interpretation(candidate_summary, blockers, denominator),
    }


def interpretation(candidate: dict[str, Any], blockers: list[str], denominator: int) -> list[str]:
    notes = [
        f"Frozen forward denominator is {denominator}; candidate has {candidate.get('settled')} settled rows and net {candidate.get('net_cents')}c.",
    ]
    if blockers:
        notes.append(f"Promotion blocked by: {', '.join(blockers)}.")
    notes.append("This is a forward validator, not live order logic.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Weak-Reversal Residual Repair",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Live ready: `{report.get('live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Summaries",
            "",
            "| slice | entries | settled | W/L | coverage | net c | avg c |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name, key in [
        ("target", "target_summary"),
        ("weak_reversal", "weak_reversal_summary"),
        ("skipped", "skipped_summary"),
        ("repairs", "repair_summary"),
        ("candidate", "candidate_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
