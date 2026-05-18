"""Side-flip path diagnostic for v28 broad candidates.

This examines markets where the broad raw candidate and the later/book-anchored
candidate select opposite sides. The first clean frozen market is one of these:
cheap raw YES first, later p60/book NO. This report asks how that pattern has
behaved in the available shadow evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_rmt_forgetting_entry_bakeoff import build_report as build_entry_bakeoff_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_side_flip_path_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_side_flip_path_diagnostic_latest.md"

EARLY_POLICY = "v28_raw_p50_edge0"
LATE_POLICIES = [
    "first_side_raw_later_book_p60_edge0",
    "rmt_repetition_forget_p60_edge0",
    "book_ask_prior_p60_edge0",
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_report() -> dict[str, Any]:
    payload = build_entry_bakeoff_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    by_policy_market = {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {EARLY_POLICY, *LATE_POLICIES}
    }
    markets = sorted({market for policy, market in by_policy_market if policy == EARLY_POLICY and market})
    comparisons: list[dict[str, Any]] = []
    for market in markets:
        early = by_policy_market.get((EARLY_POLICY, market))
        if not early:
            continue
        for late_policy in LATE_POLICIES:
            late = by_policy_market.get((late_policy, market))
            if not late:
                comparisons.append({
                    "market": market,
                    "late_policy": late_policy,
                    "status": "late_policy_missed",
                    "early_side": early.get("side"),
                    "early_gross_cents": early.get("gross_cents"),
                    "early_side_won": early.get("side_won"),
                })
                continue
            same_side = early.get("side") == late.get("side")
            comparisons.append({
                "market": market,
                "late_policy": late_policy,
                "status": "same_side" if same_side else "side_flip",
                "early_side": early.get("side"),
                "late_side": late.get("side"),
                "early_p_eff": early.get("p_eff"),
                "late_p_eff": late.get("p_eff"),
                "early_ask": early.get("ask_prob"),
                "late_ask": late.get("ask_prob"),
                "early_edge": early.get("eff_edge_prob"),
                "late_edge": late.get("eff_edge_prob"),
                "early_ts": early.get("ts_wall"),
                "late_ts": late.get("ts_wall"),
                "early_gross_cents": early.get("gross_cents"),
                "late_gross_cents": late.get("gross_cents"),
                "early_net_cents": early.get("net_gross_cents_after_entry_fee"),
                "late_net_cents": late.get("net_gross_cents_after_entry_fee"),
                "early_side_won": early.get("side_won"),
                "late_side_won": late.get("side_won"),
            })
    return {
        "early_policy": EARLY_POLICY,
        "late_policies": LATE_POLICIES,
        "summary": summarize(comparisons),
        "rows": comparisons,
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for late_policy in LATE_POLICIES:
        for status in ["same_side", "side_flip", "late_policy_missed"]:
            bucket = [row for row in rows if row.get("late_policy") == late_policy and row.get("status") == status]
            settled = [row for row in bucket if row.get("early_side_won") is not None]
            early_net = sum(float(row.get("early_net_cents") or row.get("early_gross_cents") or 0.0) for row in settled)
            late_net = sum(float(row.get("late_net_cents") or row.get("late_gross_cents") or 0.0) for row in settled)
            out.append({
                "late_policy": late_policy,
                "status": status,
                "count": len(bucket),
                "settled": len(settled),
                "early_wins": sum(1 for row in settled if row.get("early_side_won") is True),
                "late_wins": sum(1 for row in settled if row.get("late_side_won") is True),
                "early_net_cents": early_net,
                "late_net_cents": late_net,
                "late_minus_early_net_cents": late_net - early_net,
            })
    return out


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Side-Flip Path Diagnostic",
        "",
        f"- Early policy: `{report['early_policy']}`",
        f"- Late policies: `{', '.join(report['late_policies'])}`",
        "",
        "## Summary",
        "",
        "| late policy | status | count | settled | early wins | late wins | early net c | late net c | late - early c |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['late_policy']} | {row['status']} | {row['count']} | {row['settled']} | {row['early_wins']} | "
            f"{row['late_wins']} | {fmt(row['early_net_cents'])} | {fmt(row['late_net_cents'])} | {fmt(row['late_minus_early_net_cents'])} |"
        )
    lines.extend(["", "## Recent Rows", ""])
    lines.append("| market | late policy | status | early side | late side | early edge | late edge | early won | late won | early net | late net |")
    lines.append("|---|---|---|---|---|---:|---:|---|---|---:|---:|")
    for row in report["rows"][-30:]:
        lines.append(
            f"| {row.get('market')} | {row.get('late_policy')} | {row.get('status')} | {row.get('early_side')} | "
            f"{row.get('late_side')} | {fmt(row.get('early_edge'))} | {fmt(row.get('late_edge'))} | "
            f"{row.get('early_side_won')} | {row.get('late_side_won')} | {fmt(row.get('early_net_cents'))} | {fmt(row.get('late_net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
