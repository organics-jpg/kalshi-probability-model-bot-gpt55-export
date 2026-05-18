"""Book-dislocation attribution for the v28 false-conviction FV bridge.

Research-only; no live bot changes and no orders.

User hypothesis under test:
    Kalshi BTC 15m books should be inefficient during spikes/dips because some
    participants trade vibes instead of live fair value. The exploitable form
    should be FV/book dislocation filtered by path geometry, not raw gap-chasing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_false_conviction_fv_entry_bridge import (
    OUT_JSON as BRIDGE_JSON,
    STATE_JSON as BRIDGE_STATE_JSON,
    VARIANTS,
    adjusted_edge,
    as_float,
    escape_energy,
    load_json,
    select_entries,
    thin_by_escape_energy,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_book_dislocation_regime_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_book_dislocation_regime_attribution_latest.md"

REFERENCE_FREEZE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"
LEAD_SCORE_NAME = "first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget"
LEAD_SCOPE = "first_eligible_top80_escape_energy"
LEAD_SELECTOR = "escape_edge6_or_p65_or_far_edge4"
LEAD_VARIANT = "continuous_recross_forget"


def classify_edge(row: dict[str, Any]) -> str:
    edge = as_float(row.get("eff_edge_prob"))
    if edge is None:
        return "edge_missing"
    if edge >= 0.12:
        return "deep_discount_ge12pp"
    if edge >= 0.08:
        return "discount_8_12pp"
    if edge >= 0.04:
        return "discount_4_8pp"
    if edge >= 0.00:
        return "thin_discount_0_4pp"
    return "negative_edge"


def classify_path(row: dict[str, Any]) -> str:
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    if abs_d is None or recross is None:
        return "path_unknown"
    if abs_d >= 0.75 and recross < 0.65:
        return "escaped_low_recross"
    if abs_d >= 0.75:
        return "escaped_but_choppy"
    if recross >= 0.75:
        return "near_high_recross"
    if recross >= 0.55:
        return "near_mid_recross"
    return "near_low_recross"


def classify_ask_move(row: dict[str, Any], previous: dict[tuple[str, str], dict[str, Any]]) -> str:
    key = (str(row.get("market") or ""), str(row.get("side") or ""))
    prev = previous.get(key)
    ask = as_float(row.get("ask_prob"))
    prev_ask = as_float(prev.get("ask_prob")) if prev else None
    if ask is None or prev_ask is None:
        return "ask_move_unknown"
    delta = ask - prev_ask
    if delta >= 0.08:
        return "ask_spike_ge8pp"
    if delta >= 0.04:
        return "ask_rise_4_8pp"
    if delta <= -0.08:
        return "ask_dip_ge8pp"
    if delta <= -0.04:
        return "ask_drop_4_8pp"
    return "ask_stable"


def annotate_ask_moves(all_rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_keys = {(str(row.get("market") or ""), str(row.get("side") or ""), str(row.get("ts_wall") or "")) for row in selected}
    previous: dict[tuple[str, str], dict[str, Any]] = {}
    annotations: dict[tuple[str, str, str], str] = {}
    for row in sorted(all_rows, key=lambda item: str(item.get("ts_wall") or "")):
        key2 = (str(row.get("market") or ""), str(row.get("side") or ""))
        key3 = (key2[0], key2[1], str(row.get("ts_wall") or ""))
        if key3 in selected_keys:
            annotations[key3] = classify_ask_move(row, previous)
        previous[key2] = row
    out = []
    for row in selected:
        key3 = (str(row.get("market") or ""), str(row.get("side") or ""), str(row.get("ts_wall") or ""))
        out.append({**row, "ask_move_bucket": annotations.get(key3, "ask_move_unknown")})
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or row.get("net_cents") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "avg_edge": avg(row.get("eff_edge_prob") for row in rows),
        "avg_escape_energy": avg(row.get("escape_energy") for row in rows),
        "approved_entries": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "reconstructed_entries": sum(1 for row in rows if row.get("source") != "approved_entry"),
    }


def avg(values: Any) -> float | None:
    nums = [as_float(value) for value in values]
    nums = [value for value in nums if value is not None]
    return sum(nums) / len(nums) if nums else None


def bucket(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    out = []
    for value in sorted({str(row.get(key) or "") for row in rows}):
        group = [row for row in rows if str(row.get(key) or "") == value]
        out.append({"bucket": value, **summarize(group)})
    out.sort(key=lambda row: (as_float(row.get("net_cents")) or -999999.0), reverse=True)
    return out


def select_lead_rows(all_rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    selected = select_entries(
        all_rows,
        LEAD_SELECTOR,
        LEAD_VARIANT,
        VARIANTS[LEAD_VARIANT],
        "first_eligible",
    )
    selected = thin_by_escape_energy(selected, denominator, 0.80)
    annotated = []
    for row in selected:
        annotated.append(
            {
                **row,
                "escape_energy": escape_energy(row),
                "eff_edge_prob": adjusted_edge(row, float(row.get("p_eff"))),
                "edge_bucket": classify_edge(row),
                "path_bucket": classify_path(row),
            }
        )
    return annotated


def score_window(name: str, freeze_ts: str) -> dict[str, Any]:
    timing = market_timing(parse_ts(freeze_ts))
    future_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in future_markets])
    selected = annotate_ask_moves(all_rows, select_lead_rows(all_rows, len(future_markets)))
    for row in selected:
        row["edge_bucket"] = classify_edge(row)
        row["path_bucket"] = classify_path(row)
        row["book_dislocation_bucket"] = f"{row.get('edge_bucket')}|{row.get('ask_move_bucket')}|{row.get('path_bucket')}"
    return {
        "window": name,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": len(future_markets),
        "lead_score_name": LEAD_SCORE_NAME,
        "summary": {
            **summarize(selected),
            "coverage_pct": 100.0 * len(selected) / len(future_markets) if future_markets else None,
        },
        "by_edge_bucket": bucket(selected, "edge_bucket"),
        "by_ask_move_bucket": bucket(selected, "ask_move_bucket"),
        "by_path_bucket": bucket(selected, "path_bucket"),
        "by_book_dislocation_bucket": bucket(selected, "book_dislocation_bucket"),
        "selected_rows": [compact(row) for row in selected],
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "p_eff": row.get("p_eff"),
        "raw_p_eff": row.get("raw_p_eff"),
        "ask_prob": row.get("ask_prob"),
        "eff_edge_prob": row.get("eff_edge_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "escape_energy": row.get("escape_energy"),
        "edge_bucket": row.get("edge_bucket"),
        "ask_move_bucket": row.get("ask_move_bucket"),
        "path_bucket": row.get("path_bucket"),
    }


def build_report() -> dict[str, Any]:
    state = load_json(BRIDGE_STATE_JSON)
    reference_state = load_json(REFERENCE_FREEZE_JSON)
    reference_freeze = reference_state.get("freeze_ts_utc") or state.get("freeze_ts_utc")
    post_freeze = state.get("freeze_ts_utc")
    windows = []
    if reference_freeze:
        windows.append(score_window("diagnostic_existing_false_conviction_freeze", str(reference_freeze)))
    if post_freeze:
        windows.append(score_window("post_freeze_candidate", str(post_freeze)))
    return {
        "purpose": "Test whether book/FV spikes and dips are usable only when path geometry confirms escape.",
        "lead_score_name": LEAD_SCORE_NAME,
        "bridge_report": str(BRIDGE_JSON),
        "requirements": [
            "research-only, no live bot changes, no orders",
            "classify book dislocations on the current lead FV bridge candidate",
            "separate edge size from ask move and path geometry",
            "promotion still requires post-freeze sample and source-quality gates",
        ],
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = []
    for window in windows:
        summary = window.get("summary") or {}
        best_path = (window.get("by_path_bucket") or [{}])[0]
        worst_edge = sorted(
            window.get("by_edge_bucket") or [],
            key=lambda row: as_float(row.get("net_cents")) or 0.0,
        )
        notes.append(
            f"{window.get('window')}: lead entries/settled/coverage/net "
            f"{summary.get('entries')}/{summary.get('settled')}/{summary.get('coverage_pct')}/{summary.get('net_cents')}c."
        )
        if best_path:
            notes.append(
                f"Best path bucket is {best_path.get('bucket')} with {best_path.get('settled')} settled and {best_path.get('net_cents')}c."
            )
        if worst_edge:
            notes.append(
                f"Worst edge bucket is {worst_edge[0].get('bucket')} with {worst_edge[0].get('settled')} settled and {worst_edge[0].get('net_cents')}c."
            )
    notes.append("Diagnostic windows can explain direction only; post-freeze rows decide whether the idea survives.")
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
    lines = [
        "# v28 Book Dislocation Regime Attribution",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Lead candidate: `{report.get('lead_score_name')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        summary = window.get("summary") or {}
        lines.extend([
            "",
            f"## {window.get('window')}",
            "",
            f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
            f"- Summary entries/settled/coverage/net: `{summary.get('entries')}/{summary.get('settled')}/{fmt(summary.get('coverage_pct'))}/{fmt(summary.get('net_cents'))}c`",
            "",
        ])
        for title, key in [
            ("Edge Buckets", "by_edge_bucket"),
            ("Ask-Move Buckets", "by_ask_move_bucket"),
            ("Path Buckets", "by_path_bucket"),
            ("Combined Buckets", "by_book_dislocation_bucket"),
        ]:
            lines.extend([
                f"### {title}",
                "",
                "| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ])
            for row in window.get(key) or []:
                lines.append(
                    f"| `{row.get('bucket')}` | {row.get('entries')} | {row.get('settled')} | "
                    f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
                    f"{fmt(row.get('avg_net_cents'))} | {fmt(row.get('avg_edge'))} | "
                    f"{fmt(row.get('avg_escape_energy'))} | {row.get('approved_entries')}/{row.get('reconstructed_entries')} |"
                )
            lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
