"""Confirmed dual-clock coverage-fill portfolio for feature-gate branch.

Research-only; no live bot changes or orders.

This combines three observable ideas that each repair a different gate:

1. same-market source confirmation replacement lowers source share;
2. dual-clock delayed recheck repairs clipped winners and false collapses;
3. highest-quality omitted-market filler restores minimum broad coverage.

The parent evidence is diagnostic. The portfolio has its own freeze timestamp;
only post-birth rows can count as strict evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state as load_feature_gate_state
from probe_v28_boundary_clock_feature_gate_candidate import market, net, source
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule
from probe_v28_feature_gate_coverage_size_shrink import ANCHOR_RULE, REPAIR_RULE, repair_weight, row_key, selected
from probe_v28_feature_gate_dual_clock_recheck_rescue import (
    BOOK_GAP_JSON,
    LIVE_SUMMARY_JSON,
    REDUCE_JSON,
    VARIANTS,
    evaluate_variant,
    grouped_exit_rows,
    load_json,
    read_heartbeats,
)
from probe_v28_feature_gate_source_confirmation_replacement import (
    confirmation_rank,
    strong_confirmation,
    weak_selected,
)
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_latest.md"
STATE_JSON = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_state.json"

POLICY = "repair_low_absd_quarter_else_half"
TARGET_COVERAGE = 0.75


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    existing = load_json(STATE_JSON)
    if existing:
        return existing
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_confirmed_dual_clock_fill",
        "parent_policy": POLICY,
        "note": "Freeze created after diagnostic source-confirmation + dual-clock + coverage-fill composition; post-birth rows are the only strict-forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fval(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key) if row.get(key) is not None else default)
    except (TypeError, ValueError):
        return default


def filler_pool_rule(row: dict[str, Any]) -> bool:
    return (
        fval(row, "p_side") >= 0.75
        and fval(row, "abs_d_sigma") >= 0.30
        and fval(row, "ask_prob") >= 0.20
        and fval(row, "recross_hazard_score", 1.0) <= 0.70
    )


def filler_rank(row: dict[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        fval(row, "p_side"),
        fval(row, "abs_d_sigma"),
        fval(row, "ask_prob"),
        -fval(row, "recross_hazard_score", 1.0),
        str(row.get("ts_wall") or ""),
    )


def row_view(row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> dict[str, Any]:
    weight = repair_weight(POLICY, row, anchor_keys)
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "weight": weight,
        "weighted_net_cents": weight * net(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "raw_edge": row.get("raw_edge"),
        "reason": row.get("reason"),
    }


def build_entries(freeze_ts: str) -> tuple[list[dict[str, Any]], set[tuple[str, str]], int, list[dict[str, Any]], list[dict[str, Any]]]:
    rows, _, denominator_raw = entry_surfaces(freeze_ts)
    denominator = int(denominator_raw or 0)
    anchor_rows = selected(rows, ANCHOR_RULE)
    base_rows = selected(rows, REPAIR_RULE)
    anchor_keys = {row_key(row) for row in anchor_rows}
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row) and passes_rule(row, REPAIR_RULE):
            by_market[market(row)].append(row)
    confirmed = []
    replacements = []
    for row in base_rows:
        alternatives = [
            alt for alt in by_market.get(market(row), [])
            if row_key(alt) == row_key(row) and strong_confirmation(alt)
        ]
        if weak_selected(row) and alternatives:
            replacement = max(alternatives, key=confirmation_rank)
            confirmed.append(replacement)
            replacements.append({"old": row_view(row, anchor_keys), "new": row_view(replacement, anchor_keys)})
        else:
            confirmed.append(row)

    selected_markets = {market(row) for row in confirmed}
    required = int((denominator * TARGET_COVERAGE) + 0.999999)
    fillers_needed = max(0, required - len(confirmed))
    candidates_by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row) not in selected_markets and filler_pool_rule(row):
            candidates_by_market[market(row)].append(row)
    filler_candidates = [max(items, key=filler_rank) for items in candidates_by_market.values()]
    filler_candidates.sort(key=filler_rank, reverse=True)
    fillers = filler_candidates[:fillers_needed]
    return confirmed + fillers, anchor_keys, denominator, replacements, [row_view(row, anchor_keys) for row in fillers]


def evaluate_lane(label: str, strict_forward: bool, freeze_ts: str) -> dict[str, Any]:
    entries, anchor_keys, denominator, replacements, fillers = build_entries(freeze_ts)
    book_rows = grouped_exit_rows(BOOK_GAP_JSON)
    reduce_rows = grouped_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    live_cents = 100.0 * float(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars") or 0.0)
    variants = [
        evaluate_variant(variant, entries, anchor_keys, denominator, book_rows, reduce_rows, heartbeats, live_cents, label, strict_forward)
        for variant in VARIANTS
    ]
    for row in variants:
        row["blockers"] = list(row.get("blockers") or [])
        if not strict_forward:
            row["blockers"].append("confirmed_dual_clock_fill_diagnostic")
        else:
            row["blockers"].append("post_birth_watch")
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("candidate_net_cents") or -999999.0),
            -float(row.get("delta_vs_current_exit_cents") or -999999.0),
        )
    )
    counts = Counter(source(row) for row in entries)
    return {
        "lane": label,
        "strict_forward": strict_forward,
        "freeze_ts_utc": freeze_ts,
        "denominator": denominator,
        "entry_rows": len(entries),
        "source_counts": dict(counts),
        "reconstructed_share": (len(entries) - int(counts.get("approved_entry") or 0)) / len(entries) if entries else None,
        "replacements": replacements,
        "fillers": fillers,
        "variants": variants,
        "best": variants[0] if variants else {},
    }


def build_report() -> dict[str, Any]:
    feature_state = load_feature_gate_state()
    state = load_or_create_state()
    diagnostic = evaluate_lane("diagnostic_prefreeze_context", False, str(feature_state["freeze_ts_utc"]))
    post = evaluate_lane("post_confirmed_dual_clock_fill_birth", True, str(state["freeze_ts_utc"]))
    best = diagnostic.get("best") or {}
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_state.get("freeze_ts_utc"),
        "state": state,
        "policy": POLICY,
        "lanes": [diagnostic, post],
        "variants": diagnostic.get("variants") or [],
        "interpretation": [
            "Research-only confirmed dual-clock coverage-fill portfolio; no live bot changes or orders.",
            (
                f"Diagnostic best {((best.get('variant') or {}).get('name'))} has net {best.get('candidate_net_cents')}c, "
                f"delta vs live {best.get('delta_vs_live_cents')}c, W/L {best.get('wins')}/{best.get('losses')}, "
                f"coverage {best.get('coverage_pct')}%, source {best.get('reconstructed_share')}, blockers {best.get('blockers')}."
            ) if best else "No diagnostic variants scored.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Confirmed Dual-Clock Fill",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Portfolio freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | strict | entries | coverage | source | replacements | fillers | best variant | W/L | net | delta live | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        best = lane.get("best") or {}
        variant = best.get("variant") or {}
        lines.append(
            f"| `{lane.get('lane')}` | {lane.get('strict_forward')} | {lane.get('entry_rows')} | "
            f"{fmt(best.get('coverage_pct'))}% | {fmt(best.get('reconstructed_share'))} | "
            f"{len(lane.get('replacements') or [])} | {len(lane.get('fillers') or [])} | "
            f"`{variant.get('name')}` | {best.get('wins')}/{best.get('losses')} | "
            f"{fmt(best.get('candidate_net_cents'))} | {fmt(best.get('delta_vs_live_cents'))} | "
            f"{', '.join(best.get('blockers') or [])} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')} Fillers",
            "",
            "| market | side | source | net | p_side | abs_d | ask | recross | reason |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ])
        for row in lane.get("fillers") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(row.get('net_cents'))} | "
                f"{fmt(row.get('p_side'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {row.get('reason')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
