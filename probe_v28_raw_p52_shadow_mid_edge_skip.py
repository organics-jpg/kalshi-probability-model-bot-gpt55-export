"""Raw p52 shadow-expansion mid-edge skip diagnostic.

Research-only; no live bot changes or orders.

This preserves actual v28-approved rows and only skips rejected-actionable
expansion rows in the 5-10pp edge band.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_p52_mid_edge_skip import BASE_POLICY, edge_prob, summarize
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_shadow_mid_edge_skip_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_shadow_mid_edge_skip_latest.md"


def should_skip(row: dict[str, Any]) -> bool:
    edge = edge_prob(row)
    return (
        row.get("source") == "rejected_actionable"
        and edge is not None
        and 0.05 <= edge < 0.10
    )


def build_report() -> dict[str, Any]:
    source = build_raw_report()
    watched = int(source.get("watched_markets") or 0)
    base = [row for row in source.get("rows") or [] if row.get("policy") == BASE_POLICY]
    kept = [row for row in base if not should_skip(row)]
    skipped = [row for row in base if should_skip(row)]
    base_s = summarize(base, watched)
    kept_s = summarize(kept, watched)
    skip_s = summarize(skipped, watched)
    return {
        "base_policy": BASE_POLICY,
        "candidate": "raw_p52_skip_rejected_mid_edge_5_10pp",
        "rule": "Start from v28_raw_p52_edge0; preserve approved_entry rows; skip rejected_actionable rows with edge in [5pp, 10pp).",
        "physics": "The live-approved core may encode execution/state context; the broad expansion surface is where middle-edge false conviction should be penalized first.",
        "watched_markets": watched,
        "base": base_s,
        "candidate_summary": kept_s,
        "skipped_summary": skip_s,
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
        "# v28 Raw p52 Shadow Mid-Edge Skip",
        "",
        "Discovery diagnostic only. The rule is frozen separately before forward validation.",
        "",
        f"- Base policy: `{report.get('base_policy')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Rule: `{report.get('rule')}`",
        f"- Watched markets: `{report.get('watched_markets')}`",
        f"- Delta vs base: `{fmt(report.get('delta_net_cents'))}c`",
        "",
        "## Summary",
        "",
        "| row | entries | settled | W/L | coverage | win rate | avg edge | net c | actual/sim |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["base", "candidate_summary", "skipped_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_edge'))} | "
            f"{fmt(row.get('net_cents'))} | {row.get('actual_count')}/{row.get('sim_count')} |"
        )
    lines.extend(["", "## Skipped Rows", "", "| market | side | source | p | ask | edge | won | net c |", "|---|---|---|---:|---:|---:|---|---:|"])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(row.get('p_eff'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(edge_prob(row))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_gross_cents_after_entry_fee') or row.get('gross_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
