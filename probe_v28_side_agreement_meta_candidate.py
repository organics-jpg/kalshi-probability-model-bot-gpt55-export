"""Side-agreement meta candidate for v28 broad FV research.

Discovery idea:
- Raw broad entries look better when later/book-confirmed candidates agree on
  the same side.
- Raw broad entries look dangerous when later/book-confirmed candidates flip
  side; in those cases, waiting for the p60 forgetting candidate may reduce
  damage.

This is shadow-only. The candidate is scored from the frozen entry bakeoff rows.
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
OUT_JSON = OUT_DIR / "v28_side_agreement_meta_candidate_latest.json"
OUT_CSV = OUT_DIR / "v28_side_agreement_meta_candidate_latest.csv"
OUT_MD = OUT_DIR / "v28_side_agreement_meta_candidate_latest.md"

RAW_POLICY = "v28_raw_p50_edge0"
WAIT_POLICY = "first_side_raw_later_book_p60_edge0"
RMT_WAIT_POLICY = "rmt_repetition_forget_p60_edge0"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rows_by_policy_market(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {RAW_POLICY, WAIT_POLICY, RMT_WAIT_POLICY}
    }


def choose_rows(wait_policy: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = rows_by_policy_market(rows)
    markets = sorted({market for policy, market in indexed if policy == RAW_POLICY and market})
    selected: list[dict[str, Any]] = []
    for market in markets:
        raw = indexed.get((RAW_POLICY, market))
        wait = indexed.get((wait_policy, market))
        if not raw:
            continue
        if not wait:
            selected.append({"meta_policy": f"raw_else_{wait_policy}_missing_wait", "selection_reason": "wait_missing_use_raw", **raw})
            continue
        if raw.get("side") == wait.get("side"):
            selected.append({"meta_policy": f"raw_when_same_else_{wait_policy}", "selection_reason": "same_side_use_raw", **raw})
        else:
            selected.append({"meta_policy": f"raw_when_same_else_{wait_policy}", "selection_reason": "side_flip_use_wait", **wait})
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
        "same_side_use_raw": sum(1 for row in rows if row.get("selection_reason") == "same_side_use_raw"),
        "side_flip_use_wait": sum(1 for row in rows if row.get("selection_reason") == "side_flip_use_wait"),
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    payload = build_entry_bakeoff_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    denominator = len(watched_markets())
    selected_a = choose_rows(WAIT_POLICY, rows)
    selected_b = choose_rows(RMT_WAIT_POLICY, rows)
    summary = [
        summarize("raw_when_same_else_first_side_p60", selected_a, denominator),
        summarize("raw_when_same_else_rmt_p60", selected_b, denominator),
    ]
    return {
        "watched_markets": denominator,
        "summary": summary,
        "rows": selected_a + selected_b,
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
        "# v28 Side-Agreement Meta Candidate",
        "",
        "Uses raw broad timing when p60 agrees on side; waits for p60 when side flips.",
        "",
        f"- Watched markets: `{report['watched_markets']}`",
        "",
        "## Summary",
        "",
        "| policy | entries | settled | wins/losses | coverage | net c | avg net c | brier | same raw | flip wait | actual/shadow |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_net_cents_after_entry_fee'])} | "
            f"{fmt(row['avg_brier'])} | {row['same_side_use_raw']} | {row['side_flip_use_wait']} | "
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
