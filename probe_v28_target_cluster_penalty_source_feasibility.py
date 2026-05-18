"""Source feasibility audit for target cluster-penalty ranking.

Research-only; no live bot changes or orders.

This checks whether the frozen cluster-penalty broad-entry watch can satisfy
the <=35% reconstructed/rejected share gate from the rows that actually exist
in each forward denominator.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, row_net_after_fee, summarize
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable
from probe_v28_target_coverage_cluster_penalty_watch import (
    VARIANTS,
    adjusted_edge,
    clean_forward_rows,
    compact,
    load_json,
    selected_rows,
    target_freeze_ts,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_state.json"
OUT_JSON = OUT_DIR / "v28_target_cluster_penalty_source_feasibility_latest.json"
OUT_MD = OUT_DIR / "v28_target_cluster_penalty_source_feasibility_latest.md"

MAX_RECONSTRUCTED_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def required_entries(denominator: int) -> int:
    if denominator <= 0:
        return 0
    return math.ceil((COVERAGE_FLOOR / 100.0) * denominator)


def is_approved(row: dict[str, Any]) -> bool:
    return str(row.get("source") or "") == "approved_entry"


def tradeable_scored_rows(rows: list[dict[str, Any]], params: dict[str, float]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not base_tradeable(row):
            continue
        score = adjusted_edge(row, params)
        if score is None:
            continue
        out.append({
            **row,
            "adjusted_edge": score,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
        })
    return out


def best_by_market(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market") or "")
        if market:
            grouped.setdefault(market, []).append(row)
    return {
        market: max(items, key=lambda row: float(row.get("adjusted_edge") or -999.0))
        for market, items in grouped.items()
    }


def selected_source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(row.get("source") or "unknown") for row in rows))


def share_from_rows(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    recon = sum(1 for row in rows if not is_approved(row))
    return recon / len(rows)


def feasibility_for_variant(
    label: str,
    freeze_ts: str,
    rows: list[dict[str, Any]],
    denominator: int,
    variant_name: str,
    params: dict[str, float],
) -> dict[str, Any]:
    need = required_entries(denominator)
    scored = tradeable_scored_rows(rows, params)
    best_all = best_by_market(scored)
    approved_rows = [row for row in scored if is_approved(row)]
    best_approved = best_by_market(approved_rows)
    approved_available_markets = set(best_approved)
    selected = selected_rows(rows, denominator, params)
    selected_markets = {str(row.get("market") or "") for row in selected}
    selected_approved = {str(row.get("market") or "") for row in selected if is_approved(row)}
    omitted_approved = sorted(approved_available_markets - selected_approved)
    min_recon_needed = max(0, need - len(approved_available_markets))
    min_recon_share = None if need <= 0 else min_recon_needed / need
    source_gate_feasible = need > 0 and min_recon_share <= MAX_RECONSTRUCTED_SHARE
    approved_preferred_rows = sorted(
        list(best_approved.values()) + [
            row for market, row in best_all.items()
            if market not in approved_available_markets
        ],
        key=lambda row: (is_approved(row), float(row.get("adjusted_edge") or -999.0)),
        reverse=True,
    )[:need]
    return {
        "lane": label,
        "variant": variant_name,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "required_entries_for_75pct_coverage": need,
        "tradeable_markets": len(best_all),
        "approved_available_markets": len(approved_available_markets),
        "reconstructed_available_markets": max(0, len(best_all) - len(approved_available_markets)),
        "selected_entries": len(selected),
        "selected_settled": summarize(selected, denominator).get("settled"),
        "selected_net_cents": summarize(selected, denominator).get("net_cents"),
        "selected_source_counts": selected_source_counts(selected),
        "selected_reconstructed_share": share_from_rows(selected),
        "selected_approved_markets": len(selected_approved),
        "omitted_approved_available_markets": len(omitted_approved),
        "minimum_reconstructed_rows_needed_for_coverage": min_recon_needed,
        "minimum_reconstructed_share_for_75pct_coverage": min_recon_share,
        "source_gate_feasible_at_current_denominator": source_gate_feasible,
        "approved_preferred_summary": summarize(approved_preferred_rows, denominator),
        "approved_preferred_source_counts": selected_source_counts(approved_preferred_rows),
        "approved_preferred_reconstructed_share": share_from_rows(approved_preferred_rows),
        "omitted_approved_examples": [compact(best_approved[market]) for market in omitted_approved[:12]],
    }


def lane_freezes() -> dict[str, str]:
    state = load_json(STATE_JSON)
    return {
        "diagnostic_target_window": target_freeze_ts(),
        "post_cluster_penalty_birth": str(state.get("freeze_ts_utc") or utc_now_iso()),
    }


def build_report() -> dict[str, Any]:
    freezes = lane_freezes()
    lanes = []
    for lane, freeze_ts in freezes.items():
        rows, _target, denominator = clean_forward_rows(freeze_ts)
        variants = [
            feasibility_for_variant(lane, freeze_ts, rows, denominator, name, params)
            for name, params in VARIANTS.items()
        ]
        variants.sort(
            key=lambda row: (
                row.get("source_gate_feasible_at_current_denominator") is not True,
                as_float(row.get("selected_reconstructed_share")) if row.get("selected_reconstructed_share") is not None else 999,
                -float(as_float(row.get("selected_net_cents")) or -999999.0),
            )
        )
        lanes.append({"lane": lane, "freeze_ts_utc": freeze_ts, "variants": variants, "best": variants[0] if variants else {}})
    report = {
        "generated_at_utc": utc_now_iso(),
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This audit checks source feasibility only; it does not change the frozen cluster-penalty rule.",
    ]
    for lane in report.get("lanes") or []:
        best = lane.get("best") or {}
        notes.append(
            f"{lane.get('lane')}: selected reconstructed share {best.get('selected_reconstructed_share')}, "
            f"approved available {best.get('approved_available_markets')}/{best.get('required_entries_for_75pct_coverage')} required entries, "
            f"minimum reconstructed share {best.get('minimum_reconstructed_share_for_75pct_coverage')}, "
            f"source feasible {best.get('source_gate_feasible_at_current_denominator')}."
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
        "# v28 Target Cluster-Penalty Source Feasibility",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            "| variant | required | approved available | selected | selected recon | min recon share | feasible | selected net c | approved-preferred net c |",
            "|---|---:|---:|---:|---:|---:|---|---:|---:|",
        ])
        for row in lane.get("variants") or []:
            preferred = row.get("approved_preferred_summary") or {}
            lines.append(
                f"| `{row.get('variant')}` | {row.get('required_entries_for_75pct_coverage')} | "
                f"{row.get('approved_available_markets')} | {row.get('selected_entries')} | "
                f"{fmt(row.get('selected_reconstructed_share'))} | "
                f"{fmt(row.get('minimum_reconstructed_share_for_75pct_coverage'))} | "
                f"{row.get('source_gate_feasible_at_current_denominator')} | "
                f"{fmt(row.get('selected_net_cents'))} | {fmt(preferred.get('net_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
