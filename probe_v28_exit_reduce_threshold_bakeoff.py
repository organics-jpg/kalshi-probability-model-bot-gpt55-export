"""Threshold bakeoff for v28 probability-reduce exit suppression.

Research-only; no live bot changes or orders.

This report stress-tests the frozen 0.75 probability-reduce suppression rule
against nearby thresholds. The goal is to avoid a brittle threshold chosen to
catch one recent winner; a good threshold should have a broad physical plateau
and should not buy winner recovery by reopening large losing holds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    hold_to_settlement,
    is_probability_reduce,
    side_won,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_reduce_threshold_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_threshold_bakeoff_latest.md"

THRESHOLDS = [0.68, 0.70, 0.72, 0.74, 0.75, 0.76, 0.78, 0.80]
FROZEN_THRESHOLD = 0.75


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def candidate_value(row: dict[str, Any], threshold: float) -> float | None:
    current = current_exit(row)
    p_hold = exit_p_hold(row)
    if current is None:
        return None
    if is_probability_reduce(row) and p_hold is not None and p_hold >= threshold:
        return hold_to_settlement(row)
    return current


def threshold_summary(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    current_values = []
    candidate_values = []
    suppressed = []
    for row in rows:
        current = current_exit(row)
        candidate = candidate_value(row, threshold)
        if current is None or candidate is None:
            continue
        current_values.append(float(current))
        candidate_values.append(float(candidate))
        p_hold = exit_p_hold(row)
        if is_probability_reduce(row) and p_hold is not None and p_hold >= threshold:
            suppressed.append(row)
    current_gross = sum(current_values)
    candidate_gross = sum(candidate_values)
    winner_recovery = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is True
    )
    loss_cost = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is False
    )
    return {
        "threshold": threshold,
        "rows": len(candidate_values),
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross,
        "delta_vs_current_cents": candidate_gross - current_gross,
        "candidate_wins": sum(1 for value in candidate_values if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_values if value < 0.0),
        "suppressed_exits": len(suppressed),
        "suppressed_winners": sum(1 for row in suppressed if side_won(row) is True),
        "suppressed_losers": sum(1 for row in suppressed if side_won(row) is False),
        "winner_recovery_cents": winner_recovery,
        "loss_control_cost_cents": loss_cost,
        "net_recovery_after_loss_cost_cents": winner_recovery + loss_cost,
        "suppressed_markets": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "result": row.get("result"),
                "entry_cents": row.get("entry_cents"),
                "exit_cents": row.get("exit_cents"),
                "current_cents": current_exit(row),
                "hold_cents": hold_to_settlement(row),
                "delta_cents": None
                if current_exit(row) is None or hold_to_settlement(row) is None
                else float(hold_to_settlement(row)) - float(current_exit(row)),
                "p_hold": exit_p_hold(row),
                "fair_drawdown_cents": exit_fair_drawdown(row),
                "side_won": side_won(row),
            }
            for row in suppressed
        ],
    }


def robust_plateau(summary_rows: list[dict[str, Any]]) -> list[str]:
    notes = []
    best = max(summary_rows, key=lambda row: float(row.get("delta_vs_current_cents") or 0.0), default={})
    frozen = next((row for row in summary_rows if row.get("threshold") == FROZEN_THRESHOLD), {})
    if best:
        notes.append(
            f"Best threshold by gross delta is {best.get('threshold')} with {best.get('delta_vs_current_cents')}c versus current."
        )
    if frozen:
        notes.append(
            f"Frozen threshold {FROZEN_THRESHOLD} has {frozen.get('delta_vs_current_cents')}c delta, {frozen.get('suppressed_winners')} suppressed winners, and {frozen.get('suppressed_losers')} suppressed losers."
        )
        if float(frozen.get("loss_control_cost_cents") or 0.0) == 0.0:
            notes.append("At 0.75, the diagnostic sample recovers winner clips without suppressing any losing probability-reduce exits.")
    low = next((row for row in summary_rows if row.get("threshold") == 0.74), {})
    if low and frozen:
        notes.append(
            f"Lowering to 0.74 would change delta by {float(low.get('delta_vs_current_cents') or 0.0) - float(frozen.get('delta_vs_current_cents') or 0.0)}c and introduces {low.get('suppressed_losers')} suppressed losers."
        )
    return notes


def build_report() -> dict[str, Any]:
    rows = build_rows()
    summaries = [threshold_summary(rows, threshold) for threshold in THRESHOLDS]
    summaries.sort(key=lambda row: float(row.get("delta_vs_current_cents") or 0.0), reverse=True)
    return {
        "surface": "settled_v28_trades_with_counterfactual_hold",
        "thresholds": THRESHOLDS,
        "frozen_threshold": FROZEN_THRESHOLD,
        "summaries": summaries,
        "interpretation": robust_plateau(summaries),
    }


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
        "# v28 Exit Reduce Threshold Bakeoff",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Frozen threshold: `{report.get('frozen_threshold')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Thresholds",
        "",
        "| threshold | rows | gross c | delta c | W/L | suppressed | suppressed W/L | winner recovery c | loss cost c | net recovery c |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("summaries") or []:
        lines.append(
            f"| {fmt(row.get('threshold'))} | {row.get('rows')} | {fmt(row.get('candidate_gross_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('candidate_wins')}/{row.get('candidate_losses')} | "
            f"{row.get('suppressed_exits')} | {row.get('suppressed_winners')}/{row.get('suppressed_losers')} | "
            f"{fmt(row.get('winner_recovery_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"{fmt(row.get('net_recovery_after_loss_cost_cents'))} |"
        )
    frozen = next((row for row in report.get("summaries") or [] if row.get("threshold") == FROZEN_THRESHOLD), {})
    if frozen:
        lines.extend([
            "",
            "## Frozen Threshold Suppressed Rows",
            "",
            "| market | side | result | entry | exit | current c | hold c | delta c | p_hold | drawdown |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in frozen.get("suppressed_markets") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
                f"{row.get('entry_cents')} | {row.get('exit_cents')} | {row.get('current_cents')} | "
                f"{row.get('hold_cents')} | {fmt(row.get('delta_cents'))} | {fmt(row.get('p_hold'))} | "
                f"{fmt(row.get('fair_drawdown_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
