"""Price-friction attribution for the target-coverage v28 surface.

Research-only; no live bot changes or orders.

This report asks a narrow question: are broad-surface losses mostly because
the FV side is directionally wrong, or because the strategy pays too much for
uncertain contracts?  It buckets the fixed target-coverage surface by ask,
raw edge, side, and boundary geometry so candidate rules can be grounded in
execution economics instead of just probability tweaks.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_target_coverage_price_friction_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_price_friction_latest.md"

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


def net_cents(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_gross_cents_after_entry_fee")) or 0.0)


def side_won(row: dict[str, Any]) -> bool | None:
    value = row.get("side_won")
    return value if isinstance(value, bool) else None


def ask(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("ask_prob"))
    if value is not None:
        return value
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def raw_edge(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("raw_edge_prob"))
    if value is not None:
        return value
    p = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    a = ask(row)
    return None if p is None or a is None else p - a


def bucket_ask(row: dict[str, Any]) -> str:
    value = ask(row)
    if value is None:
        return "ask_missing"
    if value < 0.50:
        return "ask_lt_50"
    if value < 0.55:
        return "ask_50_55"
    if value < 0.65:
        return "ask_55_65"
    if value < 0.75:
        return "ask_65_75"
    return "ask_ge_75"


def bucket_edge(row: dict[str, Any]) -> str:
    value = raw_edge(row)
    if value is None:
        return "edge_missing"
    if value < 0.02:
        return "edge_lt_2pp"
    if value < 0.04:
        return "edge_2_4pp"
    if value < 0.08:
        return "edge_4_8pp"
    if value < 0.14:
        return "edge_8_14pp"
    return "edge_ge_14pp"


def bucket_side(row: dict[str, Any]) -> str:
    return f"side_{str(row.get('side') or 'unknown').lower()}"


def bucket_boundary(row: dict[str, Any]) -> str:
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    if abs_d is None or recross is None:
        return "boundary_missing"
    if abs_d <= 0.25 and recross >= 0.75:
        return "near_high_recross"
    if abs_d <= 0.45 and recross >= 0.55:
        return "mid_high_recross"
    if abs_d >= 0.75:
        return "far_from_strike"
    return "ordinary_boundary"


def bucket_clock(row: dict[str, Any]) -> str:
    stc = as_float(row.get("seconds_to_close"))
    if stc is None:
        return "stc_missing"
    if stc >= 780:
        return "early_ge_780"
    if stc >= 660:
        return "early_660_780"
    if stc >= 480:
        return "mid_480_660"
    return "late_lt_480"


def summarize(name: str, rows: list[dict[str, Any]], denominator: int | None = None) -> dict[str, Any]:
    settled = [row for row in rows if side_won(row) is not None]
    wins = [row for row in settled if side_won(row) is True]
    losses = [row for row in settled if side_won(row) is False]
    net = sum(net_cents(row) for row in settled)
    avg_ask_values = [ask(row) for row in settled]
    avg_ask_values = [value for value in avg_ask_values if value is not None]
    edge_values = [raw_edge(row) for row in settled]
    edge_values = [value for value in edge_values if value is not None]
    return {
        "bucket": name,
        "rows": len(rows),
        "settled": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "coverage_pct": None if denominator is None or denominator <= 0 else 100.0 * len(rows) / denominator,
        "win_rate": len(wins) / len(settled) if settled else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "avg_ask": sum(avg_ask_values) / len(avg_ask_values) if avg_ask_values else None,
        "avg_raw_edge": sum(edge_values) / len(edge_values) if edge_values else None,
        "direction_loss_cents": sum(net_cents(row) for row in losses),
        "winner_cents": sum(net_cents(row) for row in wins),
    }


def grouped(rows: list[dict[str, Any]], fn: Callable[[dict[str, Any]], str]) -> list[dict[str, Any]]:
    keys = sorted({fn(row) for row in rows})
    out = [summarize(key, [row for row in rows if fn(row) == key]) for key in keys]
    return sorted(out, key=lambda row: (float(row.get("net_cents") or 0.0), -int(row.get("settled") or 0)))


def composite_tags(row: dict[str, Any]) -> list[str]:
    tags = [
        bucket_ask(row),
        bucket_edge(row),
        bucket_side(row),
        bucket_boundary(row),
        bucket_clock(row),
    ]
    if bucket_side(row) == "side_no" and bucket_clock(row).startswith("early") and bucket_boundary(row) in {
        "near_high_recross",
        "mid_high_recross",
    }:
        tags.append("early_no_boundary_decay")
    if bucket_ask(row) in {"ask_lt_50", "ask_50_55"} and bucket_boundary(row) == "near_high_recross":
        tags.append("cheap_boundary_turbulence")
    return tags


def tag_rollups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for tag in composite_tags(row):
            groups.setdefault(tag, []).append(row)
    return sorted(
        [summarize(tag, group) for tag, group in groups.items()],
        key=lambda row: (float(row.get("net_cents") or 0.0), -int(row.get("settled") or 0)),
    )


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net_cents(row),
        "p_side": row.get("p_side"),
        "ask_prob": ask(row),
        "raw_edge_prob": raw_edge(row),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "tags": composite_tags(row),
    }


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    settled = [row for row in rows if side_won(row) is not None]
    report = {
        "policy": POLICY,
        "forward_denominator": denominator,
        "summary": summarize("all", rows, denominator),
        "by_ask": grouped(rows, bucket_ask),
        "by_edge": grouped(rows, bucket_edge),
        "by_side": grouped(rows, bucket_side),
        "by_boundary": grouped(rows, bucket_boundary),
        "by_clock": grouped(rows, bucket_clock),
        "tag_rollups": tag_rollups(rows),
        "worst_rows": [compact(row) for row in sorted(settled, key=net_cents)[:12]],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary") or {}
    tags = report.get("tag_rollups") or []
    worst_tags = [row for row in tags if int(row.get("settled") or 0) >= 5][:5]
    notes = [
        f"Target surface has {summary.get('settled')} settled rows, win rate {summary.get('win_rate')}, net {summary.get('net_cents')}c.",
        "If a bucket wins often but still loses money, it is likely an entry-price/exit-value problem rather than only an FV side problem.",
    ]
    for row in worst_tags:
        notes.append(
            f"Worst repeated tag {row.get('bucket')} has {row.get('settled')} settled rows, W/L {row.get('wins')}/{row.get('losses')}, net {row.get('net_cents')}c, avg ask {row.get('avg_ask')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def table(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "",
        f"## {title}",
        "",
        "| bucket | settled | W/L | win rate | net c | avg c | avg ask | avg edge | direction c | winner c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        lines.append(
            f"| `{row.get('bucket')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} | "
            f"{fmt(row.get('avg_ask'))} | {fmt(row.get('avg_raw_edge'))} | "
            f"{fmt(row.get('direction_loss_cents'))} | {fmt(row.get('winner_cents'))} |"
        )


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Target-Coverage Price Friction",
        "",
        "Research-only attribution for entry price, edge, side, clock, and boundary geometry.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Entries/settled/coverage: `{summary.get('rows')}/{summary.get('settled')}/{fmt(summary.get('coverage_pct'))}`",
        f"- Net cents: `{fmt(summary.get('net_cents'))}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    table(lines, "By Ask", report.get("by_ask") or [])
    table(lines, "By Raw Edge", report.get("by_edge") or [])
    table(lines, "By Side", report.get("by_side") or [])
    table(lines, "By Boundary", report.get("by_boundary") or [])
    table(lines, "By Clock", report.get("by_clock") or [])
    table(lines, "Worst Tags", (report.get("tag_rollups") or [])[:12])
    lines.extend([
        "",
        "## Worst Rows",
        "",
        "| market | side | won | net c | p | ask | edge | stc | abs d | recross | tags |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("worst_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
