"""Feasibility bounds for feature-gate coverage vs source-quality gates.

Research-only; no live bot changes or orders.

This does not propose a trading rule. It answers a narrower audit question:
given the current post-freeze observation pool, is it mathematically possible
to reach target market coverage while keeping reconstructed/rejected rows at or
below the promotion source-quality limit?
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state, market, source
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_feasibility_bound_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_feasibility_bound_latest.md"

COVERAGE_TARGETS = [0.75, 0.80, 0.90]
MAX_RECON_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_bucket(row: dict[str, Any]) -> str:
    return "approved" if source(row) == "approved_entry" else "reconstructed_or_rejected"


def market_source_sets(rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for row in rows:
        ticker = market(row)
        if not ticker:
            continue
        out.setdefault(ticker, set()).add(source_bucket(row))
    return out


def feasibility_for_target(denominator: int, approved_markets: int, recon_markets: int, target: float) -> dict[str, Any]:
    required = int(math.ceil(float(denominator) * target))
    min_recon_needed = max(0, required - approved_markets)
    feasible_supply = min_recon_needed <= recon_markets
    min_share = (min_recon_needed / required) if required > 0 else None
    source_gate_feasible = bool(feasible_supply and min_share is not None and min_share <= MAX_RECON_SHARE)
    max_recon_under_gate = int(math.floor((MAX_RECON_SHARE / (1.0 - MAX_RECON_SHARE)) * approved_markets))
    max_source_clean_selected = min(denominator, approved_markets + min(recon_markets, max_recon_under_gate))
    max_source_clean_coverage = (100.0 * max_source_clean_selected / denominator) if denominator > 0 else None
    return {
        "target_coverage_pct": target * 100.0,
        "required_markets": required,
        "approved_markets_available": approved_markets,
        "reconstructed_markets_available": recon_markets,
        "min_reconstructed_needed": min_recon_needed,
        "min_reconstructed_share_needed": min_share,
        "source_gate_feasible": source_gate_feasible,
        "max_reconstructed_under_35pct_gate": max_recon_under_gate,
        "max_source_clean_selected_markets": max_source_clean_selected,
        "max_source_clean_coverage_pct": max_source_clean_coverage,
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    denominator_int = int(denominator or 0)
    by_market = market_source_sets(rows)
    approved_markets = sum(1 for sources in by_market.values() if "approved" in sources)
    recon_markets = sum(1 for sources in by_market.values() if "reconstructed_or_rejected" in sources)
    both_sources = sum(1 for sources in by_market.values() if len(sources) > 1)
    target_bounds = [
        feasibility_for_target(denominator_int, approved_markets, recon_markets, target)
        for target in COVERAGE_TARGETS
    ]
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator_int,
        "observed_markets_with_rows": len(by_market),
        "approved_markets_available": approved_markets,
        "reconstructed_markets_available": recon_markets,
        "markets_with_both_sources": both_sources,
        "approved_only_markets": sum(1 for sources in by_market.values() if sources == {"approved"}),
        "reconstructed_only_markets": sum(
            1 for sources in by_market.values() if sources == {"reconstructed_or_rejected"}
        ),
        "target_bounds": target_bounds,
        "source_quality_target_coverage_feasible": any(
            bound["target_coverage_pct"] == 75.0 and bound["source_gate_feasible"]
            for bound in target_bounds
        ),
        "market_sources": {ticker: sorted(sources) for ticker, sources in sorted(by_market.items())},
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "max_reconstructed_share": MAX_RECON_SHARE,
        "purpose": "Audit whether current observation supply can satisfy coverage and source-quality gates together.",
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Source labels are audit-only; this probe does not select trades.",
    ]
    for lane in lanes:
        bound_75 = next((row for row in lane.get("target_bounds") or [] if row.get("target_coverage_pct") == 75.0), {})
        feasible = bound_75.get("source_gate_feasible")
        max_clean = bound_75.get("max_source_clean_coverage_pct")
        notes.append(
            f"{lane.get('lane')}: denominator {lane.get('future_denominator')}, approved markets {lane.get('approved_markets_available')}, "
            f"reconstructed markets {lane.get('reconstructed_markets_available')}; 75% coverage source gate feasible={feasible}, "
            f"minimum reconstructed share needed {bound_75.get('min_reconstructed_share_needed')}, max <=35% source-clean coverage {max_clean}%."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Source Feasibility Bound",
        "",
        "Research-only audit. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Max reconstructed/rejected share gate: `{report.get('max_reconstructed_share')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Denominator: `{lane.get('future_denominator')}`",
            f"- Approved markets available: `{lane.get('approved_markets_available')}`",
            f"- Reconstructed/rejected markets available: `{lane.get('reconstructed_markets_available')}`",
            f"- Markets with both source types: `{lane.get('markets_with_both_sources')}`",
            "",
            "| target coverage | required markets | min recon needed | min recon share | feasible under <=35% | max source-clean coverage |",
            "|---:|---:|---:|---:|---|---:|",
        ])
        for bound in lane.get("target_bounds") or []:
            lines.append(
                f"| {fmt(bound.get('target_coverage_pct'))}% | {bound.get('required_markets')} | "
                f"{bound.get('min_reconstructed_needed')} | {fmt(bound.get('min_reconstructed_share_needed'))} | "
                f"{bound.get('source_gate_feasible')} | {fmt(bound.get('max_source_clean_coverage_pct'))}% |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
