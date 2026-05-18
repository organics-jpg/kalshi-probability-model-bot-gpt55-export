"""Raw p52 favorite-valley skip diagnostic.

Research-only; no live bot changes or orders.

Physics hypothesis:
    BTC 15m contracts around 65-75c are a dangerous middle-favorite zone for
    raw v28 p52. They are expensive enough that each miss is large, but not so
    close to settlement-certainty that the price geometry is forgiving. If the
    side probability does not dominate that ask band, the fair value can look
    accurate while the trade remains negative EV.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_favorite_valley_skip_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_favorite_valley_skip_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return None
    return ask if ask <= 1.0 else ask / 100.0


def is_favorite_valley(row: dict[str, Any]) -> bool:
    ask = ask_prob(row)
    return ask is not None and 0.65 <= ask < 0.75


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0) for row in rows if settled(row))


def summarize(rows: list[dict[str, Any]], watched: int) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    return {
        "entries": len(rows),
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
        "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / watched if watched else None,
        "net_cents": net_cents(rows),
        "avg_ask": avg(ask_prob(row) for row in settled_rows),
        "win_rate": (
            sum(1 for row in settled_rows if row.get("side_won") is True) / len(settled_rows)
            if settled_rows else None
        ),
        "actual_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "sim_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


def build_report() -> dict[str, Any]:
    source = build_raw_report()
    watched = int(source.get("watched_markets") or 0)
    base = [row for row in source.get("rows") or [] if row.get("policy") == BASE_POLICY]
    kept = [row for row in base if not is_favorite_valley(row)]
    skipped = [row for row in base if is_favorite_valley(row)]
    base_s = summarize(base, watched)
    kept_s = summarize(kept, watched)
    skipped_s = summarize(skipped, watched)
    return {
        "base_policy": BASE_POLICY,
        "candidate": "raw_p52_skip_ask65_75_favorite_valley",
        "rule": "Start from v28_raw_p52_edge0 and skip selected entries with executable ask in [65c, 75c).",
        "physics": "Middle-favorite prices have large loss severity without enough certainty; require future validation before use.",
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
        "# v28 Raw p52 Favorite-Valley Skip",
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
        "| row | entries | settled | W/L | coverage | win rate | avg ask | net c | actual/sim |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["base", "candidate_summary", "skipped_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_ask'))} | "
            f"{fmt(row.get('net_cents'))} | {row.get('actual_count')}/{row.get('sim_count')} |"
        )
    lines.extend([
        "",
        "## Skipped Rows",
        "",
        "| market | side | source | p | ask | won | net c |",
        "|---|---|---|---:|---:|---|---:|",
    ])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(row.get('p_eff'))} | "
            f"{fmt(ask_prob(row))} | {row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee') or row.get('gross_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
