"""Entry projection for book-trajectory FV overlays.

Research-only; no live bot changes or orders.

Tests whether the trajectory FV improvement can translate into broad entry
economics. Policies are fixed, simple surfaces around the live v28 constraints:
first qualifying side per market, ask <=90c, 0-600 seconds to close, and
candidate probability/edge thresholds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_book_disagreement_trajectory_fv import (
    VARIANTS,
    observation_events,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_book_trajectory_entry_projection_latest.json"
OUT_MD = OUT_DIR / "v28_book_trajectory_entry_projection_latest.md"

MAX_ASK = 0.90
MIN_STC = 0.0
MAX_STC = 600.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def selected_rows(rows: list[dict[str, Any]], variant: str, min_p: float, min_edge: float) -> list[dict[str, Any]]:
    fn = VARIANTS[variant]
    selected_by_market: dict[str, dict[str, Any]] = {}
    for row in rows:
        market = str(row.get("market") or "")
        if market in selected_by_market:
            continue
        ask = as_float(row.get("ask_prob"))
        stc = as_float(row.get("seconds_to_close"))
        if ask is None or ask > MAX_ASK:
            continue
        if stc is None or stc < MIN_STC or stc > MAX_STC:
            continue
        p_eff = float(fn(row))
        edge = p_eff - ask
        if p_eff < min_p or edge < min_edge:
            continue
        out = dict(row)
        out["p_eff"] = p_eff
        out["edge_eff"] = edge
        out["policy_variant"] = variant
        selected_by_market[market] = out
    return list(selected_by_market.values())


def score(rows: list[dict[str, Any]], variant: str, min_p: float, min_edge: float, denominator: int) -> dict[str, Any]:
    selected = selected_rows(rows, variant, min_p, min_edge)
    gross = sum((1.0 - float(row["ask_prob"])) * 100.0 if row.get("side_won") is True else -float(row["ask_prob"]) * 100.0 for row in selected)
    return {
        "policy": f"{variant}_p{int(min_p * 100)}_edge{int(min_edge * 100)}",
        "variant": variant,
        "min_p": min_p,
        "min_edge": min_edge,
        "entries": len(selected),
        "settled": len(selected),
        "wins": sum(1 for row in selected if row.get("side_won") is True),
        "losses": sum(1 for row in selected if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(selected) / denominator if denominator else None,
        "gross_cents": gross,
        "avg_p_eff": avg([float(row["p_eff"]) for row in selected]),
        "avg_ask": avg([float(row["ask_prob"]) for row in selected]),
        "avg_edge": avg([float(row["edge_eff"]) for row in selected]),
        "selected_markets": [row.get("market") for row in selected],
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def overlap_delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    cand_markets = set(candidate.get("selected_markets") or [])
    base_markets = set(baseline.get("selected_markets") or [])
    return {
        "candidate": candidate.get("policy"),
        "baseline": baseline.get("policy"),
        "overlap_markets": len(cand_markets & base_markets),
        "candidate_only_markets": len(cand_markets - base_markets),
        "baseline_only_markets": len(base_markets - cand_markets),
    }


def build_report() -> dict[str, Any]:
    rows = observation_events()
    denominator = len({row.get("market") for row in rows})
    policies = [
        ("raw_probability", 0.50, 0.00),
        ("raw_probability", 0.52, 0.00),
        ("raw_probability", 0.60, 0.00),
        ("gap15_or_drawdown10", 0.50, 0.00),
        ("gap15_or_drawdown10", 0.52, 0.00),
        ("gap15_or_drawdown10", 0.60, 0.00),
        ("gap15_or_drawdown10", 0.60, 0.02),
        ("book_probability", 0.50, 0.00),
        ("book_probability", 0.52, 0.00),
    ]
    ranked = [score(rows, variant, min_p, min_edge, denominator) for variant, min_p, min_edge in policies]
    ranked.sort(key=lambda row: (target_coverage_rank(row), float(row.get("gross_cents") or -999999.0)), reverse=True)
    baseline = next((row for row in ranked if row.get("policy") == "raw_probability_p50_edge0"), {})
    return {
        "surface": "first_qualifying_observation_per_market",
        "constraints": {
            "max_ask": MAX_ASK,
            "min_seconds_to_close": MIN_STC,
            "max_seconds_to_close": MAX_STC,
        },
        "denominator_markets": denominator,
        "ranked": ranked,
        "overlap_vs_raw_p50": [overlap_delta(row, baseline) for row in ranked],
        "interpretation": current_read(ranked, baseline),
    }


def target_coverage_rank(row: dict[str, Any]) -> float:
    coverage = float(row.get("coverage_pct") or 0.0)
    if 75.0 <= coverage <= 90.0:
        return 2.0
    if 65.0 <= coverage < 75.0 or 90.0 < coverage <= 95.0:
        return 1.0
    return 0.0


def current_read(ranked: list[dict[str, Any]], baseline: dict[str, Any]) -> list[str]:
    target_rows = [row for row in ranked if 75.0 <= float(row.get("coverage_pct") or 0.0) <= 90.0]
    best_target = max(target_rows, key=lambda row: float(row.get("gross_cents") or -999999.0), default=None)
    notes = []
    if best_target:
        notes.append(
            f"Best 75-90% coverage row is {best_target['policy']} with coverage {best_target.get('coverage_pct')} and gross {best_target.get('gross_cents')}c."
        )
    if baseline:
        notes.append(
            f"Raw p50 baseline has coverage {baseline.get('coverage_pct')} and gross {baseline.get('gross_cents')}c."
        )
    notes.append("This is discovery-only because projected entries use observed shadow opportunities, not actual fills.")
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
        "# v28 Book-Trajectory Entry Projection",
        "",
        "Discovery-only first-qualifying-entry projection for trajectory-adjusted FV.",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Denominator markets: `{report.get('denominator_markets')}`",
        f"- Constraints: `{report.get('constraints')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranked Policies",
        "",
        "| rank | policy | entries | W/L | coverage | gross c | avg p | avg ask | avg edge |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('policy')}` | {row.get('entries')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('gross_cents'))} | "
            f"{fmt(row.get('avg_p_eff'))} | {fmt(row.get('avg_ask'))} | {fmt(row.get('avg_edge'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
