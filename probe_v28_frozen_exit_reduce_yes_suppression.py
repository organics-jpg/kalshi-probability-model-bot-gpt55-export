"""Frozen forward challenger for YES-only v28 probability-reduce suppression.

Research-only; no live bot changes or orders.

Physics hypothesis:
    The current forward reduce-suppression evidence is side-asymmetric: the
    suppressed exits that helped were YES-side exits. That says the broad rule
    is not proven for NO. This challenger freezes a narrower interpretation:
    only suppress probability_reduce exits when the held side is YES and the
    held-side thesis remains strong.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    side_won,
)
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.md"

MIN_SETTLED = 30
P_HOLD_FLOOR = 0.75
SIDE = "yes"


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
        "candidate": "suppress_yes_reduce_p_hold_ge_075",
        "side": SIDE,
        "p_hold_floor": P_HOLD_FLOOR,
        "rule": "If exit reason is mushroom_v28_probability_reduce, side is YES, and p_hold >= 0.75, score as held to settlement; otherwise keep current v28 exit.",
        "physics": "A YES-side high-probability reduce exit can be a turbulence clip; NO-side evidence is intentionally excluded until it earns its own forward proof.",
        "source": "Derived from the full reduce-suppression robustness profile, then frozen separately before promotion evidence.",
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


def should_suppress(row: dict[str, Any], side: str, p_hold_floor: float) -> bool:
    p_hold = exit_p_hold(row)
    return (
        is_probability_reduce(row)
        and str(row.get("side") or "").lower() == side
        and p_hold is not None
        and p_hold >= p_hold_floor
    )


def candidate_gross(row: dict[str, Any], side: str, p_hold_floor: float) -> float | None:
    if should_suppress(row, side, p_hold_floor):
        return hold_to_settlement(row)
    return current_exit(row)


def summarize(rows: list[dict[str, Any]], side: str, p_hold_floor: float) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, side, p_hold_floor)
        if cur is None or cand is None:
            continue
        current_vals.append(float(cur))
        candidate_vals.append(float(cand))
        if should_suppress(row, side, p_hold_floor):
            suppressed.append(row)
    current_gross = sum(current_vals)
    candidate_gross_cents = sum(candidate_vals)
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
        "suppressed_winners": sum(1 for row in suppressed if side_won(row) is True),
        "suppressed_losers": sum(1 for row in suppressed if side_won(row) is False),
        "winner_clip_recovered_cents": sum(
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


def detail_rows(rows: list[dict[str, Any]], side: str, p_hold_floor: float) -> list[dict[str, Any]]:
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    out = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, side, p_hold_floor)
        if cur is None or cand is None:
            continue
        path = path_by_market.get(str(row.get("market"))) or {}
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "exit_ts": row.get("exit_ts"),
            "entry_cents": row.get("entry_cents"),
            "exit_cents": row.get("exit_cents"),
            "exit_reason": exit_reason(row),
            "p_hold": exit_p_hold(row),
            "fair_drawdown_cents": exit_fair_drawdown(row),
            "current_cents": cur,
            "hold_cents": hold_to_settlement(row),
            "candidate_cents": cand,
            "delta_cents": float(cand) - float(cur),
            "suppressed": should_suppress(row, side, p_hold_floor),
            "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
        })
    out.sort(key=lambda row: str(row.get("exit_ts") or row.get("entry_ts") or ""))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    p_hold_floor = float(state.get("p_hold_floor") or P_HOLD_FLOOR)
    side = str(state.get("side") or SIDE).lower()
    rows = future_rows(str(state["freeze_ts_utc"]))
    summary = summarize(rows, side, p_hold_floor)
    blockers = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        blockers.append("delta_not_positive")
    if int(summary.get("suppressed_exits") or 0) <= 0:
        blockers.append("no_suppressed_exits")
    if int(summary.get("suppressed_losers") or 0) > 0:
        blockers.append("suppressed_losers_present")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        blockers.append("suppressed_loss_control_cost_negative")
    return {
        "freeze": state,
        "summary": summary,
        "rows": detail_rows(rows, side, p_hold_floor),
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "interpretation": [
            f"Frozen YES-only reduce-suppression candidate has {summary.get('settled')} settled future rows.",
            f"Delta versus current v28 exits is {summary.get('delta_vs_current_cents')}c.",
            f"Suppressed exits: {summary.get('suppressed_exits')}; winners/losers {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}.",
            "This is narrower than the full reduce-suppression rule and intentionally excludes NO until NO has independent forward evidence.",
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
        "# v28 Frozen YES-Only Exit Reduce Suppression",
        "",
        "Research-only: no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future rows/settled: `{summary.get('rows')}/{summary.get('settled')}`",
        f"- Current/candidate gross: `{summary.get('current_gross_cents')}c/{summary.get('candidate_gross_cents')}c`",
        f"- Delta vs current: `{summary.get('delta_vs_current_cents')}c`",
        f"- Suppressed exits: `{summary.get('suppressed_exits')}`",
        f"- Suppressed winners/losers: `{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}`",
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
        "| market | side | result | entry | exit | reason | p_hold | drawdown | current c | hold c | candidate c | delta c | suppressed | worst hold mark |",
        "|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{row.get('entry_cents')} | {row.get('exit_cents')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{row.get('current_cents')} | {row.get('hold_cents')} | {row.get('candidate_cents')} | "
            f"{fmt(row.get('delta_cents'))} | {row.get('suppressed')} | {row.get('worst_post_exit_hold_mark_cents')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
