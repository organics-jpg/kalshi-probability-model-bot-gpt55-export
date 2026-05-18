"""Raw p52 book-disagreement shrink entry diagnostic.

Research-only; no live bot changes or orders.

Physics hypothesis:
    When raw v28 is far above the executable Kalshi book, the model may be
    over-reading boundary geometry. Instead of a hard skip, shrink probability
    toward the book only in that disagreement regime, then re-apply the raw p52
    nonnegative-edge entry surface.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import p_raw
from probe_v28_continuous_scorecard import watched_markets


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_book_shrink_entry_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_book_shrink_entry_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"
MIN_P = 0.52
MIN_EDGE = 0.0
GAP_TRIGGER = 0.15


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp(p: float) -> float:
    return max(0.0, min(1.0, p))


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return None
    return ask if ask <= 1.0 else ask / 100.0


def blend(raw: float, book: float, weight: float) -> float:
    return clamp((1.0 - weight) * raw + weight * book)


def shrink_gap15(weight: float) -> Callable[[dict[str, Any]], float]:
    def _fn(row: dict[str, Any]) -> float:
        raw = p_raw(row)
        book = ask_prob(row)
        if book is not None and raw - book > GAP_TRIGGER:
            return blend(raw, book, weight)
        return raw
    return _fn


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "gap15_book25": shrink_gap15(0.25),
    "gap15_book50": shrink_gap15(0.50),
    "gap15_book75": shrink_gap15(0.75),
}


def selected_rows(rows: list[dict[str, Any]], variant: str, fn: Callable[[dict[str, Any]], float]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not base_tradeable(row):
            continue
        ask = ask_prob(row)
        if ask is None:
            continue
        try:
            raw = p_raw(row)
            p_eff = fn(row)
        except (KeyError, TypeError, ValueError):
            continue
        edge = p_eff - ask
        if p_eff < MIN_P or edge < MIN_EDGE:
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = {
                **row,
                "policy": f"{variant}_p52_edge0",
                "variant": variant,
                "p_eff": p_eff,
                "raw_p_eff": raw,
                "ask_prob": ask,
                "eff_edge_prob": edge,
                "raw_book_gap": raw - ask,
                "shrunk": p_eff != raw,
                "net_gross_cents_after_entry_fee": None
                if row.get("gross_cents") is None
                else float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row),
            }
    return [picked[key] for key in sorted(picked)]


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


def summarize(rows: list[dict[str, Any]], watched_count: int) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    net = sum(
        float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0)
        for row in rows
        if row.get("gross_cents") is not None
    )
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled_rows
        if row.get("p_eff") is not None
    ]
    wins = sum(1 for row in settled_rows if row.get("side_won") is True)
    losses = sum(1 for row in settled_rows if row.get("side_won") is False)
    return {
        "entries": len(rows),
        "settled": len(settled_rows),
        "wins": wins,
        "losses": losses,
        "coverage_pct": 100.0 * len(rows) / watched_count if watched_count else None,
        "net_cents": net,
        "avg_brier": avg(briers),
        "avg_p": avg(row.get("p_eff") for row in settled_rows),
        "win_rate": wins / len(settled_rows) if settled_rows else None,
        "shrunk_count": sum(1 for row in rows if row.get("shrunk") is True),
        "actual_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "sim_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    rows = observation_pool()
    watched = len(watched_markets())
    all_selected: list[dict[str, Any]] = []
    summaries = []
    for variant, fn in VARIANTS.items():
        picked = selected_rows(rows, variant, fn)
        all_selected.extend(picked)
        summaries.append({
            "policy": f"{variant}_p52_edge0",
            **summarize(picked, watched),
        })
    ranked = sorted(
        summaries,
        key=lambda row: (
            row.get("coverage_pct") is not None and 75.0 <= float(row.get("coverage_pct") or 0.0) <= 90.0,
            float(row.get("net_cents") or -999999.0),
            -float(row.get("avg_brier") or 999.0),
        ),
        reverse=True,
    )
    base = next((row for row in summaries if row.get("policy") == "raw_probability_p52_edge0"), {})
    return {
        "base_policy": BASE_POLICY,
        "rule_family": "Shrink raw v28 toward executable ask only when raw - ask > 15pp, then require p>=0.52 and edge>=0.",
        "watched_markets": watched,
        "summary": summaries,
        "ranked": ranked,
        "base": base,
        "rows": all_selected,
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
        "# v28 Raw p52 Book-Shrink Entry",
        "",
        "Discovery diagnostic only. Frozen validator fixes a single variant before forward validation.",
        "",
        f"- Base policy: `{report.get('base_policy')}`",
        f"- Rule family: `{report.get('rule_family')}`",
        f"- Watched markets: `{report.get('watched_markets')}`",
        "",
        "## Ranked",
        "",
        "| rank | policy | entries | settled | W/L | coverage | net c | avg brier | avg p | win rate | shrunk | actual/sim |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | "
            f"{row.get('shrunk_count')} | {row.get('actual_count')}/{row.get('sim_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
