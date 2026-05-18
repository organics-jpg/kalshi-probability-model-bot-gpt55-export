"""Source-quality frontier for the v28 hybrid/boundary entry stack.

Research-only; no live bot changes or orders.

The best stack variants are profitable and broad but still too reconstructed.
This probe asks an upper-bound question: if we are allowed to replace weak
non-danger kept rows too, is there any broad 75% candidate that can stay under
the 35% reconstructed-share gate while preserving positive PnL?
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float, summarize
from probe_v28_hybrid_boundary_entry_stack import (
    DANGER_RULES,
    MAX_RECONSTRUCTED_SHARE,
    compact,
    hybrid_or_early,
    load_json,
    source_quality,
)
from probe_v28_target_coverage_fv_overlay_validator import STATE_JSON as TARGET_STATE_JSON
from probe_v28_target_hybrid_veto_repair import (
    ask_prob,
    hybrid_edge_value,
    hybrid_repair_score,
    is_hybrid_clean_repair,
    raw_edge_value,
    repair_rows_by_market,
    source_counts,
    surface_for_freeze,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_state.json"
OUT_JSON = OUT_DIR / "v28_hybrid_boundary_source_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_hybrid_boundary_source_frontier_latest.md"

MIN_SETTLED = 30
TARGET_COVERAGE_MAX = 90.0


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def row_net(row: dict[str, Any]) -> float:
    return float(row.get("net_gross_cents_after_entry_fee") or 0.0)


def is_reconstructed(row: dict[str, Any]) -> bool:
    return source(row) != "approved_entry"


def row_score(row: dict[str, Any], score_mode: str) -> float:
    net = row_net(row)
    if score_mode == "realized_oracle":
        return net
    if score_mode == "approved_first_hybrid":
        return (1000.0 if source(row) == "approved_entry" else 0.0) + hybrid_repair_score(row)
    if score_mode == "approved_first_raw_edge":
        edge = raw_edge_value(row)
        return (1000.0 if source(row) == "approved_entry" else 0.0) + (edge if edge is not None else -9.0)
    return hybrid_repair_score(row)


def enrich(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **row,
        "raw_edge_prob": raw_edge_value(row),
        "hybrid_edge_prob": hybrid_edge_value(row),
        "repair_score": hybrid_repair_score(row),
        "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
    }


def eligible_rows(
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    danger_fn: Callable[[dict[str, Any]], bool],
    require_hybrid_edge: bool,
) -> list[dict[str, Any]]:
    target_markets = {market(row) for row in target}
    danger_markets = {market(row) for row in target if danger_fn(row)}
    kept_candidates = [
        enrich(row)
        for row in target
        if market(row) not in danger_markets and ask_prob(row) is not None
    ]
    repair_candidates = repair_rows_by_market(
        all_rows,
        {market(row) for row in all_rows if market(row)} - target_markets,
        require_hybrid_edge,
    )
    fallback_candidates = repair_rows_by_market(
        all_rows,
        {market(row) for row in all_rows if market(row)} - {market(row) for row in kept_candidates},
        require_hybrid_edge,
    )
    rows_by_market: dict[str, list[dict[str, Any]]] = {}
    for row in kept_candidates + repair_candidates + fallback_candidates:
        if require_hybrid_edge and not is_hybrid_clean_repair(row, True):
            continue
        if ask_prob(row) is None:
            continue
        rows_by_market.setdefault(market(row), []).append(enrich(row))
    return [row for rows in rows_by_market.values() for row in rows]


def choose_frontier(
    rows: list[dict[str, Any]],
    denominator: int,
    score_mode: str,
    cap_reconstructed: bool,
) -> list[dict[str, Any]]:
    needed = int((COVERAGE_FLOOR * denominator + 99.999999) // 100)
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_market.setdefault(market(row), []).append(row)
    per_market = [
        sorted(items, key=lambda row: row_score(row, score_mode), reverse=True)[0]
        for items in by_market.values()
    ]
    approved = sorted([row for row in per_market if not is_reconstructed(row)], key=lambda row: row_score(row, score_mode), reverse=True)
    reconstructed = sorted([row for row in per_market if is_reconstructed(row)], key=lambda row: row_score(row, score_mode), reverse=True)
    chosen: list[dict[str, Any]] = []
    max_recon = int(needed * MAX_RECONSTRUCTED_SHARE)
    chosen.extend(approved[:needed])
    if len(chosen) < needed:
        allowed = needed - len(chosen)
        if cap_reconstructed:
            allowed = min(allowed, max_recon)
        chosen.extend(reconstructed[:allowed])
    if len(chosen) > needed:
        chosen = sorted(chosen, key=lambda row: row_score(row, score_mode), reverse=True)[:needed]
    return chosen


def blockers(summary: dict[str, Any], integrity: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        out.append("coverage_too_high")
    if net is None or net <= 0:
        out.append("net_not_positive")
    recon = as_float(integrity.get("reconstructed_share"))
    if recon is not None and recon > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    return out


def evaluate_window(label: str, freeze_ts: str) -> dict[str, Any]:
    all_rows, target, denominator, _ = surface_for_freeze(freeze_ts)
    variants = []
    for danger_name, danger_fn in DANGER_RULES.items():
        for require_hybrid_edge in (True, False):
            candidates = eligible_rows(all_rows, target, danger_fn, require_hybrid_edge)
            for score_mode in ("approved_first_hybrid", "approved_first_raw_edge", "hybrid_score", "realized_oracle"):
                for cap in (True, False):
                    chosen = choose_frontier(candidates, denominator, score_mode, cap)
                    summary = summarize(chosen, denominator)
                    integrity = source_quality(source_counts(chosen), as_float(summary.get("net_cents")))
                    name = f"{danger_name}_{'hybrid_edge' if require_hybrid_edge else 'raw_clean'}_{score_mode}_{'cap35' if cap else 'uncapped'}"
                    variants.append(
                        {
                            "candidate": name,
                            "danger_rule": danger_name,
                            "require_hybrid_edge": require_hybrid_edge,
                            "score_mode": score_mode,
                            "cap_reconstructed": cap,
                            "candidate_summary": summary,
                            "source_counts": source_counts(chosen),
                            "integrity_preview": integrity,
                            "blockers": blockers(summary, integrity),
                            "rows": [compact(row) for row in chosen],
                        }
                    )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
            float((row.get("integrity_preview") or {}).get("reconstructed_share") or 1.0),
        )
    )
    return {
        "window": label,
        "freeze_ts": freeze_ts,
        "forward_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    stack_state = load_json(STATE_JSON)
    target_state = load_json(TARGET_STATE_JSON)
    diagnostic_freeze = target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts")
    windows = []
    if diagnostic_freeze:
        windows.append(evaluate_window("diagnostic_existing_target_window", str(diagnostic_freeze)))
    if stack_state.get("freeze_ts_utc"):
        windows.append(evaluate_window("post_stack_freeze_window", str(stack_state["freeze_ts_utc"])))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Upper-bound source-quality frontier for the hybrid/boundary stack.",
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = []
    for window in windows:
        best = (window.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        integrity = best.get("integrity_preview") or {}
        notes.append(
            f"{window.get('window')}: best frontier {best.get('candidate')} settled {summary.get('settled')}, coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, reconstructed {integrity.get('reconstructed_share')}, blockers {best.get('blockers')}."
        )
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
        "# v28 Hybrid/Boundary Source Frontier",
        "",
        "Research-only; upper-bound source-quality diagnostic.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(["", f"## {window.get('window')}", ""])
        lines.append(f"- Forward denominator: `{window.get('forward_denominator')}`")
        lines.extend(["", "| rank | candidate | settled | coverage | net c | W/L | recon share | blockers |", "|---:|---|---:|---:|---:|---:|---:|---|"])
        for idx, row in enumerate((window.get("variants") or [])[:20], start=1):
            summary = row.get("candidate_summary") or {}
            integrity = row.get("integrity_preview") or {}
            lines.append(
                f"| {idx} | {row.get('candidate')} | {summary.get('settled')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(integrity.get('reconstructed_share'))} | "
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
