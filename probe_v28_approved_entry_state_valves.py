"""Actual-approved v28 entry state-valve diagnostics.

Research-only; no live bot changes or orders.

The current source-aware FV overlay improves calibration largely because v28
approved entries can be overconfident versus the executable book during same
market reentry clusters. This probe tests simple physical valves on actual
approved entries only.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from probe_v28_forward_physics_registry import build_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_approved_entry_state_valves_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_state_valves_latest.md"


def parse_ts(value: Any) -> datetime:
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min


def book_prob(row: dict[str, Any]) -> float | None:
    ask = row.get("ask_cents")
    if ask is None:
        return None
    return float(ask) / 100.0


def raw_prob(row: dict[str, Any]) -> float | None:
    value = row.get("p_side")
    return None if value is None else float(value)


def raw_book_gap(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    return None if raw is None or book is None else raw - book


def sorted_rows() -> list[dict[str, Any]]:
    rows = [dict(row) for row in build_rows() if row.get("side_won") is not None]
    rows.sort(key=lambda row: (str(row.get("market") or ""), parse_ts(row.get("entry_ts"))))
    return rows


def with_state(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts_by_market: dict[str, int] = {}
    counts_by_market_side: dict[tuple[str, str], int] = {}
    last_book_by_market_side: dict[tuple[str, str], float] = {}
    out = []
    for row in rows:
        market = str(row.get("market") or "")
        side = str(row.get("side") or "")
        key = (market, side)
        enriched = dict(row)
        enriched["market_entry_index"] = counts_by_market.get(market, 0)
        enriched["market_side_entry_index"] = counts_by_market_side.get(key, 0)
        enriched["book_prob"] = book_prob(row)
        enriched["raw_book_gap"] = raw_book_gap(row)
        enriched["book_delta_vs_prior_same_side"] = (
            None
            if key not in last_book_by_market_side or enriched["book_prob"] is None
            else float(enriched["book_prob"]) - float(last_book_by_market_side[key])
        )
        out.append(enriched)
        counts_by_market[market] = counts_by_market.get(market, 0) + 1
        counts_by_market_side[key] = counts_by_market_side.get(key, 0) + 1
        if enriched["book_prob"] is not None:
            last_book_by_market_side[key] = float(enriched["book_prob"])
    return out


def candidate_fns() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "current_v28_approved_all": lambda row: True,
        "first_entry_per_market": lambda row: int(row.get("market_entry_index") or 0) == 0,
        "no_same_side_reentry": lambda row: int(row.get("market_side_entry_index") or 0) == 0,
        "raw_book_gap_lte_20pp": lambda row: (row.get("raw_book_gap") is None or float(row["raw_book_gap"]) <= 0.20),
        "raw_book_gap_lte_15pp": lambda row: (row.get("raw_book_gap") is None or float(row["raw_book_gap"]) <= 0.15),
        "same_side_reentry_gap_lte_15pp": lambda row: (
            int(row.get("market_side_entry_index") or 0) == 0
            or row.get("raw_book_gap") is None
            or float(row["raw_book_gap"]) <= 0.15
        ),
        "same_side_reentry_book_not_down_10pp": lambda row: (
            int(row.get("market_side_entry_index") or 0) == 0
            or row.get("book_delta_vs_prior_same_side") is None
            or float(row["book_delta_vs_prior_same_side"]) >= -0.10
        ),
        "same_side_reentry_gap_lte15_and_book_not_down10": lambda row: (
            int(row.get("market_side_entry_index") or 0) == 0
            or (
                (row.get("raw_book_gap") is None or float(row["raw_book_gap"]) <= 0.15)
                and (
                    row.get("book_delta_vs_prior_same_side") is None
                    or float(row["book_delta_vs_prior_same_side"]) >= -0.10
                )
            )
        ),
    }


def score(rows: list[dict[str, Any]], policy: str, keep: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    selected = [row for row in rows if keep(row)]
    skipped = [row for row in rows if not keep(row)]
    markets = {row.get("market") for row in rows}
    selected_markets = {row.get("market") for row in selected}
    selected_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in selected)
    current_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    skipped_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in skipped)
    return {
        "policy": policy,
        "entries": len(selected),
        "settled": len(selected),
        "wins": sum(1 for row in selected if row.get("side_won") is True),
        "losses": sum(1 for row in selected if row.get("side_won") is False),
        "gross_cents": selected_gross,
        "delta_vs_current_cents": selected_gross - current_gross,
        "skipped_entries": len(skipped),
        "skipped_gross_cents": skipped_gross,
        "market_coverage_pct": 100.0 * len(selected_markets) / len(markets) if markets else None,
        "skipped_markets": len(markets - selected_markets),
    }


def skipped_examples(rows: list[dict[str, Any]], keep: Callable[[dict[str, Any]], bool]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if keep(row):
            continue
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "gross_cents": row.get("actual_gross_cents"),
            "p_side": row.get("p_side"),
            "ask_cents": row.get("ask_cents"),
            "raw_book_gap": row.get("raw_book_gap"),
            "market_side_entry_index": row.get("market_side_entry_index"),
            "book_delta_vs_prior_same_side": row.get("book_delta_vs_prior_same_side"),
        })
    return out[:20]


def build_report() -> dict[str, Any]:
    rows = with_state(sorted_rows())
    ranked = [score(rows, name, fn) for name, fn in candidate_fns().items()]
    ranked.sort(key=lambda row: (float(row.get("delta_vs_current_cents") or 0.0), float(row.get("gross_cents") or 0.0)), reverse=True)
    best = ranked[0] if ranked else {}
    examples = {
        name: skipped_examples(rows, fn)
        for name, fn in candidate_fns().items()
        if name != "current_v28_approved_all"
    }
    return {
        "entry_surface": "actual_v28_approved_entries_only",
        "total_rows": len(rows),
        "markets": len({row.get("market") for row in rows}),
        "best_policy": best.get("policy"),
        "ranked": ranked,
        "skipped_examples": examples,
        "interpretation": current_read(ranked),
    }


def current_read(ranked: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return ["No settled approved-entry rows available."]
    best = ranked[0]
    control = next((row for row in ranked if row.get("policy") == "current_v28_approved_all"), {})
    return [
        f"Best actual-only state valve is {best.get('policy')} with delta {best.get('delta_vs_current_cents')}c vs current approved entries.",
        f"Control approved entries are {control.get('entries')} rows with gross {control.get('gross_cents')}c.",
        "This is diagnostic only because it is evaluated on already-approved live/shadow entries, not a frozen future promotion slice.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Approved-Entry State Valves",
        "",
        "Actual-approved-entry diagnostic for same-market reentry and raw/book disagreement valves.",
        "",
        f"- Surface: `{report.get('entry_surface')}`",
        f"- Rows/markets: `{report.get('total_rows')}/{report.get('markets')}`",
        f"- Best policy: `{report.get('best_policy')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | policy | entries | W/L | market coverage | gross c | delta c | skipped | skipped gross c | skipped markets |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('policy')}` | {row.get('entries')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('market_coverage_pct'))} | {fmt(row.get('gross_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('skipped_entries')} | "
            f"{fmt(row.get('skipped_gross_cents'))} | {row.get('skipped_markets')} |"
        )
    lines.extend(["", "## Skipped Examples", ""])
    for policy, examples in (report.get("skipped_examples") or {}).items():
        if not examples:
            continue
        lines.append(f"### {policy}")
        for row in examples[:5]:
            lines.append(
                f"- `{row.get('market')}` `{row.get('side')}` won `{row.get('won')}`, "
                f"gross `{fmt(row.get('gross_cents'))}`, raw/book gap `{fmt(row.get('raw_book_gap'))}`, "
                f"same-side idx `{row.get('market_side_entry_index')}`, book delta `{fmt(row.get('book_delta_vs_prior_same_side'))}`"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
