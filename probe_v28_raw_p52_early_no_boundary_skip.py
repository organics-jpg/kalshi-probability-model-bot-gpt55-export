"""Raw p52 early-NO boundary-decay skip diagnostic.

Research-only; no live bot changes or orders.

Physics hypothesis:
    Early NO positions near the strike are path-fragile. When there is still
    plenty of clock and recross hazard is high, NO can look statistically
    favored while still being exposed to repeated BTC boundary churn.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_early_no_boundary_skip_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_early_no_boundary_skip_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def probability(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_eff") if row.get("p_eff") is not None else row.get("p_side"))


def is_early_no_boundary_decay(row: dict[str, Any]) -> bool:
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
        and stc >= 720.0
        and p < 0.70
        and abs_d <= 0.45
        and recross >= 0.55
    )


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(
        float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0)
        for row in rows
        if settled(row)
    )


def summarize(rows: list[dict[str, Any]], watched: int) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    wins = sum(1 for row in settled_rows if row.get("side_won") is True)
    losses = sum(1 for row in settled_rows if row.get("side_won") is False)
    return {
        "entries": len(rows),
        "settled": len(settled_rows),
        "wins": wins,
        "losses": losses,
        "coverage_pct": 100.0 * len(rows) / watched if watched else None,
        "net_cents": net_cents(rows),
        "avg_p": avg(probability(row) for row in settled_rows),
        "avg_ask": avg(row.get("ask_prob") for row in settled_rows),
        "avg_abs_d": avg(row.get("abs_d_sigma") for row in settled_rows),
        "avg_recross": avg(row.get("recross_hazard_score") for row in settled_rows),
        "win_rate": wins / len(settled_rows) if settled_rows else None,
        "actual_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "sim_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    source = build_raw_report()
    watched = int(source.get("watched_markets") or 0)
    base = [row for row in source.get("rows") or [] if row.get("policy") == BASE_POLICY]
    kept = [row for row in base if not is_early_no_boundary_decay(row)]
    skipped = [row for row in base if is_early_no_boundary_decay(row)]
    base_s = summarize(base, watched)
    kept_s = summarize(kept, watched)
    skipped_s = summarize(skipped, watched)
    return {
        "base_policy": BASE_POLICY,
        "candidate": "raw_p52_skip_early_no_boundary_decay",
        "rule": "Start from v28_raw_p52_edge0 and skip NO rows with stc>=720, p<0.70, abs_d<=0.45, recross>=0.55.",
        "physics": "Early NO near-boundary trades are exposed to BTC path churn; apparent NO edge may decay before close.",
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
        "# v28 Raw p52 Early-NO Boundary Skip",
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
