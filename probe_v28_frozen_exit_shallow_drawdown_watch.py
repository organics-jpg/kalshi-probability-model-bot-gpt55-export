"""Frozen watch for shallow fair-drawdown exit suppression.

Research-only; no live bot changes or orders.

The unresolved-loss separator found that matched losses with shallow
fair-value drawdown at exit were often clipped winners. This probe freezes a
rounded observable rule family and scores it on the full exit denominator, not
only on known losing rows.
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
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_REDUCE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
SEPARATOR_JSON = OUT_DIR / "v28_exit_unresolved_state_separator_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3

SOFT_REDUCE = "mushroom_v28_probability_reduce"
COLLAPSE = "mushroom_v28_probability_collapse_full"
VALUE_OVER_HOLD = "mushroom_v28_exit_value_over_hold"

RULES = {
    "shallow_drawdown_reduce_or_collapse_lte5": {
        "exit_reasons": [SOFT_REDUCE, COLLAPSE],
        "fair_drawdown_cents_max": 5.0,
        "physics": "If fair-value drawdown is shallow, reduce/collapse exits may be path turbulence rather than thesis failure.",
    },
    "shallow_drawdown_reduce_only_lte5": {
        "exit_reasons": [SOFT_REDUCE],
        "fair_drawdown_cents_max": 5.0,
        "physics": "Probability-reduce exits with shallow fair drawdown are the cleanest clipped-winner hypothesis.",
    },
    "shallow_drawdown_collapse_only_lte5": {
        "exit_reasons": [COLLAPSE],
        "fair_drawdown_cents_max": 5.0,
        "physics": "Collapse exits with shallow fair drawdown test whether collapse is sometimes mark churn rather than true FV failure.",
    },
    "shallow_drawdown_any_exit_lte5": {
        "exit_reasons": [SOFT_REDUCE, COLLAPSE, VALUE_OVER_HOLD],
        "fair_drawdown_cents_max": 5.0,
        "physics": "Broad sanity check across all v28 soft/value exits; this is expected to be riskier than child rules.",
    },
    "shallow_drawdown_reduce_or_collapse_lte5_p_hold60": {
        "exit_reasons": [SOFT_REDUCE, COLLAPSE],
        "fair_drawdown_cents_max": 5.0,
        "p_hold_min": 0.60,
        "physics": "Requires shallow fair drawdown plus at least modest hold probability before suppressing reduce/collapse exits.",
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    separator = load_json(SEPARATOR_JSON)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "exit_shallow_fair_drawdown_watch",
        "origin": "Rounded from v28_exit_unresolved_state_separator best clean diagnostic rule.",
        "source_best_rounded_rule": (separator.get("best_nice_clean_diagnostic_rule") or {}).get("rule"),
        "rules": RULES,
        "research_only": True,
        "strict_forward_note": "Only post_shallow_drawdown_birth lanes count as forward evidence.",
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


def row_exit_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("exit_ts") or row.get("entry_ts"))


def rows_after(rows: list[dict[str, Any]], freeze_ts: str | None) -> list[dict[str, Any]]:
    freeze = parse_ts(freeze_ts)
    if freeze is None:
        return rows
    return [
        row for row in rows
        if (row_exit_ts(row) or datetime.min.replace(tzinfo=timezone.utc)) >= freeze
    ]


def should_suppress(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    reason = exit_reason(row)
    drawdown = exit_fair_drawdown(row)
    if reason not in set(rule.get("exit_reasons") or []):
        return False
    if drawdown is None or drawdown > float(rule.get("fair_drawdown_cents_max")):
        return False
    p_hold_min = rule.get("p_hold_min")
    if p_hold_min is not None:
        p_hold = exit_p_hold(row)
        if p_hold is None or p_hold < float(p_hold_min):
            return False
    return True


def candidate_exit(row: dict[str, Any], rule: dict[str, Any]) -> float | None:
    if should_suppress(row, rule):
        return hold_to_settlement(row)
    return current_exit(row)


def delta_if_suppressed(row: dict[str, Any]) -> float | None:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    if cur is None or hold is None:
        return None
    return hold - cur


def fail_reasons(row: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    reasons = []
    if exit_reason(row) not in set(rule.get("exit_reasons") or []):
        reasons.append("exit_reason_not_in_rule")
    drawdown = exit_fair_drawdown(row)
    if drawdown is None:
        reasons.append("fair_drawdown_missing")
    elif drawdown > float(rule.get("fair_drawdown_cents_max")):
        reasons.append("fair_drawdown_above_ceiling")
    p_hold_min = rule.get("p_hold_min")
    if p_hold_min is not None:
        p_hold = exit_p_hold(row)
        if p_hold is None:
            reasons.append("p_hold_missing")
        elif p_hold < float(p_hold_min):
            reasons.append("p_hold_below_floor")
    return reasons


def compact(row: dict[str, Any], rule: dict[str, Any] | None = None) -> dict[str, Any]:
    selected = should_suppress(row, rule) if rule else None
    return {
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
        "current_cents": current_exit(row),
        "hold_cents": hold_to_settlement(row),
        "delta_if_suppressed_cents": delta_if_suppressed(row),
        "selected": selected,
        "fail_reasons": fail_reasons(row, rule) if rule else [],
    }


def summarize(rows: list[dict[str, Any]], rule_name: str, rule: dict[str, Any], strict_forward: bool) -> dict[str, Any]:
    scored = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_exit(row, rule)
        if cur is None or cand is None:
            continue
        scored.append((row, float(cur), float(cand)))
        if should_suppress(row, rule):
            suppressed.append(row)
    current_gross = sum(cur for _, cur, _ in scored)
    candidate_gross = sum(cand for _, _, cand in scored)
    deltas = [delta_if_suppressed(row) or 0.0 for row in suppressed]
    helpful = [value for value in deltas if value > 0.0]
    harmful = [value for value in deltas if value < 0.0]
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
    cushion = floor(candidate_gross / 100.0) if candidate_gross > 0.0 else 0
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    return {
        "policy": rule_name,
        "strict_forward": strict_forward,
        "settled": len(scored),
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
        "blockers": blockers,
        "examples": [compact(row, rule) for row in suppressed[:12]],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows = build_rows()
    base_state = load_json(BASE_REDUCE_STATE_JSON)
    base_freeze_ts = base_state.get("freeze_ts_utc")
    lanes = [
        {
            "lane": "diagnostic_from_reduce_freeze",
            "freeze_ts_utc": base_freeze_ts,
            "strict_forward": False,
            "rows": rows_after(rows, base_freeze_ts),
        },
        {
            "lane": "post_shallow_drawdown_birth",
            "freeze_ts_utc": state.get("freeze_ts_utc"),
            "strict_forward": True,
            "rows": rows_after(rows, state.get("freeze_ts_utc")),
        },
    ]
    lane_reports = []
    for lane in lanes:
        variants = [
            summarize(lane["rows"], rule_name, rule, bool(lane["strict_forward"]))
            for rule_name, rule in (state.get("rules") or {}).items()
        ]
        variants.sort(
            key=lambda item: (
                item["strict_forward"],
                not item["blockers"],
                item["delta_vs_current_cents"],
                item["suppressed_exits"],
            ),
            reverse=True,
        )
        lane_reports.append({
            "lane": lane["lane"],
            "freeze_ts_utc": lane["freeze_ts_utc"],
            "strict_forward": lane["strict_forward"],
            "row_count": len(lane["rows"]),
            "variants": variants,
        })
    best_diag = (lane_reports[0].get("variants") or [{}])[0]
    best_strict = (lane_reports[1].get("variants") or [{}])[0]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "base_reduce_freeze_ts_utc": base_freeze_ts,
        "lanes": lane_reports,
        "best_diagnostic": best_diag,
        "best_strict_forward": best_strict,
        "candidate_live_ready": False,
        "interpretation": [
            "Research-only frozen watch; this does not change live exits or promote a candidate.",
            "Diagnostic lane uses rows after the older reduce-exit freeze only for mechanism context.",
            "Only post_shallow_drawdown_birth rows count as strict forward evidence.",
        ],
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return "None" if value is None else str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Exit Shallow-Drawdown Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Source rounded rule: `{(report.get('state') or {}).get('source_best_rounded_rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Freeze UTC: `{lane.get('freeze_ts_utc')}`",
            f"- Strict forward: `{lane.get('strict_forward')}`",
            f"- Rows: `{lane.get('row_count')}`",
            "",
            "| policy | settled | current c | candidate c | delta c | W/L current | W/L candidate | suppressed | helpful/harmful | loss cost c | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in lane.get("variants") or []:
            lines.append(
                f"| {row.get('policy')} | {row.get('settled')} | {fmt(row.get('current_gross_cents'))} | "
                f"{fmt(row.get('candidate_gross_cents'))} | {fmt(row.get('delta_vs_current_cents'))} | "
                f"{row.get('current_wins')}/{row.get('current_losses')} | {row.get('candidate_wins')}/{row.get('candidate_losses')} | "
                f"{row.get('suppressed_exits')} | {row.get('suppressed_helpful')}/{row.get('suppressed_harmful')} | "
                f"{fmt(row.get('loss_control_cost_cents'))} | {row.get('full_loss_cushion_estimate')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    best = report.get("best_strict_forward") or {}
    lines.extend([
        "",
        "## Best Strict Forward",
        "",
        f"- Policy: `{best.get('policy')}`",
        f"- Settled/suppressed: `{best.get('settled')}/{best.get('suppressed_exits')}`",
        f"- Delta: `{fmt(best.get('delta_vs_current_cents'))}c`",
        f"- Blockers: `{best.get('blockers')}`",
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
