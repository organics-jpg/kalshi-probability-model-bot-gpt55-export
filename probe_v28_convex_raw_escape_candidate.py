"""Convex raw-escape candidate for v28 broad FV research.

The first clean frozen market punished the p60/book side and rewarded cheap
raw YES with large model-vs-book edge. This diagnostic tests a constrained
escape hatch: use raw broad when raw p >= 0.50 and edge >= 20pp, otherwise use
the p60 forgetting candidate.

Discovery-only unless separately frozen.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from probe_v28_continuous_scorecard import watched_markets
from probe_v28_rmt_forgetting_entry_bakeoff import build_report as build_entry_bakeoff_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_convex_raw_escape_candidate_latest.json"
OUT_CSV = OUT_DIR / "v28_convex_raw_escape_candidate_latest.csv"
OUT_MD = OUT_DIR / "v28_convex_raw_escape_candidate_latest.md"

RAW_POLICY = "v28_raw_p50_edge0"
WAIT_POLICY = "first_side_raw_later_book_p60_edge0"
RMT_WAIT_POLICY = "rmt_repetition_forget_p60_edge0"
RAW_EDGE_ESCAPE_MIN = 0.20


def rows_by_policy_market(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {RAW_POLICY, WAIT_POLICY, RMT_WAIT_POLICY}
    }


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def choose(wait_policy: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = rows_by_policy_market(rows)
    markets = sorted({market for policy, market in indexed if policy == RAW_POLICY and market})
    selected: list[dict[str, Any]] = []
    for market in markets:
        raw = indexed.get((RAW_POLICY, market))
        wait = indexed.get((wait_policy, market))
        if not raw:
            continue
        raw_edge = as_float(raw.get("eff_edge_prob"))
        raw_p = as_float(raw.get("p_eff"))
        if raw_edge is not None and raw_p is not None and raw_p >= 0.50 and raw_edge >= RAW_EDGE_ESCAPE_MIN:
            selected.append({
                "meta_policy": f"raw_edge20_else_{wait_policy}",
                "selection_reason": "raw_high_convex_edge",
                **raw,
            })
        elif wait:
            selected.append({
                "meta_policy": f"raw_edge20_else_{wait_policy}",
                "selection_reason": "use_wait_policy",
                **wait,
            })
        else:
            selected.append({
                "meta_policy": f"raw_edge20_else_{wait_policy}",
                "selection_reason": "wait_missing_use_raw",
                **raw,
            })
    return selected


def summarize(name: str, rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0) for row in resolved)
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
        if row.get("p_eff") is not None
    ]
    return {
        "policy": name,
        "entries": len(rows),
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": (len(rows) / denominator * 100.0) if denominator else None,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "raw_high_convex_edge": sum(1 for row in rows if row.get("selection_reason") == "raw_high_convex_edge"),
        "use_wait_policy": sum(1 for row in rows if row.get("selection_reason") == "use_wait_policy"),
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    payload = build_entry_bakeoff_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    denominator = len(watched_markets())
    first_side_rows = choose(WAIT_POLICY, rows)
    rmt_rows = choose(RMT_WAIT_POLICY, rows)
    return {
        "watched_markets": denominator,
        "settings": {"raw_edge_escape_min": RAW_EDGE_ESCAPE_MIN},
        "summary": [
            summarize("raw_edge20_else_first_side_p60", first_side_rows, denominator),
            summarize("raw_edge20_else_rmt_p60", rmt_rows, denominator),
        ],
        "rows": first_side_rows + rmt_rows,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = sorted({key for row in rows for key in row.keys()})
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Convex Raw-Escape Candidate",
        "",
        "Use raw broad only when raw edge is >= 20pp; otherwise use p60 forgetting candidate.",
        "",
        f"- Watched markets: `{report['watched_markets']}`",
        f"- Raw edge escape min: `{report['settings']['raw_edge_escape_min']}`",
        "",
        "## Summary",
        "",
        "| policy | entries | settled | wins/losses | coverage | net c | avg net c | brier | raw escape | wait | actual/shadow |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_net_cents_after_entry_fee'])} | "
            f"{fmt(row['avg_brier'])} | {row['raw_high_convex_edge']} | {row['use_wait_policy']} | "
            f"{row['approved_entry_count']}/{row['added_reject_count']} |"
        )
    lines.extend(["", "## Recent Rows", ""])
    lines.append("| meta | market | reason | side | p_eff | ask | edge | won | net c |")
    lines.append("|---|---|---|---|---:|---:|---:|---|---:|")
    for row in report["rows"][-25:]:
        lines.append(
            f"| {row.get('meta_policy')} | {row.get('market')} | {row.get('selection_reason')} | {row.get('side')} | "
            f"{fmt(row.get('p_eff'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('eff_edge_prob'))} | "
            f"{row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(report["rows"])
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
