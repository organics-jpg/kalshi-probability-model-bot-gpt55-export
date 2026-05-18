"""Danger-zone entry valve diagnostics for v28 approved entries.

Research-only; no live bot changes or orders.

Tests simple physical danger-zone filters suggested by the probability/profit
bridge:
- same-side reentry is weak;
- raw FV more than 30pp above executable book is weak.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_approved_entry_state_valves import sorted_rows, with_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_danger_zone_entry_valve_latest.json"
OUT_MD = OUT_DIR / "v28_danger_zone_entry_valve_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def raw_book_gap(row: dict[str, Any]) -> float | None:
    return as_float(row.get("raw_book_gap"))


def is_same_side_reentry(row: dict[str, Any]) -> bool:
    return int(row.get("market_side_entry_index") or 0) > 0


def policies() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "current_v28_approved_all": lambda row: True,
        "skip_same_side_reentry": lambda row: not is_same_side_reentry(row),
        "skip_raw_book_gap_gt30": lambda row: raw_book_gap(row) is None or float(raw_book_gap(row)) <= 0.30,
        "skip_reentry_gap15_or_gap30": lambda row: (
            (not is_same_side_reentry(row) or raw_book_gap(row) is None or float(raw_book_gap(row)) <= 0.15)
            and (raw_book_gap(row) is None or float(raw_book_gap(row)) <= 0.30)
        ),
        "skip_reentry_or_gap30": lambda row: (
            not is_same_side_reentry(row)
            and (raw_book_gap(row) is None or float(raw_book_gap(row)) <= 0.30)
        ),
    }


def score(rows: list[dict[str, Any]], name: str, keep: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    selected = [row for row in rows if keep(row)]
    skipped = [row for row in rows if not keep(row)]
    markets = {row.get("market") for row in rows}
    selected_markets = {row.get("market") for row in selected}
    current_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    selected_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in selected)
    selected_hold = sum(float(row.get("hold_gross_cents") or 0.0) for row in selected)
    return {
        "policy": name,
        "entries": len(selected),
        "settled": len(selected),
        "wins": sum(1 for row in selected if row.get("side_won") is True),
        "losses": sum(1 for row in selected if row.get("side_won") is False),
        "gross_cents": selected_gross,
        "hold_gross_cents": selected_hold,
        "delta_vs_current_cents": selected_gross - current_gross,
        "skipped_entries": len(skipped),
        "skipped_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in skipped),
        "skipped_hold_gross_cents": sum(float(row.get("hold_gross_cents") or 0.0) for row in skipped),
        "market_coverage_pct": 100.0 * len(selected_markets) / len(markets) if markets else None,
        "skipped_examples": skipped_examples(skipped),
    }


def skipped_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows[:12]:
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "gross_cents": row.get("actual_gross_cents"),
            "hold_gross_cents": row.get("hold_gross_cents"),
            "p_side": row.get("p_side"),
            "ask_cents": row.get("ask_cents"),
            "raw_book_gap": row.get("raw_book_gap"),
            "market_side_entry_index": row.get("market_side_entry_index"),
        })
    return out


def build_report() -> dict[str, Any]:
    rows = [row for row in with_state(sorted_rows()) if row.get("side_won") is not None]
    ranked = [score(rows, name, keep) for name, keep in policies().items()]
    ranked.sort(key=lambda row: (float(row.get("delta_vs_current_cents") or 0.0), float(row.get("gross_cents") or 0.0)), reverse=True)
    return {
        "surface": "actual_v28_approved_entries_only",
        "rows": len(rows),
        "markets": len({row.get("market") for row in rows}),
        "best_policy": ranked[0].get("policy") if ranked else None,
        "ranked": ranked,
        "interpretation": current_read(ranked),
    }


def current_read(ranked: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return ["No rows."]
    best = ranked[0]
    control = next((row for row in ranked if row.get("policy") == "current_v28_approved_all"), {})
    return [
        f"Best danger-zone policy is {best.get('policy')} with delta {best.get('delta_vs_current_cents')}c and coverage {best.get('market_coverage_pct')}%.",
        f"Control gross is {control.get('gross_cents')}c over {control.get('entries')} entries.",
        "Discovery-only: this must be frozen and validated forward before promotion.",
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
        "# v28 Danger-Zone Entry Valve",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Rows/markets: `{report.get('rows')}/{report.get('markets')}`",
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
        "| rank | policy | entries | W/L | coverage | gross c | hold c | delta c | skipped | skipped gross c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('policy')}` | {row.get('entries')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('market_coverage_pct'))} | {fmt(row.get('gross_cents'))} | {fmt(row.get('hold_gross_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('skipped_entries')} | {fmt(row.get('skipped_gross_cents'))} |"
        )
    lines.extend(["", "## Skipped Examples", ""])
    for row in (report.get("ranked") or [])[:3]:
        examples = row.get("skipped_examples") or []
        if not examples:
            continue
        lines.append(f"### {row.get('policy')}")
        for ex in examples[:5]:
            lines.append(
                f"- `{ex.get('market')}` `{ex.get('side')}` won `{ex.get('won')}`, gross/hold "
                f"`{fmt(ex.get('gross_cents'))}/{fmt(ex.get('hold_gross_cents'))}`, gap `{fmt(ex.get('raw_book_gap'))}`, "
                f"same-side idx `{ex.get('market_side_entry_index')}`"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
