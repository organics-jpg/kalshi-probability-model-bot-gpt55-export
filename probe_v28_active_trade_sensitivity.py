"""Active v28 trade sensitivity report.

Research-only; no live bot changes or orders.

Shows unresolved v28 trades, their locked/realized exit P&L if already exited,
their hold-to-settlement sensitivity, and whether frozen state/FV candidates
would have changed the entry probability or kept/skipped the entry.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_book_disagreement_trajectory_fv import VARIANTS
from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_active_trade_sensitivity_latest.json"
OUT_MD = OUT_DIR / "v28_active_trade_sensitivity_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def entry_row(score: dict[str, Any]) -> dict[str, Any]:
    features = score.get("entry_features") if isinstance(score.get("entry_features"), dict) else {}
    ask = as_float(features.get("mushroom_v28_ask_cents") or score.get("entry_cents"))
    p_side = as_float(features.get("mushroom_v28_p_side"))
    return {
        "market": score.get("market"),
        "side": score.get("side"),
        "p_side": p_side,
        "ask_prob": None if ask is None else ask / 100.0,
        "ask_cents": ask,
        "book_delta_vs_prior_same_side": None,
    }


def hold_gross_if(score: dict[str, Any], result: str) -> float | None:
    side = str(score.get("side") or "").lower()
    entry = as_float(score.get("entry_cents"))
    qty = as_float(score.get("qty")) or 1.0
    if side not in {"yes", "no"} or result not in {"yes", "no"} or entry is None:
        return None
    return (100.0 - entry) * qty if result == side else -entry * qty


def raw_book_gap(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_cents"))
    return None if p is None or ask is None else p - ask / 100.0


def state_valve_keep(row: dict[str, Any], same_side_prior_count: int) -> bool:
    if same_side_prior_count <= 0:
        return True
    gap = raw_book_gap(row)
    return gap is None or gap <= 0.15


def active_rows() -> list[dict[str, Any]]:
    scored = [score_trade(trade) for trade in reconstruct_trades(read_events())]
    out = []
    for score in scored:
        if str(score.get("result") or "").lower() in {"yes", "no"}:
            continue
        row = entry_row(score)
        if row.get("p_side") is None or row.get("ask_prob") is None:
            raw_p = None
            candidate_p = None
        else:
            raw_p = float(VARIANTS["raw_probability"](row))
            candidate_p = float(VARIANTS["gap15_or_drawdown10"](row))
        same_side_prior = sum(
            1
            for prior in scored
            if prior is not score
            and str(prior.get("market")) == str(score.get("market"))
            and str(prior.get("side")) == str(score.get("side"))
            and str(prior.get("entry_ts") or "") < str(score.get("entry_ts") or "")
        )
        yes_hold = hold_gross_if(score, "yes")
        no_hold = hold_gross_if(score, "no")
        actual = as_float(score.get("actual_gross_cents"))
        out.append({
            "market": score.get("market"),
            "side": score.get("side"),
            "qty": score.get("qty"),
            "entry_cents": score.get("entry_cents"),
            "exit_cents": score.get("exit_cents"),
            "status": score.get("status"),
            "entry_ts": score.get("entry_ts"),
            "exit_ts": score.get("exit_ts"),
            "actual_or_locked_gross_cents": actual,
            "hold_if_yes_cents": yes_hold,
            "hold_if_no_cents": no_hold,
            "exit_value_if_yes_cents": None if actual is None or yes_hold is None else actual - yes_hold,
            "exit_value_if_no_cents": None if actual is None or no_hold is None else actual - no_hold,
            "raw_probability": raw_p,
            "book_trajectory_probability": candidate_p,
            "probability_delta": None if raw_p is None or candidate_p is None else candidate_p - raw_p,
            "ask_prob": row.get("ask_prob"),
            "raw_book_gap": raw_book_gap(row),
            "same_side_prior_count": same_side_prior,
            "state_valve_keep": state_valve_keep(row, same_side_prior),
            "exit_reason": score.get("exit_features", {}).get("mushroom_v28_exit_reason") if isinstance(score.get("exit_features"), dict) else score.get("exit_reason"),
            "exit_p_hold": score.get("exit_features", {}).get("mushroom_v28_p_hold") if isinstance(score.get("exit_features"), dict) else None,
            "exit_bid_cents": score.get("exit_features", {}).get("mushroom_v28_exit_bid_cents") if isinstance(score.get("exit_features"), dict) else None,
        })
    return out


def build_report() -> dict[str, Any]:
    rows = active_rows()
    return {
        "active_count": len(rows),
        "rows": rows,
        "interpretation": current_read(rows),
    }


def current_read(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No unresolved v28 trades currently reconstructed."]
    notes = []
    for row in rows:
        notes.append(
            f"{row.get('market')} {row.get('side')} locked/current {row.get('actual_or_locked_gross_cents')}c; hold if YES/NO {row.get('hold_if_yes_cents')}/{row.get('hold_if_no_cents')}c; state valve keep {row.get('state_valve_keep')}; FV delta {row.get('probability_delta')}."
        )
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
        "# v28 Active Trade Sensitivity",
        "",
        f"- Active/unresolved trades: `{report.get('active_count')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | entry | exit | locked c | hold yes | hold no | exit val yes | exit val no | raw p | traj p | gap | state keep | exit reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {row.get('entry_cents')} | {row.get('exit_cents')} | "
            f"{fmt(row.get('actual_or_locked_gross_cents'))} | {fmt(row.get('hold_if_yes_cents'))} | {fmt(row.get('hold_if_no_cents'))} | "
            f"{fmt(row.get('exit_value_if_yes_cents'))} | {fmt(row.get('exit_value_if_no_cents'))} | "
            f"{fmt(row.get('raw_probability'))} | {fmt(row.get('book_trajectory_probability'))} | {fmt(row.get('raw_book_gap'))} | "
            f"{row.get('state_valve_keep')} | `{row.get('exit_reason')}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
