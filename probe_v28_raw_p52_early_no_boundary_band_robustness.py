"""Robustness audit for raw p52 middle-confidence early-NO boundary skip.

Research-only; no live bot changes or orders.

This is an anti-overfit check for the discovery rule. It does not promote the
candidate; it checks whether nearby threshold variants tell the same physical
story and whether the discovery lift depends on one skipped market.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_p52_early_no_boundary_skip import as_float, probability, summarize
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_band_robustness_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_early_no_boundary_band_robustness_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"
CANONICAL = {
    "name": "p62_70_rec55_abs45",
    "p_min": 0.62,
    "p_max": 0.70,
    "recross_min": 0.55,
    "abs_d_max": 0.45,
    "stc_min": 720.0,
}


def net(row: dict[str, Any]) -> float:
    return float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0)


def is_skip(row: dict[str, Any], spec: dict[str, Any]) -> bool:
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
        and float(spec["p_min"]) <= p < float(spec["p_max"])
        and stc >= float(spec["stc_min"])
        and abs_d <= float(spec["abs_d_max"])
        and recross >= float(spec["recross_min"])
    )


def evaluate(base: list[dict[str, Any]], watched: int, spec: dict[str, Any]) -> dict[str, Any]:
    kept = [row for row in base if not is_skip(row, spec)]
    skipped = [row for row in base if is_skip(row, spec)]
    kept_s = summarize(kept, watched)
    skipped_s = summarize(skipped, watched)
    base_s = summarize(base, watched)
    return {
        **spec,
        "candidate_summary": kept_s,
        "skipped_summary": skipped_s,
        "delta_net_cents": kept_s["net_cents"] - base_s["net_cents"],
    }


def specs() -> list[dict[str, Any]]:
    out = []
    for p_min, p_max in [(0.58, 0.68), (0.60, 0.68), (0.60, 0.70), (0.62, 0.68), (0.62, 0.70), (0.64, 0.70), (0.66, 0.70)]:
        for recross_min in [0.55, 0.65, 0.75]:
            for abs_d_max in [0.35, 0.45]:
                out.append({
                    "name": f"p{int(p_min*100)}_{int(p_max*100)}_rec{int(recross_min*100)}_abs{int(abs_d_max*100)}",
                    "p_min": p_min,
                    "p_max": p_max,
                    "recross_min": recross_min,
                    "abs_d_max": abs_d_max,
                    "stc_min": 720.0,
                })
    return out


def leave_one_skipped(base: list[dict[str, Any]], watched: int, spec: dict[str, Any]) -> list[dict[str, Any]]:
    skipped = [row for row in base if is_skip(row, spec)]
    base_s = summarize(base, watched)
    out = []
    for remove in skipped:
        kept_with_one_returned = [row for row in base if not is_skip(row, spec) or row is remove]
        s = summarize(kept_with_one_returned, watched)
        out.append({
            "returned_market": remove.get("market"),
            "returned_net_cents": net(remove),
            "candidate_net_with_returned_market": s.get("net_cents"),
            "delta_vs_base_with_returned_market": float(s.get("net_cents") or 0.0) - float(base_s.get("net_cents") or 0.0),
        })
    out.sort(key=lambda row: float(row["delta_vs_base_with_returned_market"]))
    return out


def build_report() -> dict[str, Any]:
    source = build_raw_report()
    watched = int(source.get("watched_markets") or 0)
    base = [row for row in source.get("rows") or [] if row.get("policy") == BASE_POLICY]
    base_s = summarize(base, watched)
    evaluated = [evaluate(base, watched, spec) for spec in specs()]
    target_rows = [
        row for row in evaluated
        if 75.0 <= float((row.get("candidate_summary") or {}).get("coverage_pct") or 0.0) <= 90.0
    ]
    target_rows.sort(
        key=lambda row: (
            float(row.get("delta_net_cents") or -999999.0),
            float((row.get("candidate_summary") or {}).get("coverage_pct") or 0.0),
        ),
        reverse=True,
    )
    canonical = evaluate(base, watched, CANONICAL)
    leave_one = leave_one_skipped(base, watched, CANONICAL)
    pass_basic = (
        float(canonical.get("delta_net_cents") or 0.0) > 0.0
        and bool(leave_one)
        and float(leave_one[0]["delta_vs_base_with_returned_market"]) > 0.0
        and len([row for row in target_rows[:10] if float(row.get("delta_net_cents") or 0.0) > 0.0]) >= 7
    )
    return {
        "base_policy": BASE_POLICY,
        "base": base_s,
        "canonical": canonical,
        "top_target_coverage_variants": target_rows[:20],
        "leave_one_skipped": leave_one,
        "passes_basic_robustness": pass_basic,
        "interpretation": interpretation(canonical, target_rows, leave_one, pass_basic),
    }


def interpretation(
    canonical: dict[str, Any],
    target_rows: list[dict[str, Any]],
    leave_one: list[dict[str, Any]],
    pass_basic: bool,
) -> list[str]:
    cand = canonical.get("candidate_summary") or {}
    skipped = canonical.get("skipped_summary") or {}
    notes = [
        f"Canonical rule coverage/net is {cand.get('coverage_pct')}%/{cand.get('net_cents')}c with skipped bucket {skipped.get('wins')}/{skipped.get('losses')} for {skipped.get('net_cents')}c.",
        f"Top target-coverage threshold variants with positive delta among top 10: {sum(1 for row in target_rows[:10] if float(row.get('delta_net_cents') or 0.0) > 0.0)}/10.",
        f"Basic robustness pass is {pass_basic}; this is still discovery-only until frozen forward rows settle.",
    ]
    if leave_one:
        worst = leave_one[0]
        notes.append(
            f"Worst leave-one-skipped delta is {worst.get('delta_vs_base_with_returned_market')}c if {worst.get('returned_market')} is put back."
        )
    return notes


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
        "# v28 Raw p52 Early-NO Boundary Band Robustness",
        "",
        "Discovery-only robustness audit. No live orders.",
        "",
        f"- Passes basic robustness: `{report.get('passes_basic_robustness')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Top Target-Coverage Variants",
        "",
        "| rank | variant | coverage | net c | delta c | settled | W/L | skipped W/L | skipped net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("top_target_coverage_variants") or [], start=1):
        cand = row.get("candidate_summary") or {}
        skip = row.get("skipped_summary") or {}
        lines.append(
            f"| {idx} | {row.get('name')} | {fmt(cand.get('coverage_pct'))} | {fmt(cand.get('net_cents'))} | "
            f"{fmt(row.get('delta_net_cents'))} | {cand.get('settled')} | {cand.get('wins')}/{cand.get('losses')} | "
            f"{skip.get('wins')}/{skip.get('losses')} | {fmt(skip.get('net_cents'))} |"
        )
    lines.extend([
        "",
        "## Leave-One Skipped Stress",
        "",
        "| returned market | returned net c | candidate net if returned | delta vs base if returned |",
        "|---|---:|---:|---:|",
    ])
    for row in report.get("leave_one_skipped") or []:
        lines.append(
            f"| {row.get('returned_market')} | {fmt(row.get('returned_net_cents'))} | "
            f"{fmt(row.get('candidate_net_with_returned_market'))} | {fmt(row.get('delta_vs_base_with_returned_market'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
