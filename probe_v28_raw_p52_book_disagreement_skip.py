"""Raw p52 book-disagreement skip diagnostic.

Research-only; no live bot changes or orders.

Physics hypothesis:
    Kalshi touch price is a noisy crowd prior. When raw v28 p52 says the
    selected side is more than 15 percentage points better than the executable
    ask, the model may be overconfident about path risk near the boundary.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_book_disagreement_skip_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_book_disagreement_skip_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"
MAX_V28_MINUS_BOOK = 0.15


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


def p_eff(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_eff") if row.get("p_eff") is not None else row.get("p_side"))


def v28_minus_book(row: dict[str, Any]) -> float | None:
    p = p_eff(row)
    ask = ask_prob(row)
    if p is None or ask is None:
        return None
    return p - ask


def is_overconfident_vs_book(row: dict[str, Any]) -> bool:
    delta = v28_minus_book(row)
    return delta is not None and delta > MAX_V28_MINUS_BOOK


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
        "avg_ask": avg(ask_prob(row) for row in settled_rows),
        "avg_p": avg(p_eff(row) for row in settled_rows),
        "avg_v28_minus_book": avg(v28_minus_book(row) for row in settled_rows),
        "win_rate": wins / len(settled_rows) if settled_rows else None,
        "actual_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "sim_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    source = build_raw_report()
    watched = int(source.get("watched_markets") or 0)
    base = [row for row in source.get("rows") or [] if row.get("policy") == BASE_POLICY]
    kept = [row for row in base if not is_overconfident_vs_book(row)]
    skipped = [row for row in base if is_overconfident_vs_book(row)]
    base_s = summarize(base, watched)
    kept_s = summarize(kept, watched)
    skipped_s = summarize(skipped, watched)
    return {
        "base_policy": BASE_POLICY,
        "candidate": "raw_p52_skip_v28_minus_book_gt15pp",
        "rule": "Start from v28_raw_p52_edge0 and skip rows where p_eff - executable ask probability > 15pp.",
        "physics": "Large positive disagreement against the executable book can be hidden path-risk overconfidence; require forward proof before use.",
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
        "# v28 Raw p52 Book-Disagreement Skip",
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
        "| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg p-book | net c | actual/sim |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["base", "candidate_summary", "skipped_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('avg_ask'))} | {fmt(row.get('avg_v28_minus_book'))} | {fmt(row.get('net_cents'))} | "
            f"{row.get('actual_count')}/{row.get('sim_count')} |"
        )
    lines.extend([
        "",
        "## Skipped Rows",
        "",
        "| market | side | source | p | ask | p-book | won | net c |",
        "|---|---|---|---:|---:|---:|---|---:|",
    ])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(p_eff(row))} | "
            f"{fmt(ask_prob(row))} | {fmt(v28_minus_book(row))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_gross_cents_after_entry_fee') or row.get('gross_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
