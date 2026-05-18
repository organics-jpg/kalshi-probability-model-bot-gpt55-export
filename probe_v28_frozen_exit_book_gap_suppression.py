"""Frozen forward challenger for v28 soft-exit book-gap suppression.

Research-only; no live bot changes or orders.

Physics hypothesis:
    A v28 soft exit should not fire just because the executable exit bid is
    temporarily poor while the held-side thesis is still alive. If p_hold is
    high, or p_hold exceeds the exit bid by a large enough gap, the exit is
    probably paying spread/turbulence instead of reducing real settlement risk.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import (
    exit_bid_prob,
    exit_reason,
    fair_drawdown,
    hold_book_gap,
    is_soft_exit,
    p_hold,
)
from probe_v28_exit_policy_candidates import build_rows, current_exit, hold_to_settlement, side_won
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.md"

MIN_SETTLED = 30
GAP_FLOOR = 0.15
P_HOLD_FLOOR = 0.75


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "suppress_soft_gap15_or_p_hold75",
        "gap_floor": GAP_FLOOR,
        "p_hold_floor": P_HOLD_FLOOR,
        "rule": (
            "If exit reason is mushroom_v28_exit_value_over_hold or "
            "mushroom_v28_probability_reduce, hold to settlement when "
            "p_hold - exit_bid >= 0.15 or p_hold >= 0.75; otherwise keep "
            "current v28 exit. Do not suppress probability_collapse_full."
        ),
        "physics": (
            "Soft exits are allowed to be noisy spread/turbulence events; "
            "collapse exits remain operational/model risk exits."
        ),
        "source_artifact": "v28_exit_book_gap_candidates_latest.json",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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
    rows = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def should_suppress(row: dict[str, Any], gap_floor: float, p_floor: float) -> bool:
    if not is_soft_exit(row):
        return False
    gap = hold_book_gap(row)
    p = p_hold(row)
    return (gap is not None and gap >= gap_floor) or (p is not None and p >= p_floor)


def candidate_gross(row: dict[str, Any], gap_floor: float, p_floor: float) -> float | None:
    if should_suppress(row, gap_floor, p_floor):
        return hold_to_settlement(row)
    return current_exit(row)


def summarize(rows: list[dict[str, Any]], gap_floor: float, p_floor: float) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, gap_floor, p_floor)
        if cur is None or cand is None:
            continue
        current_vals.append(float(cur))
        candidate_vals.append(float(cand))
        if should_suppress(row, gap_floor, p_floor):
            suppressed.append(row)
    current_gross = sum(current_vals)
    candidate_gross_cents = sum(candidate_vals)
    loss_cost = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is False
    )
    winner_recovery = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is True
    )
    return {
        "rows": len(rows),
        "settled": len(candidate_vals),
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross_cents,
        "delta_vs_current_cents": candidate_gross_cents - current_gross,
        "current_wins": sum(1 for value in current_vals if value >= 0.0),
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "candidate_wins": sum(1 for value in candidate_vals if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "suppressed_exits": len(suppressed),
        "winner_clip_recovered_cents": winner_recovery,
        "loss_control_cost_cents": loss_cost,
    }


def detail_rows(rows: list[dict[str, Any]], gap_floor: float, p_floor: float) -> list[dict[str, Any]]:
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    out = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, gap_floor, p_floor)
        if cur is None or cand is None:
            continue
        path = path_by_market.get(str(row.get("market"))) or {}
        suppressed = should_suppress(row, gap_floor, p_floor)
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "exit_ts": row.get("exit_ts"),
            "entry_cents": row.get("entry_cents"),
            "exit_cents": row.get("exit_cents"),
            "exit_reason": exit_reason(row),
            "p_hold": p_hold(row),
            "exit_bid_prob": exit_bid_prob(row),
            "hold_book_gap": hold_book_gap(row),
            "fair_drawdown_cents": fair_drawdown(row),
            "current_cents": cur,
            "hold_cents": hold_to_settlement(row),
            "candidate_cents": cand,
            "delta_cents": float(cand) - float(cur),
            "suppressed": suppressed,
            "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
        })
    out.sort(key=lambda row: str(row.get("exit_ts") or row.get("entry_ts") or ""))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    gap_floor = float(state.get("gap_floor") or GAP_FLOOR)
    p_floor = float(state.get("p_hold_floor") or P_HOLD_FLOOR)
    rows = future_rows(str(state["freeze_ts_utc"]))
    summary = summarize(rows, gap_floor, p_floor)
    blockers = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        blockers.append("delta_not_positive")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        blockers.append("suppressed_loss_control_cost_negative")
    return {
        "freeze": state,
        "summary": summary,
        "rows": detail_rows(rows, gap_floor, p_floor),
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "interpretation": [
            f"Frozen soft-exit book-gap candidate has {summary.get('settled')} settled future rows.",
            f"Delta versus current v28 exits is {summary.get('delta_vs_current_cents')}c.",
            f"Suppressed exits: {summary.get('suppressed_exits')}; winner recovery {summary.get('winner_clip_recovered_cents')}c; loss-control cost {summary.get('loss_control_cost_cents')}c.",
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
    summary = report.get("summary") or {}
    lines = [
        "# v28 Frozen Exit Book-Gap Suppression",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future rows/settled: `{summary.get('rows')}/{summary.get('settled')}`",
        f"- Current/candidate gross: `{summary.get('current_gross_cents')}c/{summary.get('candidate_gross_cents')}c`",
        f"- Delta vs current: `{summary.get('delta_vs_current_cents')}c`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | result | entry | exit | reason | p_hold | bid | gap | drawdown | current c | hold c | candidate c | delta c | suppressed | worst hold mark |",
        "|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{row.get('entry_cents')} | {row.get('exit_cents')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('exit_bid_prob'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {row.get('current_cents')} | {row.get('hold_cents')} | "
            f"{row.get('candidate_cents')} | {fmt(row.get('delta_cents'))} | {row.get('suppressed')} | "
            f"{row.get('worst_post_exit_hold_mark_cents')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
