"""Boundary-clock probability overlays for the v28 target surface.

Research-only; no live bot changes or orders.

This converts the boundary-clock entry finding into FV-model language. Instead
of skipping rows, hazard rows have their confidence shrunk toward 50, with a
few fixed shrink strengths. This tests whether the physics improves probability
accuracy before it is considered as an entry gate.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_hazard_repair import clock_composite
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import (
    STATE_JSON as COVERAGE_STATE_JSON,
    selected_base_rows,
)
from probe_v28_target_coverage_fv_overlay_validator import (
    DEFAULT_POLICY,
    apply_policy,
    as_float,
    clamp_prob,
    load_json,
    logloss,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_fv_overlay_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_fv_overlay_latest.md"

POLICY = DEFAULT_POLICY


def raw_prob(row: dict[str, Any]) -> float:
    raw = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if raw is None:
        raise ValueError("missing raw probability")
    return clamp_prob(raw)


def shrink_prob(row: dict[str, Any], scale: float) -> float:
    raw = raw_prob(row)
    if not clock_composite(row):
        return raw
    return clamp_prob(0.5 + scale * (raw - 0.5))


def book_blend_prob(row: dict[str, Any], book_weight: float) -> float:
    raw = raw_prob(row)
    if not clock_composite(row):
        return raw
    book = as_float(row.get("ask_prob"))
    if book is None:
        return raw
    return clamp_prob((1.0 - book_weight) * raw + book_weight * book)


def overlay_fns() -> dict[str, Callable[[dict[str, Any]], float]]:
    return {
        "raw_probability": raw_prob,
        "clock_shrink_0p00": lambda row: shrink_prob(row, 0.0),
        "clock_shrink_0p25": lambda row: shrink_prob(row, 0.25),
        "clock_shrink_0p50": lambda row: shrink_prob(row, 0.50),
        "clock_shrink_0p75": lambda row: shrink_prob(row, 0.75),
        "clock_book_blend_0p50": lambda row: book_blend_prob(row, 0.50),
        "clock_book_blend_1p00": lambda row: book_blend_prob(row, 1.00),
    }


def forward_rows() -> tuple[list[dict[str, Any]], int]:
    source_state = load_json(COVERAGE_STATE_JSON)
    freeze_dt = parse_ts(source_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    target = apply_policy(selected_base_rows(), POLICY)
    rows = [row for row in target if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def score_rows(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    adjusted = 0
    hazard_settled = 0
    for row in settled:
        try:
            p = fn(row)
            raw = raw_prob(row)
        except (TypeError, ValueError):
            continue
        if abs(p - raw) > 1e-12:
            adjusted += 1
        if clock_composite(row):
            hazard_settled += 1
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "p": p,
            "raw": raw,
            "outcome": outcome,
            "brier": (p - outcome) ** 2,
            "raw_brier": (raw - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "raw_logloss": logloss(raw, outcome),
        })
    brier = avg([row["brier"] for row in scored])
    raw_brier = avg([row["raw_brier"] for row in scored])
    loss = avg([row["logloss"] for row in scored])
    raw_loss = avg([row["raw_logloss"] for row in scored])
    net = sum(float(as_float(row.get("net_gross_cents_after_entry_fee")) or 0.0) for row in settled)
    return {
        "overlay": name,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "hazard_settled": hazard_settled,
        "adjusted_rows": adjusted,
        "avg_brier": brier,
        "avg_logloss": loss,
        "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
        "logloss_delta_vs_raw": None if loss is None or raw_loss is None else loss - raw_loss,
        "net_cents": net,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def row_detail(row: dict[str, Any], best_fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    raw = raw_prob(row)
    adjusted = best_fn(row)
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "raw_p": raw,
        "adjusted_p": adjusted,
        "delta_p": adjusted - raw,
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "clock_composite": clock_composite(row),
    }


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    fns = overlay_fns()
    ranked = [score_rows(rows, name, fn, denominator) for name, fn in fns.items()]
    ranked.sort(key=lambda row: (
        float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
        float(row.get("avg_logloss") if row.get("avg_logloss") is not None else 999.0),
    ))
    best_name = ranked[0]["overlay"] if ranked else "raw_probability"
    best_fn = fns.get(str(best_name), raw_prob)
    hazard_rows = [row for row in rows if row.get("side_won") is not None and clock_composite(row)]
    return {
        "diagnostic": "boundary_clock_fv_overlay",
        "policy": POLICY,
        "forward_denominator": denominator,
        "ranked": ranked,
        "best_overlay": best_name,
        "hazard_rows": [row_detail(row, best_fn) for row in hazard_rows],
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return ["No rows available."]
    best = ranked[0]
    return [
        f"Best boundary-clock FV overlay is {best.get('overlay')} with Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}.",
        f"It adjusts {best.get('adjusted_rows')} settled rows out of {best.get('settled')} on the target surface.",
        "This is diagnostic only until frozen future validation exists.",
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
        "# v28 Boundary-Clock FV Overlay",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Best overlay: `{report.get('best_overlay')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | overlay | settled | W/L | adjusted | hazard settled | brier d | logloss d | net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{row.get('adjusted_rows')} | {row.get('hazard_settled')} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('logloss_delta_vs_raw'))} | {fmt(row.get('net_cents'))} |"
        )
    lines.extend([
        "",
        "## Hazard Rows Under Best Overlay",
        "",
        "| market | source | side | won | net c | raw p | adj p | d p | ask | edge | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("hazard_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | "
            f"{fmt(row.get('delta_p'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
