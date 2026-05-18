"""Combined hybrid-veto, boundary-clock, and early-NO repair probe.

Research-only; no live bot changes or orders.

This asks the current handoff question directly: can the hybrid-veto warning,
boundary-clock repair, and early-NO boundary-decay repair combine into a broad
75%+ coverage candidate that is profitable on frozen forward rows?
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_fv_entry_bridge import adjusted_edge
from probe_v28_boundary_clock_hazard_repair import clock_composite
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float
from probe_v28_frozen_early_no_boundary_decay_repair_entry import is_danger as early_no_boundary_danger
from probe_v28_target_coverage_fv_overlay_validator import STATE_JSON as TARGET_STATE_JSON
from probe_v28_target_hybrid_veto_repair import (
    ceil_entries_for_floor,
    compact,
    evaluate_window as evaluate_hybrid_veto_window,
    fmt,
    is_hybrid_veto,
    load_json,
    repair_rows_by_market,
    source_counts,
    surface_for_freeze,
    utc_now_iso,
)
from probe_v28_coverage_repair_pool_diagnostic import summarize


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_state.json"
SOURCE_STRESS_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_source_stress_latest.json"
OUT_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.json"
OUT_MD = OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.md"

MIN_SETTLED = 30
TARGET_COVERAGE_MAX = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
BOUNDARY_CLOCK_EDGE_FLOOR = 0.02

REPAIR_MODES = (
    ("hybrid_edge_repair", True, "score"),
    ("raw_clean_repair", False, "score"),
    ("approved_first_hybrid_edge_repair", True, "approved_first"),
    ("approved_first_raw_clean_repair", False, "approved_first"),
    ("approved_only_hybrid_edge_repair", True, "approved_only"),
    ("approved_only_raw_clean_repair", False, "approved_only"),
    ("source_cap35_hybrid_edge_repair", True, "source_cap35"),
    ("source_cap35_raw_clean_repair", False, "source_cap35"),
)


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    payload = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "hybrid_boundary_entry_stack",
        "coverage_floor": COVERAGE_FLOOR,
        "components": [
            "target_hybrid_veto_warning",
            "boundary_clock_composite_repair",
            "boundary_clock_adjusted_edge_floor",
            "early_no_boundary_decay_repair",
        ],
        "physics": (
            "The shared failure mode is false conviction near unresolved boundaries: raw FV clears the ask, "
            "but path churn, clock state, or shrink-to-50 says the edge is fragile. The stack removes those "
            "rows and repairs coverage with cleaner missed-market rows."
        ),
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def boundary_clock_fv_danger(row: dict[str, Any]) -> bool:
    edge = adjusted_edge(row)
    return edge is not None and float(edge) < BOUNDARY_CLOCK_EDGE_FLOOR


def any_boundary_clock_danger(row: dict[str, Any]) -> bool:
    return clock_composite(row) or boundary_clock_fv_danger(row)


def hybrid_or_early(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) or early_no_boundary_danger(row)


def hybrid_or_boundary_clock(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) or any_boundary_clock_danger(row)


def early_or_boundary_clock(row: dict[str, Any]) -> bool:
    return early_no_boundary_danger(row) or any_boundary_clock_danger(row)


def all_three(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) or early_no_boundary_danger(row) or any_boundary_clock_danger(row)


def all_three_without_fv_edge(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) or early_no_boundary_danger(row) or clock_composite(row)


DANGER_RULES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "hybrid_veto_plus_early_no": hybrid_or_early,
    "hybrid_veto_plus_boundary_clock": hybrid_or_boundary_clock,
    "early_no_plus_boundary_clock": early_or_boundary_clock,
    "all_three_without_boundary_fv_edge": all_three_without_fv_edge,
    "all_three_with_boundary_fv_edge": all_three,
}


def source_quality(source_counts: dict[str, int], net_cents: float | None) -> dict[str, Any]:
    total = sum(int(value or 0) for value in source_counts.values())
    approved = int(source_counts.get("approved_entry") or 0)
    reconstructed_share = None if total <= 0 else (total - approved) / total
    full_loss_cushion = None if net_cents is None else int(max(0.0, net_cents) // 100.0)
    source_stress_present = SOURCE_STRESS_JSON.exists()
    blockers: list[str] = []
    if not source_stress_present:
        blockers.append("no_source_stress_audit")
    if reconstructed_share is not None and reconstructed_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if full_loss_cushion is not None and full_loss_cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "candidate_source_counts": source_counts,
        "approved_entry_share": None if total <= 0 else approved / total,
        "reconstructed_share": reconstructed_share,
        "full_loss_cushion_estimate": full_loss_cushion,
        "source_stress_audit_present": source_stress_present,
        "integrity_preview_blockers": blockers,
    }


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    reconstructed = sum(1 for row in rows if str(row.get("source") or "") != "approved_entry")
    return reconstructed / len(rows)


def sort_repairs(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    if mode == "approved_first":
        return sorted(
            rows,
            key=lambda row: (
                str(row.get("source") or "") != "approved_entry",
                -float(row.get("repair_score") or -999.0),
                str(row.get("ts_wall") or ""),
            ),
        )
    if mode == "approved_only":
        return [row for row in rows if str(row.get("source") or "") == "approved_entry"]
    if mode == "source_cap35":
        return sorted(
            rows,
            key=lambda row: (
                str(row.get("source") or "") != "approved_entry",
                -float(row.get("repair_score") or -999.0),
                str(row.get("ts_wall") or ""),
            ),
        )
    return rows


def choose_repairs(
    kept: list[dict[str, Any]],
    repair_pool: list[dict[str, Any]],
    needed: int,
    mode: str,
) -> list[dict[str, Any]]:
    if needed <= 0:
        return []
    ordered = sort_repairs(repair_pool, mode)
    chosen: list[dict[str, Any]] = []
    if mode != "source_cap35":
        return ordered[:needed]
    approved_rows = [row for row in ordered if str(row.get("source") or "") == "approved_entry"]
    other_rows = [row for row in ordered if str(row.get("source") or "") != "approved_entry"]
    for row in approved_rows:
        if len(chosen) >= needed:
            break
        chosen.append(row)
    for row in other_rows:
        if len(chosen) >= needed:
            break
        trial = kept + chosen + [row]
        share = reconstructed_share(trial)
        if share is None or share <= MAX_RECONSTRUCTED_SHARE:
            chosen.append(row)
    return chosen


def build_stack_candidate(
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    denominator: int,
    forward_markets: set[str],
    name: str,
    danger_fn: Callable[[dict[str, Any]], bool],
    require_hybrid_edge: bool,
    repair_mode: str,
) -> dict[str, Any]:
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if danger_fn(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed = repair_rows_by_market(all_rows, forward_markets - target_markets, require_hybrid_edge)
    chosen = choose_repairs(kept, missed, needed, repair_mode)
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed and repair_mode not in {"approved_only", "source_cap35"}:
        kept_markets = {str(row.get("market") or "") for row in kept}
        extras = repair_rows_by_market(
            all_rows,
            forward_markets - kept_markets - chosen_markets,
            require_hybrid_edge,
        )
        extra_chosen = choose_repairs(kept + chosen, extras, needed - len(chosen), repair_mode)
        for row in extra_chosen:
            market = str(row.get("market") or "")
            if market in chosen_markets:
                continue
            chosen.append(row)
            chosen_markets.add(market)

    candidate = kept + chosen
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    return {
        "candidate": name,
        "require_hybrid_edge_repair": require_hybrid_edge,
        "repair_mode": repair_mode,
        "target_summary": target_summary,
        "danger_summary": summarize(danger, denominator),
        "kept_summary": summarize(kept, denominator),
        "repair_summary": summarize(chosen, denominator),
        "candidate_summary": candidate_summary,
        "needed_repairs": needed,
        "available_missed_repairs": len(missed),
        "chosen_repairs": len(chosen),
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
        "source_counts": source_counts(candidate),
        "candidate_rows": [compact(row) for row in candidate],
        "danger_rows": [compact(row) for row in danger],
        "repair_rows": [compact(row) for row in chosen],
    }


def promotion_blockers(summary: dict[str, Any], integrity: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents"))
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net is None or net <= 0.0:
        blockers.append("net_not_positive")
    blockers.extend(str(item) for item in integrity.get("integrity_preview_blockers") or [])
    return blockers


def evaluate_window(label: str, freeze_ts: str) -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = surface_for_freeze(freeze_ts)
    variants: list[dict[str, Any]] = []
    for danger_name, danger_fn in DANGER_RULES.items():
        for suffix, require_hybrid_edge, repair_mode in REPAIR_MODES:
            row = build_stack_candidate(
                all_rows,
                target,
                denominator,
                forward_markets,
                f"{danger_name}_{suffix}",
                danger_fn,
                require_hybrid_edge,
                repair_mode,
            )
            summary = row.get("candidate_summary") or {}
            integrity = source_quality(row.get("source_counts") or {}, as_float(summary.get("net_cents")))
            row["integrity_preview"] = integrity
            row["promotion_blockers"] = promotion_blockers(summary, integrity)
            variants.append(row)
    variants.sort(
        key=lambda row: (
            len(row.get("promotion_blockers") or []),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
            -float(row.get("delta_vs_target_cents") or -999999.0),
        )
    )
    baseline = evaluate_hybrid_veto_window(label, freeze_ts)
    return {
        "window": label,
        "freeze_ts": freeze_ts,
        "forward_denominator": denominator,
        "target_summary": baseline.get("target_summary"),
        "hybrid_veto_summary": baseline.get("hybrid_veto_summary"),
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    target_state = load_json(TARGET_STATE_JSON)
    diagnostic_freeze = target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts")
    windows = []
    if diagnostic_freeze:
        windows.append(evaluate_window("diagnostic_existing_target_window", str(diagnostic_freeze)))
    windows.append(evaluate_window("post_stack_freeze_window", str(state["freeze_ts_utc"])))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": state,
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Research-only: this writes scorecards only and does not change live entries.",
        "Promotion requires post-freeze rows, positive net, 75-90% coverage, source-quality proof, and full-loss cushion.",
    ]
    for window in windows:
        best = (window.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{window.get('window')}: best {best.get('candidate')} has "
            f"{summary.get('settled')} settled, coverage {summary.get('coverage_pct')}%, "
            f"net {summary.get('net_cents')}c, blockers {best.get('promotion_blockers')}."
        )
    return notes


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Hybrid/Boundary Entry Stack",
        "",
        "Research-only: combined hybrid-veto, boundary-clock, and early-NO repair scorecard.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stack freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Coverage floor: `{state.get('coverage_floor')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(
            [
                "",
                f"## {window.get('window')}",
                "",
                f"- Freeze UTC: `{window.get('freeze_ts')}`",
                f"- Forward denominator: `{window.get('forward_denominator')}`",
                "",
                "| rank | candidate | repairs | coverage | net c | delta c | W/L | recon share | loss cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(window.get("variants") or [], start=1):
            summary = row.get("candidate_summary") or {}
            integrity = row.get("integrity_preview") or {}
            lines.append(
                f"| {idx} | {row.get('candidate')} | {row.get('chosen_repairs')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{fmt(row.get('delta_vs_target_cents'))} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{fmt(integrity.get('reconstructed_share'))} | {fmt(integrity.get('full_loss_cushion_estimate'))} | "
                f"{', '.join(row.get('promotion_blockers') or []) or 'none'} |"
            )
        best = (window.get("variants") or [{}])[0]
        lines.extend(
            [
                "",
                "### Best Candidate Repairs",
                "",
                "| market | source | side | won | net c | raw p | hybrid p | ask | raw edge | hybrid edge | recross | abs d | score |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in best.get("repair_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_raw'))} | {fmt(row.get('p_hybrid'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('hybrid_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('repair_score'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
