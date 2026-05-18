"""PnL attribution for the current v28 target-coverage surface.

Research-only; no live bot changes or orders.

This separates FV/entry direction errors from execution/exit-shaped PnL damage.
For the broad target surface, many rows are rejected-actionable simulations,
so this report is careful to label rows by source and by whether the selected
side actually won.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_target_coverage_pnl_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_pnl_attribution_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def forward_rows() -> tuple[list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    selected = apply_policy(selected_base_rows(), POLICY)
    rows = [row for row in selected if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def net_cents(row: dict[str, Any]) -> float | None:
    return as_float(row.get("net_gross_cents_after_entry_fee"))


def classify(row: dict[str, Any]) -> str:
    net = net_cents(row)
    if row.get("side_won") is None:
        return "unsettled"
    if row.get("side_won") is False:
        return "direction_wrong"
    if net is not None and net < 0.0:
        return "side_won_but_negative_pnl"
    return "side_won_positive_pnl"


def tags(row: dict[str, Any]) -> list[str]:
    out = []
    p = as_float(row.get("p_side"))
    edge = as_float(row.get("raw_edge_prob"))
    ask = as_float(row.get("ask_prob"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    stc = as_float(row.get("seconds_to_close"))
    source = str(row.get("source") or "unknown")
    reason = str(row.get("coverage_valve_reason") or row.get("reason") or "unknown")
    out.append(f"source:{source}")
    out.append(f"reason:{reason}")
    if p is not None:
        if p < 0.60:
            out.append("p_lt_60")
        elif p < 0.70:
            out.append("p_60_70")
        elif p < 0.80:
            out.append("p_70_80")
        else:
            out.append("p_ge_80")
    if edge is not None:
        if edge < 0.02:
            out.append("edge_lt_2pp")
        elif edge < 0.04:
            out.append("edge_2_4pp")
        else:
            out.append("edge_ge_4pp")
    if ask is not None:
        if ask >= 0.78:
            out.append("expensive_ge_78c")
        elif ask <= 0.55:
            out.append("cheap_lte_55c")
    if abs_d is not None:
        if abs_d <= 0.30:
            out.append("near_boundary_absd_lte_030")
        elif abs_d >= 0.75:
            out.append("far_boundary_absd_ge_075")
    if recross is not None:
        if recross >= 0.75:
            out.append("high_recross_ge_075")
        elif recross <= 0.45:
            out.append("low_recross_lte_045")
    if stc is not None:
        if stc >= 780.0:
            out.append("early_stc_ge_780")
        elif stc <= 480.0:
            out.append("late_stc_lte_480")
    return out


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(net_cents(row) or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
    }


def grouped_rollups(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(classify(row), []).append(row)
        for tag in tags(row):
            groups.setdefault(tag, []).append(row)
    out = {}
    for name, group in groups.items():
        settled = [row for row in group if row.get("side_won") is not None]
        out[name] = {
            "rows": len(group),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "net_cents": sum(float(net_cents(row) or 0.0) for row in settled),
            "avg_net_cents": (
                sum(float(net_cents(row) or 0.0) for row in settled) / len(settled)
                if settled
                else None
            ),
        }
    return out


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "reason": row.get("coverage_valve_reason") or row.get("reason"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "class": classify(row),
        "net_cents": net_cents(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "tags": tags(row),
    }


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    settled = [row for row in rows if row.get("side_won") is not None]
    direction_wrong = [row for row in settled if classify(row) == "direction_wrong"]
    side_won_negative = [row for row in settled if classify(row) == "side_won_but_negative_pnl"]
    rollups = grouped_rollups(rows)
    return {
        "policy": POLICY,
        "forward_denominator": denominator,
        "summary": summarize(rows, denominator),
        "class_rollups": {key: value for key, value in rollups.items() if key in {
            "direction_wrong",
            "side_won_but_negative_pnl",
            "side_won_positive_pnl",
            "unsettled",
        }},
        "tag_rollups": {
            key: value
            for key, value in sorted(
                ((k, v) for k, v in rollups.items() if ":" in k or k.startswith(("p_", "edge_", "cheap", "expensive", "near_", "far_", "high_", "low_", "early_", "late_"))),
                key=lambda item: (float(item[1].get("net_cents") or 0.0), -int(item[1].get("settled") or 0)),
            )
        },
        "direction_wrong_rows": [row_view(row) for row in sorted(direction_wrong, key=lambda r: float(net_cents(r) or 0.0))],
        "side_won_negative_rows": [row_view(row) for row in sorted(side_won_negative, key=lambda r: float(net_cents(r) or 0.0))],
        "interpretation": interpretation(rows, direction_wrong, side_won_negative, denominator),
    }


def interpretation(
    rows: list[dict[str, Any]],
    direction_wrong: list[dict[str, Any]],
    side_won_negative: list[dict[str, Any]],
    denominator: int,
) -> list[str]:
    settled = [row for row in rows if row.get("side_won") is not None]
    wrong_net = sum(float(net_cents(row) or 0.0) for row in direction_wrong)
    won_negative_net = sum(float(net_cents(row) or 0.0) for row in side_won_negative)
    notes = [
        f"Target surface has {len(rows)} entries over {denominator} markets; {len(settled)} settled.",
        f"Direction-wrong rows contribute {wrong_net}c across {len(direction_wrong)} rows.",
        f"Side-won-but-negative rows contribute {won_negative_net}c across {len(side_won_negative)} rows.",
    ]
    if side_won_negative:
        notes.append("Do not use side-won negative-PnL rows as pure FV failures; they are exit/execution shaped.")
    if direction_wrong:
        notes.append("FV/entry work should focus on directional losers, especially recurring tags that preserve coverage.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Target-Coverage PnL Attribution",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Entries/settled/coverage: `{summary.get('entries')}/{summary.get('settled')}/{fmt(summary.get('coverage_pct'))}`",
        f"- Net cents: `{fmt(summary.get('net_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Class Rollups",
        "",
        "| class | rows | settled | W/L | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for name, row in report.get("class_rollups", {}).items():
        lines.append(
            f"| {name} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Worst Tag Rollups",
        "",
        "| tag | rows | settled | W/L | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for name, row in list(report.get("tag_rollups", {}).items())[:18]:
        lines.append(
            f"| {name} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Direction-Wrong Rows",
        "",
        "| market | source | reason | side | net c | p | ask | edge | stc | abs d | recross | tags |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("direction_wrong_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('reason')} | {row.get('side')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('edge_prob'))} | {fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {', '.join(row.get('tags') or [])} |"
        )
    lines.extend([
        "",
        "## Side-Won Negative-PnL Rows",
        "",
        "| market | source | reason | side | net c | p | ask | edge | stc | abs d | recross | tags |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("side_won_negative_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('reason')} | {row.get('side')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('edge_prob'))} | {fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
