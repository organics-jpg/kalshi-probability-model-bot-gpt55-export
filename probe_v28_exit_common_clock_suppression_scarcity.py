"""Strict common-clock suppression-scarcity audit for v28 exit guards.

Research-only; no live bot changes or orders.

The closest strict exit watch is common-clock v2: it is positive, but has far
too few suppressed decisions and too little cushion. This probe keeps the same
strict common-clock window and asks whether small, physically interpretable
relaxations would add suppressions without reintroducing loss-control cost.
It is an audit only, not a new frozen live rule.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_book_gap_candidates import fair_drawdown, hold_book_gap, is_soft_exit, p_hold
from probe_v28_exit_policy_candidates import (
    current_exit,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    is_value_over_hold,
    side_won,
)
from probe_v28_exit_policy_common_clock_watch import (
    DUAL_STATE_JSON,
    build_scored_rows,
    filter_snapshot,
    max_freeze,
    state_freeze,
)
from probe_v28_frozen_exit_book_gap_loss_guard import (
    STATE_JSON as V1_STATE_JSON,
    load_json,
    should_suppress as should_v1_suppress,
)
from probe_v28_frozen_exit_book_gap_loss_guard_v2 import (
    STATE_JSON as V2_STATE_JSON,
    should_suppress as should_v2_suppress,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_suppression_scarcity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_suppression_scarcity_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def suppress_v2(row: dict[str, Any], v2_state: dict[str, Any], _v1_state: dict[str, Any]) -> bool:
    return should_v2_suppress(row, v2_state)


def suppress_v1_like(row: dict[str, Any], _v2_state: dict[str, Any], v1_state: dict[str, Any]) -> bool:
    return should_v1_suppress(row, v1_state)


def suppress_value_shallow10(row: dict[str, Any], _v2_state: dict[str, Any], _v1_state: dict[str, Any]) -> bool:
    if not is_soft_exit(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if is_value_over_hold(row):
        if gap is not None and gap >= 0.0:
            return True
        return p is not None and p >= 0.85 and drawdown is not None and drawdown >= -10.0
    if is_probability_reduce(row):
        return p is not None and p >= 0.79 and gap is not None and gap >= 0.0
    return False


def suppress_value_p90_shallow10(row: dict[str, Any], _v2_state: dict[str, Any], _v1_state: dict[str, Any]) -> bool:
    if not is_soft_exit(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if is_value_over_hold(row):
        if gap is not None and gap >= 0.0:
            return True
        return p is not None and p >= 0.90 and drawdown is not None and drawdown >= -10.0
    if is_probability_reduce(row):
        return p is not None and p >= 0.79 and gap is not None and gap >= 0.0
    return False


def suppress_value_p80_gap0(row: dict[str, Any], _v2_state: dict[str, Any], _v1_state: dict[str, Any]) -> bool:
    if not is_soft_exit(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if is_value_over_hold(row):
        if gap is not None and gap >= 0.0:
            return True
        return p is not None and p >= 0.80 and drawdown is not None and drawdown >= -5.0
    if is_probability_reduce(row):
        return p is not None and p >= 0.79 and gap is not None and gap >= 0.0
    return False


def suppress_reduce_shallow(row: dict[str, Any], _v2_state: dict[str, Any], _v1_state: dict[str, Any]) -> bool:
    if not is_soft_exit(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if is_value_over_hold(row):
        if gap is not None and gap >= 0.0:
            return True
        return p is not None and p >= 0.85 and drawdown is not None and drawdown >= -5.0
    if is_probability_reduce(row):
        if p is None:
            return False
        if gap is not None and gap >= 0.0 and p >= 0.79:
            return True
        return p >= 0.79 and drawdown is not None and drawdown >= -2.5
    return False


POLICIES: list[tuple[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], bool]]] = [
    ("v2_control", suppress_v2),
    ("v1_like_on_v2_clock", suppress_v1_like),
    ("value_p85_shallow10", suppress_value_shallow10),
    ("value_p90_shallow10", suppress_value_p90_shallow10),
    ("value_p80_shallow5", suppress_value_p80_gap0),
    ("value_v2_plus_reduce_shallow2p5", suppress_reduce_shallow),
]


def row_class(row: dict[str, Any]) -> str:
    if is_value_over_hold(row):
        return "value_over_hold"
    if is_probability_reduce(row):
        return "probability_reduce"
    return str(exit_reason(row) or "other")


def row_tags(row: dict[str, Any]) -> list[str]:
    tags = [row_class(row)]
    p = p_hold(row)
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if p is not None:
        if p >= 0.95:
            tags.append("p_hold_ge95")
        elif p >= 0.90:
            tags.append("p_hold_90_95")
        elif p >= 0.85:
            tags.append("p_hold_85_90")
        elif p >= 0.79:
            tags.append("p_hold_79_85")
        else:
            tags.append("p_hold_lt79")
    if gap is not None:
        if gap >= 0.0:
            tags.append("gap_nonnegative")
        elif gap >= -0.05:
            tags.append("gap_neg_0_5pp")
        else:
            tags.append("gap_neg_gt5pp")
    if drawdown is not None:
        if drawdown >= -2.5:
            tags.append("drawdown_shallow_ge_neg2p5")
        elif drawdown >= -5.0:
            tags.append("drawdown_neg2p5_to_neg5")
        elif drawdown >= -10.0:
            tags.append("drawdown_neg5_to_neg10")
        else:
            tags.append("drawdown_deep_lt_neg10")
    return tags


def blockers(summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        out.append("settled_lt_30")
    if int(summary.get("suppressed") or 0) < MIN_SUPPRESSED:
        out.append("suppressed_decisions_lt_30")
    if fnum(summary.get("candidate_net_cents")) <= 0.0:
        out.append("net_not_positive")
    if fnum(summary.get("delta_cents")) <= 0.0:
        out.append("delta_not_positive")
    if fnum(summary.get("loss_cost_cents")) < 0.0:
        out.append("loss_control_cost_negative")
    if int(summary.get("full_loss_cushion") or 0) < MIN_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def summarize_policy(
    rows: list[dict[str, Any]],
    policy: str,
    suppress_fn: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], bool],
    v2_state: dict[str, Any],
    v1_state: dict[str, Any],
) -> dict[str, Any]:
    current_vals: list[float] = []
    candidate_vals: list[float] = []
    suppressed_rows: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    for row in rows:
        cur = current_exit(row)
        hold = hold_to_settlement(row)
        if cur is None or hold is None:
            continue
        cur_f = float(cur)
        hold_f = float(hold)
        suppress = suppress_fn(row, v2_state, v1_state)
        cand = hold_f if suppress else cur_f
        current_vals.append(cur_f)
        candidate_vals.append(cand)
        if suppress:
            suppressed_rows.append(row)
            details.append(
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "result": row.get("result"),
                    "exit_reason": exit_reason(row),
                    "p_hold": p_hold(row),
                    "hold_book_gap": hold_book_gap(row),
                    "fair_drawdown_cents": fair_drawdown(row),
                    "current_cents": cur_f,
                    "hold_cents": hold_f,
                    "delta_cents": hold_f - cur_f,
                    "won": side_won(row),
                    "tags": row_tags(row),
                }
            )
    current_net = sum(current_vals)
    candidate_net = sum(candidate_vals)
    helpful = [row for row in details if row.get("won") is True]
    harmful = [row for row in details if row.get("won") is False]
    loss_cost = sum(fnum(row.get("delta_cents")) for row in harmful)
    winner_recovery = sum(fnum(row.get("delta_cents")) for row in helpful)
    summary = {
        "policy": policy,
        "settled": len(candidate_vals),
        "suppressed": len(suppressed_rows),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_cents": candidate_net - current_net,
        "winner_recovery_cents": winner_recovery,
        "loss_cost_cents": loss_cost,
        "full_loss_cushion": int(candidate_net // 100.0) if candidate_net > 0 else 0,
        "suppressed_tag_counts": dict(Counter(tag for row in details for tag in row.get("tags") or [])),
        "harmful_tag_counts": dict(Counter(tag for row in harmful for tag in row.get("tags") or [])),
        "worst_suppressed_rows": sorted(details, key=lambda row: fnum(row.get("delta_cents")))[:10],
    }
    summary["blockers"] = blockers(summary)
    summary["ready_for_review"] = not summary["blockers"]
    return summary


def build_report() -> dict[str, Any]:
    v1_state = load_json(V1_STATE_JSON)
    v2_state = load_json(V2_STATE_JSON)
    v2_common_freeze = max_freeze(v2_state.get("freeze_ts_utc"), state_freeze(DUAL_STATE_JSON))
    rows = filter_snapshot(build_scored_rows(), v2_common_freeze)
    summaries = [summarize_policy(rows, name, fn, v2_state, v1_state) for name, fn in POLICIES]
    summaries.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -(fnum(row.get("candidate_net_cents"))),
            -(fnum(row.get("delta_cents"))),
        )
    )
    report = {
        "generated_at_utc": utc_now_iso(),
        "window": "new_exit_mix_common_forward_v2",
        "freeze_ts_utc": v2_common_freeze,
        "row_count": len(rows),
        "purpose": "Strict-window suppression scarcity audit for the closest positive exit watch.",
        "policies": summaries,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is an audit over the existing strict common-clock v2 rows; it does not create or change a live exit rule.",
    ]
    best = (report.get("policies") or [{}])[0]
    notes.append(
        f"Best audit policy {best.get('policy')} has {best.get('settled')} settled, "
        f"{best.get('suppressed')} suppressions, candidate net {best.get('candidate_net_cents')}c, "
        f"delta {best.get('delta_cents')}c, loss cost {best.get('loss_cost_cents')}c, "
        f"blockers {best.get('blockers')}."
    )
    control = next((row for row in report.get("policies") or [] if row.get("policy") == "v2_control"), {})
    if control:
        notes.append(
            f"V2 control suppresses {control.get('suppressed')} rows for {control.get('delta_cents')}c delta; "
            f"the scarcity problem remains suppression count and cushion, not observed harmful suppressions."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Common-Clock Suppression Scarcity",
        "",
        "Research-only audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Window: `{report.get('window')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Rows: `{report.get('row_count')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Policies",
            "",
            "| rank | policy | settled | suppressed | helpful/harmful | current c | candidate c | delta c | recovery c | loss cost c | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("policies") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('policy')} | {row.get('settled')} | {row.get('suppressed')} | "
            f"{row.get('helpful_suppressed')}/{row.get('harmful_suppressed')} | "
            f"{fmt(row.get('current_net_cents'))} | {fmt(row.get('candidate_net_cents'))} | "
            f"{fmt(row.get('delta_cents'))} | {fmt(row.get('winner_recovery_cents'))} | "
            f"{fmt(row.get('loss_cost_cents'))} | {row.get('full_loss_cushion')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Worst Suppressed Rows By Policy",
            "",
            "| policy | market | side/result | reason | won | p_hold | gap | drawdown | current | hold | delta | tags |",
            "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("policies") or []:
        for item in row.get("worst_suppressed_rows") or []:
            lines.append(
                f"| {row.get('policy')} | {item.get('market')} | {item.get('side')}/{item.get('result')} | "
                f"{item.get('exit_reason')} | {item.get('won')} | {fmt(item.get('p_hold'))} | "
                f"{fmt(item.get('hold_book_gap'))} | {fmt(item.get('fair_drawdown_cents'))} | "
                f"{fmt(item.get('current_cents'))} | {fmt(item.get('hold_cents'))} | "
                f"{fmt(item.get('delta_cents'))} | {', '.join(item.get('tags') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
