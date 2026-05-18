"""Boundary-entropy FV diagnostics for the v28 target-coverage surface.

Research-only; no live bot changes or orders.

Physics hypothesis:
    Near the strike, early in the 15m window, high recross heat means the path is
    not "decided" even when raw v28 shows an apparent edge.  The fair value
    should retain more entropy: shrink the selected-side probability toward
    either 50/50 or the executable book prior in proportion to boundary heat.

This is deliberately a small family of smooth transforms, not a fitted model.
If one looks useful, it must be frozen and validated on future rows before it
can matter.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    DEFAULT_POLICY,
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_entropy_fv_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_entropy_fv_latest.md"

POLICY = DEFAULT_POLICY
ENTRY_FLOORS = [0.0, 0.01, 0.02, 0.04]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def raw_p(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def ask_prob(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("ask_prob"))
    if value is not None:
        return value
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def outcome(row: dict[str, Any]) -> float | None:
    won = row.get("side_won")
    if won is True:
        return 1.0
    if won is False:
        return 0.0
    return None


def net_cents(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_gross_cents_after_entry_fee")) or 0.0)


def logloss(p: float, y: float) -> float:
    p = clamp_prob(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def boundary_heat(row: dict[str, Any], *, side_boost: bool = False) -> float:
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    stc = as_float(row.get("seconds_to_close"))
    if recross is None or abs_d is None or stc is None:
        return 0.0
    recross_term = max(0.0, min(1.25, recross))
    boundary_term = math.exp(-((abs_d / 0.45) ** 2))
    clock_term = math.sqrt(max(0.0, min(900.0, stc)) / 900.0)
    heat = recross_term * boundary_term * clock_term
    if side_boost and str(row.get("side") or "").lower() == "no":
        p = raw_p(row)
        if 0.60 <= p < 0.70:
            heat *= 1.35
    return max(0.0, min(1.0, heat))


def shrink_to_50(row: dict[str, Any], scale: float, *, side_boost: bool = False) -> float:
    p = raw_p(row)
    heat = min(1.0, scale * boundary_heat(row, side_boost=side_boost))
    return clamp_prob(p + heat * (0.5 - p))


def shrink_to_book(row: dict[str, Any], scale: float, *, side_boost: bool = False) -> float:
    p = raw_p(row)
    book = ask_prob(row)
    if book is None:
        return shrink_to_50(row, scale, side_boost=side_boost)
    heat = min(1.0, scale * boundary_heat(row, side_boost=side_boost))
    return clamp_prob(p + heat * (book - p))


def variants() -> dict[str, Callable[[dict[str, Any]], float]]:
    return {
        "raw_probability": raw_p,
        "entropy50_s50": lambda row: shrink_to_50(row, 0.50),
        "entropy50_s75": lambda row: shrink_to_50(row, 0.75),
        "entropy50_s100": lambda row: shrink_to_50(row, 1.00),
        "entropy50_no_mid_s75": lambda row: shrink_to_50(row, 0.75, side_boost=True),
        "entropy_book_s50": lambda row: shrink_to_book(row, 0.50),
        "entropy_book_s75": lambda row: shrink_to_book(row, 0.75),
        "entropy_book_s100": lambda row: shrink_to_book(row, 1.00),
        "entropy_book_no_mid_s75": lambda row: shrink_to_book(row, 0.75, side_boost=True),
    }


def forward_rows() -> tuple[list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    selected = apply_policy(selected_base_rows(), str(target_state.get("policy") or POLICY))
    rows = [row for row in selected if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def score_variant(name: str, fn: Callable[[dict[str, Any]], float], rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    scored = []
    adjusted = 0
    heat_values = []
    for row in rows:
        y = outcome(row)
        if y is None:
            continue
        p0 = raw_p(row)
        p = fn(row)
        heat = boundary_heat(row, side_boost="no_mid" in name)
        heat_values.append(heat)
        if abs(p - p0) > 1e-9:
            adjusted += 1
        scored.append({
            "row": row,
            "p": p,
            "raw_p": p0,
            "outcome": y,
            "brier": (p - y) ** 2,
            "raw_brier": (p0 - y) ** 2,
            "logloss": logloss(p, y),
            "raw_logloss": logloss(p0, y),
        })
    brier = avg([item["brier"] for item in scored])
    raw_brier = avg([item["raw_brier"] for item in scored])
    loss = avg([item["logloss"] for item in scored])
    raw_loss = avg([item["raw_logloss"] for item in scored])
    return {
        "variant": name,
        "entries": len(rows),
        "settled": len(scored),
        "wins": sum(1 for item in scored if item["outcome"] == 1.0),
        "losses": sum(1 for item in scored if item["outcome"] == 0.0),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "adjusted_rows": adjusted,
        "avg_heat": avg(heat_values),
        "avg_brier": brier,
        "avg_logloss": loss,
        "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
        "logloss_delta_vs_raw": None if loss is None or raw_loss is None else loss - raw_loss,
        "net_cents": sum(net_cents(item["row"]) for item in scored),
        "entry_bridges": entry_bridges(name, fn, rows, denominator),
    }


def entry_bridges(name: str, fn: Callable[[dict[str, Any]], float], rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    out = []
    for floor in ENTRY_FLOORS:
        kept = []
        skipped = []
        for row in rows:
            ask = ask_prob(row)
            if ask is None:
                skipped.append(row)
                continue
            edge = fn(row) - ask
            if edge >= floor:
                kept.append(row)
            else:
                skipped.append(row)
        settled = [row for row in kept if outcome(row) is not None]
        skipped_settled = [row for row in skipped if outcome(row) is not None]
        out.append({
            "variant": name,
            "edge_floor": floor,
            "entries": len(kept),
            "settled": len(settled),
            "wins": sum(1 for row in settled if outcome(row) == 1.0),
            "losses": sum(1 for row in settled if outcome(row) == 0.0),
            "coverage_pct": 100.0 * len(kept) / denominator if denominator else None,
            "net_cents": sum(net_cents(row) for row in settled),
            "skipped": len(skipped),
            "skipped_settled": len(skipped_settled),
            "skipped_net_cents": sum(net_cents(row) for row in skipped_settled),
        })
    return out


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    scored = [score_variant(name, fn, rows, denominator) for name, fn in variants().items()]
    ranked_fv = sorted(
        scored,
        key=lambda row: (
            float(row.get("brier_delta_vs_raw") if row.get("brier_delta_vs_raw") is not None else 999.0),
            float(row.get("logloss_delta_vs_raw") if row.get("logloss_delta_vs_raw") is not None else 999.0),
        ),
    )
    bridges = [bridge for row in scored for bridge in row.get("entry_bridges") or []]
    target_bridges = [
        row for row in bridges
        if (as_float(row.get("coverage_pct")) is not None and 75.0 <= float(row.get("coverage_pct")) <= 90.0)
    ]
    ranked_bridges = sorted(
        target_bridges,
        key=lambda row: float(row.get("net_cents") if row.get("net_cents") is not None else -999999.0),
        reverse=True,
    )
    return {
        "policy": POLICY,
        "forward_denominator": denominator,
        "rows": len(rows),
        "ranked_fv": ranked_fv,
        "ranked_target_coverage_entry_bridges": ranked_bridges,
        "interpretation": interpretation(ranked_fv, ranked_bridges),
    }


def interpretation(ranked_fv: list[dict[str, Any]], ranked_bridges: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Boundary-entropy variants are diagnostic only and must be frozen before forward promotion.",
    ]
    best_fv = ranked_fv[0] if ranked_fv else {}
    if best_fv:
        notes.append(
            f"Best FV variant is {best_fv.get('variant')} with Brier/logloss deltas {best_fv.get('brier_delta_vs_raw')}/{best_fv.get('logloss_delta_vs_raw')} over {best_fv.get('settled')} settled rows."
        )
    best_bridge = ranked_bridges[0] if ranked_bridges else {}
    if best_bridge:
        notes.append(
            f"Best target-coverage entry bridge is {best_bridge.get('variant')} floor {best_bridge.get('edge_floor')} with coverage {best_bridge.get('coverage_pct')} and net {best_bridge.get('net_cents')}c."
        )
    else:
        notes.append("No boundary-entropy bridge currently lands in the 75-90% coverage band.")
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
        "# v28 Boundary-Entropy FV Diagnostic",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Rows: `{report.get('rows')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## FV Ranking",
        "",
        "| variant | settled | adjusted | avg heat | Brier d | logloss d | net c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("ranked_fv") or []:
        lines.append(
            f"| `{row.get('variant')}` | {row.get('settled')} | {row.get('adjusted_rows')} | "
            f"{fmt(row.get('avg_heat'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('logloss_delta_vs_raw'))} | {fmt(row.get('net_cents'))} |"
        )
    lines.extend([
        "",
        "## Target-Coverage Entry Bridges",
        "",
        "| variant | floor | entries | settled | W/L | coverage | net c | skipped net c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("ranked_target_coverage_entry_bridges") or []:
        lines.append(
            f"| `{row.get('variant')}` | {fmt(row.get('edge_floor'))} | {row.get('entries')} | "
            f"{row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('skipped_net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
