"""Runway and miss audit for frozen target-coverage p70 FV.

Research-only; no live bot changes or orders.

The p70 FV validator can have a forward denominator before it has entries.
This report explains that gap by listing post-freeze markets, whether the
target-coverage entry surface selected anything, and what raw candidate rows
were visible.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_frozen_target_coverage_p70_fv import STATE_JSON
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_runway_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_target_coverage_p70_runway_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def detail(row: dict[str, Any], status: str) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source"),
        "status": status,
        "p_raw": row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "coverage_valve_reason": row.get("coverage_valve_reason"),
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = state.get("freeze_ts_utc")
    if not freeze_ts:
        return {
            "state_path": str(STATE_JSON),
            "future_denominator": 0,
            "interpretation": ["Frozen p70 state does not exist yet."],
        }
    timing = market_timing(parse_ts(freeze_ts))
    forward_markets = sorted(timing["clean_forward_markets"])
    base_rows_all = selected_base_rows()
    target_rows_all = apply_policy(base_rows_all, str(state.get("entry_policy") or DEFAULT_POLICY))
    base_by_market = {
        market: [row for row in base_rows_all if str(row.get("market") or "") == market]
        for market in forward_markets
    }
    target_by_market = {
        market: [row for row in target_rows_all if str(row.get("market") or "") == market]
        for market in forward_markets
    }
    markets = []
    for market in forward_markets:
        base_rows = base_by_market.get(market) or []
        selected_rows = target_by_market.get(market) or []
        markets.append({
            "market": market,
            "base_row_count": len(base_rows),
            "selected_row_count": len(selected_rows),
            "settled_selected_count": sum(1 for row in selected_rows if row.get("side_won") is not None),
            "status": "selected" if selected_rows else ("base_seen_not_selected" if base_rows else "no_target_base_row"),
            "base_rows": [detail(row, "base") for row in base_rows],
            "selected_rows": [detail(row, "selected") for row in selected_rows],
        })
    selected_count = sum(int(row["selected_row_count"]) for row in markets)
    base_seen_count = sum(1 for row in markets if int(row["base_row_count"]) > 0)
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "selected_entries": selected_count,
        "base_seen_markets": base_seen_count,
        "coverage_pct": 100.0 * selected_count / len(forward_markets) if forward_markets else None,
        "base_opportunity_summary": base_opportunity_summary(markets),
        "markets": markets,
        "interpretation": interpretation(markets),
    }


def raw_bucket(p_raw: float | None) -> str:
    if p_raw is None:
        return "missing_raw"
    if p_raw < 0.60:
        return "raw_lt_60"
    if p_raw < 0.70:
        return "raw_60_70_boundary"
    return "raw_ge_70_p70_adjustable"


def base_opportunity_summary(markets: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "base_rows": 0,
        "selected_rows": 0,
        "raw_lt_60": 0,
        "raw_60_70_boundary": 0,
        "raw_ge_70_p70_adjustable": 0,
        "missing_raw": 0,
        "near_edge_miss_lt_2pp": 0,
        "high_recross_miss_ge_75": 0,
        "p70_adjustable_unselected": 0,
    }
    for market in markets:
        selected_markets = {str(row.get("market") or "") for row in market.get("selected_rows") or []}
        for row in market.get("base_rows") or []:
            summary["base_rows"] += 1
            p_raw = as_float(row.get("p_raw"))
            bucket = raw_bucket(p_raw)
            summary[bucket] += 1
            edge = as_float(row.get("raw_edge_prob"))
            recross = as_float(row.get("recross_hazard_score"))
            if edge is not None and edge < 0.02:
                summary["near_edge_miss_lt_2pp"] += 1
            if recross is not None and recross >= 0.75:
                summary["high_recross_miss_ge_75"] += 1
            if bucket == "raw_ge_70_p70_adjustable" and str(row.get("market") or "") not in selected_markets:
                summary["p70_adjustable_unselected"] += 1
        summary["selected_rows"] += len(market.get("selected_rows") or [])
    return summary


def interpretation(markets: list[dict[str, Any]]) -> list[str]:
    if not markets:
        return ["No clean post-freeze markets exist yet for frozen p70."]
    selected = sum(1 for row in markets if row.get("status") == "selected")
    base_unselected = sum(1 for row in markets if row.get("status") == "base_seen_not_selected")
    no_base = sum(1 for row in markets if row.get("status") == "no_target_base_row")
    summary = base_opportunity_summary(markets)
    p70_unselected = summary.get("p70_adjustable_unselected")
    return [
        f"Frozen p70 has {selected} selected markets, {base_unselected} markets with base rows that failed the target policy, and {no_base} markets with no target base row.",
        f"Base rows by raw-probability bucket: <60={summary.get('raw_lt_60')}, 60-70 boundary={summary.get('raw_60_70_boundary')}, >=70 p70-adjustable={summary.get('raw_ge_70_p70_adjustable')}.",
        f"Unselected p70-adjustable rows: {p70_unselected}; if this stays 0, the current blocker is not p70 scoring but lack of high-confidence post-freeze opportunities.",
        "If no-base dominates, the blocker is evidence availability/entry-surface opportunity, not p70 probability scoring.",
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
        "# v28 Frozen Target-Coverage P70 Runway",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Selected entries: `{report.get('selected_entries')}`",
        f"- Base-seen markets: `{report.get('base_seen_markets')}`",
        f"- Coverage: `{fmt(report.get('coverage_pct'))}`",
        f"- Base opportunity summary: `{report.get('base_opportunity_summary')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Markets",
        "",
        "| market | status | base rows | selected rows | settled selected |",
        "|---|---|---:|---:|---:|",
    ])
    for row in report.get("markets") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('status')} | {row.get('base_row_count')} | "
            f"{row.get('selected_row_count')} | {row.get('settled_selected_count')} |"
        )
        for base in row.get("base_rows") or []:
            lines.append(
                f"| -> {base.get('side')} {base.get('source')} | base raw/ask/edge/recross "
                f"{fmt(base.get('p_raw'))}/{fmt(base.get('ask_prob'))}/{fmt(base.get('raw_edge_prob'))}/{fmt(base.get('recross_hazard_score'))} |  |  |  |"
            )
        for selected in row.get("selected_rows") or []:
            lines.append(
                f"| -> {selected.get('side')} {selected.get('source')} | selected raw/ask/edge/recross "
                f"{fmt(selected.get('p_raw'))}/{fmt(selected.get('ask_prob'))}/{fmt(selected.get('raw_edge_prob'))}/{fmt(selected.get('recross_hazard_score'))} |  |  |  |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
