"""Raw p52 middle-confidence early-NO boundary skip.

Research-only; no live bot changes or orders.

Physics hypothesis:
    The worst early NO boundary rows are not the cheapest weak-NO rows. They
    are the middle-confidence NO rows where p is high enough to look safe but
    not high enough to dominate BTC recross risk before close.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_p52_early_no_boundary_skip import as_float, probability, summarize
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_skip_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_early_no_boundary_band_skip_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"
P_MIN = 0.62
P_MAX = 0.70
STC_MIN = 720.0
ABS_D_MAX = 0.45
RECROSS_MIN = 0.55


def is_middle_confidence_early_no_boundary(row: dict[str, Any]) -> bool:
    p = probability(row)
    stc = as_float(row.get("seconds_to_close"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    return (
        str(row.get("side") or "").lower() == "no"
        and p is not None
        and stc is not None
        and abs_d is not None
        and recross is not None
        and P_MIN <= p < P_MAX
        and stc >= STC_MIN
        and abs_d <= ABS_D_MAX
        and recross >= RECROSS_MIN
    )


def build_report() -> dict[str, Any]:
    source = build_raw_report()
    watched = int(source.get("watched_markets") or 0)
    base = [row for row in source.get("rows") or [] if row.get("policy") == BASE_POLICY]
    kept = [row for row in base if not is_middle_confidence_early_no_boundary(row)]
    skipped = [row for row in base if is_middle_confidence_early_no_boundary(row)]
    base_s = summarize(base, watched)
    kept_s = summarize(kept, watched)
    skipped_s = summarize(skipped, watched)
    return {
        "base_policy": BASE_POLICY,
        "candidate": "raw_p52_skip_midconf_early_no_boundary",
        "rule": "Start from v28_raw_p52_edge0 and skip NO rows with 0.62<=p<0.70, stc>=720, abs_d<=0.45, recross>=0.55.",
        "physics": "Middle-confidence early NO boundary rows can be overconfident because recross churn remains alive while payout risk is large.",
        "watched_markets": watched,
        "base": base_s,
        "candidate_summary": kept_s,
        "skipped_summary": skipped_s,
        "delta_net_cents": kept_s["net_cents"] - base_s["net_cents"],
        "rows": kept,
        "skipped_rows": skipped,
    }


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Raw p52 Middle-Confidence Early-NO Boundary Skip",
        "",
        "Discovery diagnostic only. Frozen validator fixes this rule before forward validation.",
        "",
        f"- Base policy: `{report.get('base_policy')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Rule: `{report.get('rule')}`",
        f"- Watched markets: `{report.get('watched_markets')}`",
        f"- Delta vs base: `{fmt(report.get('delta_net_cents'))}c`",
        "",
        "## Summary",
        "",
        "| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg abs d | avg recross | net c | actual/sim |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["base", "candidate_summary", "skipped_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('avg_ask'))} | {fmt(row.get('avg_abs_d'))} | {fmt(row.get('avg_recross'))} | "
            f"{fmt(row.get('net_cents'))} | {row.get('actual_count')}/{row.get('sim_count')} |"
        )
    lines.extend(["", "## Skipped Rows", "", "| market | side | source | p | ask | stc | abs d | recross | won | net c |", "|---|---|---|---:|---:|---:|---:|---:|---|---:|"])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(probability(row))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_gross_cents_after_entry_fee') or row.get('gross_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
