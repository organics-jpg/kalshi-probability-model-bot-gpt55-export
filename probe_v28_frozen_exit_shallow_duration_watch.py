"""Frozen watch for shallow-drawdown short-duration exit suppression.

Research-only; no live bot changes or orders.

The shallow-drawdown harm audit found that the clean diagnostic child guard is
not simply "shallow drawdown"; it is shallow fair-value drawdown plus a very
short time between entry and exit. This freezes that rounded mechanism from a
new timestamp.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from math import floor
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_reason,
    hold_to_settlement,
)
from probe_v28_exit_shallow_drawdown_harm_audit import trade_duration_sec
from probe_v28_frozen_exit_shallow_drawdown_watch import COLLAPSE, SOFT_REDUCE, rows_after


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_REDUCE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
HARM_AUDIT_JSON = OUT_DIR / "v28_exit_shallow_drawdown_harm_audit_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_shallow_duration_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_shallow_duration_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_shallow_duration_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    audit = load_json(HARM_AUDIT_JSON)
    best = audit.get("best_clean_child_rule") or {}
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "shallow_drawdown_duration_lte52_reduce_or_collapse",
        "rule": "For reduce/collapse exits, suppress if fair_drawdown_cents <= 5 and entry-to-exit duration <= 52 seconds.",
        "exit_reasons": [SOFT_REDUCE, COLLAPSE],
        "fair_drawdown_cents_max": 5.0,
        "duration_sec_max": 52.0,
        "origin": "Frozen from v28_exit_shallow_drawdown_harm_audit best clean child rule.",
        "diagnostic_rule": best.get("rule"),
        "diagnostic_selected": best.get("selected"),
        "diagnostic_helpful": best.get("helpful"),
        "diagnostic_harmful": best.get("harmful"),
        "diagnostic_selected_delta_cents": best.get("selected_delta_cents"),
        "physics": "A shallow FV drawdown within roughly one minute of entry is more likely mark/path churn clipping a still-live thesis than true settlement-odds failure.",
        "research_only": True,
        "strict_forward_note": "Only rows after this freeze count as strict forward evidence.",
    }
    write_json(STATE_JSON, state)
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def should_suppress(row: dict[str, Any], state: dict[str, Any]) -> bool:
    drawdown = exit_fair_drawdown(row)
    duration = trade_duration_sec(row)
    return (
        exit_reason(row) in set(state.get("exit_reasons") or [])
        and drawdown is not None
        and drawdown <= float(state.get("fair_drawdown_cents_max") or 0.0)
        and duration is not None
        and duration <= float(state.get("duration_sec_max") or 0.0)
    )


def candidate_exit(row: dict[str, Any], state: dict[str, Any]) -> float | None:
    if should_suppress(row, state):
        return hold_to_settlement(row)
    return current_exit(row)


def delta_if_suppressed(row: dict[str, Any]) -> float | None:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    if cur is None or hold is None:
        return None
    return hold - cur


def fail_reasons(row: dict[str, Any], state: dict[str, Any]) -> list[str]:
    reasons = []
    if exit_reason(row) not in set(state.get("exit_reasons") or []):
        reasons.append("exit_reason_not_reduce_or_collapse")
    drawdown = exit_fair_drawdown(row)
    if drawdown is None:
        reasons.append("fair_drawdown_missing")
    elif drawdown > float(state.get("fair_drawdown_cents_max") or 0.0):
        reasons.append("fair_drawdown_above_5")
    duration = trade_duration_sec(row)
    if duration is None:
        reasons.append("duration_missing")
    elif duration > float(state.get("duration_sec_max") or 0.0):
        reasons.append("duration_above_52")
    return reasons


def compact(row: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "exit_reason": exit_reason(row),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "duration_sec": trade_duration_sec(row),
        "current_cents": current_exit(row),
        "hold_cents": hold_to_settlement(row),
        "delta_if_suppressed_cents": delta_if_suppressed(row),
        "selected": should_suppress(row, state),
        "fail_reasons": fail_reasons(row, state),
    }


def summarize(rows: list[dict[str, Any]], state: dict[str, Any], strict_forward: bool) -> dict[str, Any]:
    scored = []
    suppressed = []
    denominator_fail_reasons: Counter[str] = Counter()
    for row in rows:
        cur = current_exit(row)
        cand = candidate_exit(row, state)
        if cur is None or cand is None:
            continue
        scored.append((row, float(cur), float(cand)))
        if should_suppress(row, state):
            suppressed.append(row)
        else:
            denominator_fail_reasons.update(fail_reasons(row, state))
    current_gross = sum(cur for _, cur, _ in scored)
    candidate_gross = sum(cand for _, _, cand in scored)
    deltas = [delta_if_suppressed(row) or 0.0 for row in suppressed]
    helpful = [value for value in deltas if value > 0.0]
    harmful = [value for value in deltas if value < 0.0]
    cushion = floor(candidate_gross / 100.0) if candidate_gross > 0.0 else 0
    blockers = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_gross <= 0.0:
        blockers.append("net_not_positive")
    if candidate_gross - current_gross <= 0.0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("suppressed_losers_present")
    if sum(harmful) < 0.0:
        blockers.append("suppressed_loss_control_cost_negative")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    return {
        "settled": len(scored),
        "strict_forward": strict_forward,
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross,
        "delta_vs_current_cents": candidate_gross - current_gross,
        "current_wins": sum(1 for _, cur, _ in scored if cur >= 0.0),
        "current_losses": sum(1 for _, cur, _ in scored if cur < 0.0),
        "candidate_wins": sum(1 for _, _, cand in scored if cand >= 0.0),
        "candidate_losses": sum(1 for _, _, cand in scored if cand < 0.0),
        "suppressed_exits": len(suppressed),
        "suppressed_helpful": len(helpful),
        "suppressed_harmful": len(harmful),
        "winner_recovery_cents": sum(helpful),
        "loss_control_cost_cents": sum(harmful),
        "full_loss_cushion_estimate": cushion,
        "exit_reason_counts": dict(Counter(exit_reason(row) for row in rows)),
        "suppressed_exit_reason_counts": dict(Counter(exit_reason(row) for row in suppressed)),
        "denominator_fail_reasons": dict(denominator_fail_reasons),
        "blockers": blockers,
        "selected_examples": [compact(row, state) for row in suppressed[:12]],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows = build_rows()
    base_state = load_json(BASE_REDUCE_STATE_JSON)
    lanes = [
        {
            "lane": "diagnostic_from_reduce_freeze",
            "freeze_ts_utc": base_state.get("freeze_ts_utc"),
            "strict_forward": False,
            "rows": rows_after(rows, base_state.get("freeze_ts_utc")),
        },
        {
            "lane": "post_shallow_duration_birth",
            "freeze_ts_utc": state.get("freeze_ts_utc"),
            "strict_forward": True,
            "rows": rows_after(rows, state.get("freeze_ts_utc")),
        },
    ]
    lane_reports = []
    for lane in lanes:
        lane_reports.append({
            "lane": lane["lane"],
            "freeze_ts_utc": lane["freeze_ts_utc"],
            "row_count": len(lane["rows"]),
            "summary": summarize(lane["rows"], state, bool(lane["strict_forward"])),
        })
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "base_reduce_freeze_ts_utc": base_state.get("freeze_ts_utc"),
        "lanes": lane_reports,
        "best_diagnostic": lane_reports[0]["summary"],
        "best_strict_forward": lane_reports[1]["summary"],
        "candidate_live_ready": False,
        "interpretation": [
            "Research-only frozen watch; this does not change live exits or promote a candidate.",
            "Diagnostic lane confirms why the child was frozen, but does not count as promotion evidence.",
            "Strict post-birth rows must prove the rule with no harmful loss-control cost.",
        ],
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return "None" if value is None else str(value)


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Exit Shallow-Duration Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Candidate: `{state.get('candidate')}`",
        f"- Diagnostic origin: `{state.get('diagnostic_rule')}` selected {state.get('diagnostic_selected')} with {state.get('diagnostic_helpful')}/{state.get('diagnostic_harmful')} helpful/harmful and {state.get('diagnostic_selected_delta_cents')}c.",
        f"- Physics: {state.get('physics')}",
        "",
        "## Interpretation",
        "",
    ]
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    for lane in report.get("lanes") or []:
        row = lane.get("summary") or {}
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Freeze UTC: `{lane.get('freeze_ts_utc')}`",
            f"- Rows: `{lane.get('row_count')}`",
            "",
            "| settled | current c | candidate c | delta c | W/L current | W/L candidate | suppressed | helpful/harmful | loss cost c | cushion | blockers |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            (
                f"| {row.get('settled')} | {fmt(row.get('current_gross_cents'))} | {fmt(row.get('candidate_gross_cents'))} | "
                f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('current_wins')}/{row.get('current_losses')} | "
                f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | {row.get('suppressed_exits')} | "
                f"{row.get('suppressed_helpful')}/{row.get('suppressed_harmful')} | {fmt(row.get('loss_control_cost_cents'))} | "
                f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            ),
        ])
    strict = report.get("best_strict_forward") or {}
    lines.extend([
        "",
        "## Best Strict Forward",
        "",
        f"- Settled/suppressed: `{strict.get('settled')}/{strict.get('suppressed_exits')}`",
        f"- Delta: `{fmt(strict.get('delta_vs_current_cents'))}c`",
        f"- Blockers: `{strict.get('blockers')}`",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_JSON, report)
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
