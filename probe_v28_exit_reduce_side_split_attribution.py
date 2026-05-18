"""Side-split attribution for v28 probability-reduce suppression.

Research-only; no live bot changes or orders.

This report is diagnostic, not a promotion gate. It explains whether the frozen
reduce-suppression signal is actually a side-specific phenomenon.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_p_hold,
    hold_to_settlement,
    is_probability_reduce,
    side_won,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_side_split_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_side_split_attribution_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    out = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        out.append(row)
    return out


def suppresses(row: dict[str, Any], side_filter: str | None, p_hold_floor: float) -> bool:
    p_hold = exit_p_hold(row)
    if not is_probability_reduce(row) or p_hold is None or p_hold < p_hold_floor:
        return False
    if side_filter is None:
        return True
    return str(row.get("side") or "").lower() == side_filter


def score_policy(rows: list[dict[str, Any]], policy: str, side_filter: str | None, p_hold_floor: float) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        hold = hold_to_settlement(row)
        if cur is None or hold is None:
            continue
        current_vals.append(float(cur))
        use_hold = suppresses(row, side_filter, p_hold_floor)
        candidate_vals.append(float(hold if use_hold else cur))
        if use_hold:
            suppressed.append(row)
    current_gross = sum(current_vals)
    candidate_gross = sum(candidate_vals)
    return {
        "policy": policy,
        "settled": len(candidate_vals),
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross,
        "delta_vs_current_cents": candidate_gross - current_gross,
        "suppressed": len(suppressed),
        "suppressed_yes": sum(1 for row in suppressed if str(row.get("side") or "").lower() == "yes"),
        "suppressed_no": sum(1 for row in suppressed if str(row.get("side") or "").lower() == "no"),
        "suppressed_winners": sum(1 for row in suppressed if side_won(row) is True),
        "suppressed_losers": sum(1 for row in suppressed if side_won(row) is False),
        "winner_recovery_cents": sum(
            float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
            for row in suppressed
            if side_won(row) is True
        ),
        "loss_control_cost_cents": sum(
            float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
            for row in suppressed
            if side_won(row) is False
        ),
    }


def suppressed_rows(rows: list[dict[str, Any]], p_hold_floor: float) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if not suppresses(row, None, p_hold_floor):
            continue
        cur = current_exit(row)
        hold = hold_to_settlement(row)
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "p_hold": exit_p_hold(row),
            "current_cents": cur,
            "hold_cents": hold,
            "delta_cents": None if cur is None or hold is None else float(hold) - float(cur),
        })
    return out


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    p_hold_floor = float(state.get("p_hold_floor") or 0.75)
    rows = future_rows(freeze_ts)
    policies = [
        score_policy(rows, "suppress_all_reduce_p_hold_ge_075", None, p_hold_floor),
        score_policy(rows, "suppress_yes_reduce_p_hold_ge_075", "yes", p_hold_floor),
        score_policy(rows, "suppress_no_reduce_p_hold_ge_075", "no", p_hold_floor),
    ]
    return {
        "freeze": state,
        "rows": len(rows),
        "policies": policies,
        "suppressed_rows": suppressed_rows(rows, p_hold_floor),
        "interpretation": [
            "If YES-only keeps most of the positive delta while NO-only is negative, the physical mechanism is side-asymmetric.",
            "A side-asymmetric read means the full two-sided exit patch should not be promoted from blended PnL.",
        ],
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
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Exit Reduce Side-Split Attribution",
        "",
        "Research-only: no live bot changes and no orders.",
        "",
        f"- Source freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Source candidate: `{freeze.get('candidate')}`",
        f"- Rows after source freeze: `{report.get('rows')}`",
        "",
        "## Policy Split",
        "",
        "| policy | settled | delta c | suppressed | yes/no suppressed | W/L suppressed | winner recovery | loss cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("policies") or []:
        lines.append(
            f"| {row.get('policy')} | {row.get('settled')} | {fmt(row.get('delta_vs_current_cents'))} | "
            f"{row.get('suppressed')} | {row.get('suppressed_yes')}/{row.get('suppressed_no')} | "
            f"{row.get('suppressed_winners')}/{row.get('suppressed_losers')} | "
            f"{fmt(row.get('winner_recovery_cents'))} | {fmt(row.get('loss_control_cost_cents'))} |"
        )
    lines.extend(["", "## Suppressed Rows", "", "| market | side | result | p_hold | current c | hold c | delta c |", "|---|---|---|---:|---:|---:|---:|"])
    for row in report.get("suppressed_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('current_cents'))} | "
            f"{fmt(row.get('hold_cents'))} | {fmt(row.get('delta_cents'))} |"
        )
    lines.extend(["", "## Interpretation", ""])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
