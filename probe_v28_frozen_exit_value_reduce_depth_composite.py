"""Frozen composite watch for value-exit and reduce-depth exit repairs.

Research-only; no live bot changes or orders.

This combines the two cleanest exit-policy mechanisms found so far:

1. Value-over-hold exits are suppressed only under the stricter book/fair-value
   guard from loss-guard v2.
2. Probability-reduce exits are suppressed only when the original entry depth
   was shallow enough to support the "thin-book clip" interpretation.

The composite is frozen from its own timestamp. Diagnostic rows explain why it
exists, but only post-freeze rows count for promotion.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import fair_drawdown, hold_book_gap, p_hold
from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    is_value_over_hold,
    side_won,
)
from probe_v28_frozen_exit_reduce_depth_gate import entry_depth
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_state.json"
REDUCE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
BOOK_GAP_STATE_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_FULL_LOSS_CUSHION = 3

RULES = {
    "value_v2_reduce_depth384": {
        "value_mode": "v2",
        "reduce_p_hold_min": 0.75,
        "reduce_entry_depth_max": 384.0,
    },
    "value_v2_reduce_depth295": {
        "value_mode": "v2",
        "reduce_p_hold_min": 0.75,
        "reduce_entry_depth_max": 295.0,
    },
    "value_v2_reduce_depth384_p79": {
        "value_mode": "v2",
        "reduce_p_hold_min": 0.79,
        "reduce_entry_depth_max": 384.0,
    },
    "value_only_p75_reduce_depth384": {
        "value_mode": "value_only_p75",
        "reduce_p_hold_min": 0.75,
        "reduce_entry_depth_max": 384.0,
    },
}


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
        "candidate": "value_v2_reduce_depth384",
        "candidate_family": "exit_value_reduce_depth_composite",
        "rules": RULES,
        "rule": (
            "Suppress value-over-hold exits using the v2 book/fair-drawdown guard; "
            "suppress probability_reduce exits only when p_hold >= 0.75 and entry_depth <= 384."
        ),
        "physics": (
            "Value exits and reduce exits are different physical events. Value exits can be rich-book "
            "winner clipping, but high-p_hold alone is unsafe when the executable bid is generous. "
            "Reduce exits are suppressible only in shallow original depth, where the exit is more plausibly "
            "thin-book turbulence than true thesis failure."
        ),
        "strict_forward_note": "Only post_composite_birth rows count as forward evidence.",
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


def rows_after(freeze_ts: str | None) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows = []
    for row in build_rows():
        ts = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and ts is not None and ts < freeze_dt:
            continue
        rows.append(row)
    return rows


def suppress_value_v2(row: dict[str, Any]) -> bool:
    if not is_value_over_hold(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if gap is not None and gap >= 0.0:
        return True
    return p is not None and p >= 0.85 and drawdown is not None and drawdown >= -5.0


def suppress_value_only_p75(row: dict[str, Any]) -> bool:
    if not is_value_over_hold(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    return (gap is not None and gap >= 0.15) or (p is not None and p >= 0.75)


def should_suppress(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if rule.get("value_mode") == "v2" and suppress_value_v2(row):
        return True
    if rule.get("value_mode") == "value_only_p75" and suppress_value_only_p75(row):
        return True
    if is_probability_reduce(row):
        p = p_hold(row)
        depth = entry_depth(row)
        return (
            p is not None
            and depth is not None
            and p >= float(rule.get("reduce_p_hold_min") or 0.0)
            and depth <= float(rule.get("reduce_entry_depth_max") or 0.0)
        )
    return False


def candidate_gross(row: dict[str, Any], rule: dict[str, Any]) -> float | None:
    if should_suppress(row, rule):
        return hold_to_settlement(row)
    return current_exit(row)


def summarize(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, rule)
        if cur is None or cand is None:
            continue
        current_vals.append(float(cur))
        candidate_vals.append(float(cand))
        if should_suppress(row, rule):
            suppressed.append(row)
    current_gross = sum(current_vals)
    candidate_gross_cents = sum(candidate_vals)
    helpful = [
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is True
    ]
    harmful = [
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is False
    ]
    value_suppressed = [row for row in suppressed if is_value_over_hold(row)]
    reduce_suppressed = [row for row in suppressed if is_probability_reduce(row)]
    return {
        "rows": len(rows),
        "settled": len(candidate_vals),
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross_cents,
        "net_cents": candidate_gross_cents,
        "delta_vs_current_cents": candidate_gross_cents - current_gross,
        "current_wins": sum(1 for value in current_vals if value >= 0.0),
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "candidate_wins": sum(1 for value in candidate_vals if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "suppressed_exits": len(suppressed),
        "suppressed_winners": len(helpful),
        "suppressed_losers": len(harmful),
        "value_suppressed": len(value_suppressed),
        "reduce_suppressed": len(reduce_suppressed),
        "winner_clip_recovered_cents": sum(helpful),
        "loss_control_cost_cents": sum(harmful),
        "full_loss_cushion_estimate": int(candidate_gross_cents // 100.0) if candidate_gross_cents > 0.0 else 0,
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        out.append("settled_lt_30")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        out.append("delta_not_positive")
    if float(summary.get("candidate_gross_cents") or 0.0) <= 0.0:
        out.append("net_not_positive")
    if int(summary.get("suppressed_exits") or 0) < MIN_SUPPRESSED_DECISIONS:
        out.append("suppressed_decisions_lt_30")
    if int(summary.get("suppressed_losers") or 0) > 0:
        out.append("suppressed_losers_present")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        out.append("suppressed_loss_control_cost_negative")
    if int(summary.get("full_loss_cushion_estimate") or 0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def detail_rows(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    out = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, rule)
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
            "entry_depth": entry_depth(row),
            "p_hold": p_hold(row),
            "hold_book_gap": hold_book_gap(row),
            "fair_drawdown_cents": fair_drawdown(row),
            "current_cents": cur,
            "hold_cents": hold_to_settlement(row),
            "candidate_cents": cand,
            "delta_cents": float(cand) - float(cur),
            "suppressed": should_suppress(row, rule),
            "side_won": side_won(row),
            "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
        })
    out.sort(key=lambda row: str(row.get("exit_ts") or row.get("entry_ts") or ""))
    return out


def evaluate_lane(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    variants = []
    for name, rule in RULES.items():
        summary = summarize(rows, rule)
        row_blockers = blockers(summary)
        variants.append({
            "candidate": f"{label}_{name}",
            "rule": name,
            "rule_params": rule,
            "summary": summary,
            "blockers": row_blockers,
            "live_ready": not row_blockers,
            "suppressed_rows": [row for row in detail_rows(rows, rule) if row.get("suppressed")],
        })
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("delta_vs_current_cents") or -999999.0),
            -float((row.get("summary") or {}).get("candidate_gross_cents") or -999999.0),
        )
    )
    return {"lane": label, "variants": variants}


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    reduce_state = load_json(REDUCE_STATE_JSON)
    book_gap_state = load_json(BOOK_GAP_STATE_JSON)
    diagnostic_freeze = min(
        str(reduce_state.get("freeze_ts_utc") or state["freeze_ts_utc"]),
        str(book_gap_state.get("freeze_ts_utc") or state["freeze_ts_utc"]),
    )
    lanes = [
        evaluate_lane("diagnostic_from_exit_freezes", rows_after(diagnostic_freeze)),
        evaluate_lane("post_composite_birth", rows_after(str(state["freeze_ts_utc"]))),
    ]
    primary = next(
        (
            row for row in (lanes[-1].get("variants") or [])
            if row.get("rule") == state.get("candidate")
        ),
        (lanes[-1].get("variants") or [{}])[0],
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze": state,
        "diagnostic_freeze_ts_utc": diagnostic_freeze,
        "lanes": lanes,
        "summary": primary.get("summary") or {},
        "blockers": primary.get("blockers") or [],
        "candidate_live_ready": bool(primary.get("live_ready")),
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Composite is frozen independently; diagnostic rows are not promotion evidence.",
        "Primary candidate combines v2 value-exit guard with reduce-depth p75/depth384 guard.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('rule')} settled {summary.get('settled')}, "
            f"candidate {summary.get('candidate_gross_cents')}c, delta {summary.get('delta_vs_current_cents')}c, "
            f"suppressed {summary.get('suppressed_exits')} value/reduce {summary.get('value_suppressed')}/{summary.get('reduce_suppressed')}, "
            f"suppressed W/L {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}, "
            f"loss cost {summary.get('loss_control_cost_cents')}c, blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Exit Value + Reduce-Depth Composite",
        "",
        "Research-only frozen forward watch. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Any live-ready primary: `{report.get('candidate_live_ready')}`",
        f"- Primary blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            "| rank | rule | settled | W/L | current c | candidate c | delta c | suppressed | value/reduce | suppressed W/L | recovery c | loss cost c | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("summary") or {}
            lines.append(
                f"| {idx} | `{row.get('rule')}` | {summary.get('settled')} | "
                f"{summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
                f"{fmt(summary.get('current_gross_cents'))} | {fmt(summary.get('candidate_gross_cents'))} | "
                f"{fmt(summary.get('delta_vs_current_cents'))} | {summary.get('suppressed_exits')} | "
                f"{summary.get('value_suppressed')}/{summary.get('reduce_suppressed')} | "
                f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
                f"{fmt(summary.get('winner_clip_recovered_cents'))} | {fmt(summary.get('loss_control_cost_cents'))} | "
                f"{summary.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
