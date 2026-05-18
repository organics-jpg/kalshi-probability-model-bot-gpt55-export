"""Counterfactual reentry-throttle candidates for v28 shadow trades.

This is shadow-only. It asks whether repeated same-side entries in the same
15m market add value after v28 has already exited that side once.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_reentry_throttle_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_reentry_throttle_candidates_latest.md"


def scored_trades() -> list[dict[str, Any]]:
    rows = []
    for trade in reconstruct_trades(read_events()):
        score = score_trade(trade)
        if score.get("actual_gross_cents") is None:
            continue
        rows.append(score)
    return rows


def policy_current(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return rows


def policy_first_entry_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept = []
    seen_markets = set()
    for row in rows:
        market = str(row.get("market") or "")
        if market in seen_markets:
            continue
        seen_markets.add(market)
        kept.append(row)
    return kept


def policy_no_same_side_reentry(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept = []
    seen_market_side = set()
    for row in rows:
        key = (str(row.get("market") or ""), str(row.get("side") or ""))
        if key in seen_market_side:
            continue
        seen_market_side.add(key)
        kept.append(row)
    return kept


def policy_no_same_side_after_model_exit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept = []
    exited_market_side = set()
    model_exit_prefixes = ("mushroom_v28_probability_", "mushroom_v28_exit_value_over_hold")
    for row in rows:
        key = (str(row.get("market") or ""), str(row.get("side") or ""))
        if key in exited_market_side:
            continue
        kept.append(row)
        reason = str(row.get("exit_reason") or "")
        if reason.startswith(model_exit_prefixes):
            exited_market_side.add(key)
    return kept


POLICIES = {
    "current_v28": policy_current,
    "first_entry_per_market": policy_first_entry_per_market,
    "no_same_side_reentry": policy_no_same_side_reentry,
    "no_same_side_after_model_exit": policy_no_same_side_after_model_exit,
}


def summarize_rows(rows: list[dict[str, Any]], current_gross: float) -> dict[str, Any]:
    settled = [row for row in rows if row.get("result") in {"yes", "no"}]
    gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    hold = sum(float(row.get("hold_gross_cents") or 0.0) for row in rows if row.get("hold_gross_cents") is not None)
    return {
        "trades": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if float(row.get("actual_gross_cents") or 0.0) > 0.0),
        "losses": sum(1 for row in settled if float(row.get("actual_gross_cents") or 0.0) < 0.0),
        "gross_cents": gross,
        "hold_cents": hold,
        "delta_vs_current_cents": gross - current_gross,
        "markets": len({str(row.get("market") or "") for row in rows}),
    }


def build_report() -> dict[str, Any]:
    rows = scored_trades()
    current_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    summaries = []
    selected = {}
    for name, fn in POLICIES.items():
        kept = fn(rows)
        selected[name] = kept
        summaries.append({"policy": name, **summarize_rows(kept, current_gross)})
    summaries.sort(key=lambda row: (-float(row["gross_cents"]), row["policy"]))
    return {
        "summary": summaries,
        "selected": selected,
        "rows": rows,
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Reentry Throttle Candidates",
        "",
        "Shadow-only counterfactual. Physical question: after the model exits a side, does reentering the same side in the same 15m market add edge or just chase turbulence?",
        "",
        "## Summary",
        "",
        "| policy | trades | settled | wins | losses | markets | gross c | hold c | delta vs current c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['policy']} | {row['trades']} | {row['settled']} | {row['wins']} | {row['losses']} | "
            f"{row['markets']} | {row['gross_cents']} | {row['hold_cents']} | {row['delta_vs_current_cents']} |"
        )
    lines.extend(["", "## Current Rows", ""])
    lines.append("| market | side | entry | exit | result | gross c | hold c | exit reason |")
    lines.append("|---|---|---:|---:|---|---:|---:|---|")
    for row in report["rows"]:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('entry_cents')} | {row.get('exit_cents')} | "
            f"{row.get('result')} | {row.get('actual_gross_cents')} | {row.get('hold_gross_cents')} | {row.get('exit_reason')} |"
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
