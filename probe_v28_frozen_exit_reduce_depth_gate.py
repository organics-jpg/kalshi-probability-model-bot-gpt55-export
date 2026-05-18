"""Forward watch for entry-depth gated reduce-exit suppression.

Research-only; no live bot changes or orders.

The reduce-suppression signature report found that the harmful suppressed
losers came from rows outside the shallow entry-depth cluster. This freezes
observable entry-depth gates from a new timestamp so future reduce exits can
test that mechanism without counting the retrospective separator as evidence.
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
BASE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
SIGNATURE_JSON = OUT_DIR / "v28_exit_reduce_loss_control_signature_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.md"

MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3

RULES = {
    "reduce_suppress_p_hold_ge_075_entry_depth_lte_384": {
        "p_hold_min": 0.75,
        "entry_depth_max": 384.0,
        "physics": "Suppress reduce exits only when original entry depth was shallow enough to suggest a thin-book clip rather than a true loss-control signal.",
    },
    "reduce_suppress_p_hold_ge_075_entry_depth_lte_295": {
        "p_hold_min": 0.75,
        "entry_depth_max": 295.0,
        "physics": "Stricter version of the shallow-entry-depth loss-control repair.",
    },
    "reduce_suppress_p_hold_ge_079_entry_depth_lte_384": {
        "p_hold_min": 0.79,
        "entry_depth_max": 384.0,
        "physics": "Require both high hold probability and shallow original entry depth.",
    },
    "reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5": {
        "p_hold_min": 0.75,
        "entry_depth_max": 384.0,
        "drawdown_max": 2.5,
        "physics": "Require shallow original entry depth and small fair-value drawdown at the reduce exit.",
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
    signature = load_json(SIGNATURE_JSON)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "exit_reduce_depth_gate",
        "origin": "Derived from v28_exit_reduce_loss_control_signature; earlier rows are diagnostic only.",
        "signature_best_separator": (signature.get("candidate_separators") or [{}])[0],
        "rules": RULES,
        "strict_forward_note": "Only post_depth_gate_birth lanes count as forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def entry_depth(row: dict[str, Any]) -> float | None:
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    for key in ("mushroom_v28_eligible_depth", "entry_depth", "eligible_depth"):
        value = as_float(entry.get(key))
        if value is not None:
            return value
    return as_float(row.get("entry_depth"))


def should_suppress(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if not is_probability_reduce(row):
        return False
    p_hold = exit_p_hold(row)
    depth = entry_depth(row)
    if p_hold is None or depth is None:
        return False
    if p_hold < float(rule.get("p_hold_min") or 0.0):
        return False
    if depth > float(rule.get("entry_depth_max") or 0.0):
        return False
    drawdown_max = rule.get("drawdown_max")
    if drawdown_max is not None:
        drawdown = exit_fair_drawdown(row)
        if drawdown is None or drawdown > float(drawdown_max):
            return False
    return True


def candidate_gross(row: dict[str, Any], rule: dict[str, Any]) -> float | None:
    if should_suppress(row, rule):
        return hold_to_settlement(row)
    return current_exit(row)


def summarize(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, Any]:
    current_vals: list[float] = []
    candidate_vals: list[float] = []
    suppressed: list[dict[str, Any]] = []
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
    suppressed_deltas = [
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
    ]
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
        "suppressed_winners": len(helpful),
        "suppressed_losers": len(harmful),
        "suppressed_delta_cents": sum(suppressed_deltas),
        "winner_clip_recovered_cents": sum(helpful),
        "loss_control_cost_cents": sum(harmful),
        "full_loss_cushion_estimate": int(max(0.0, candidate_gross_cents - current_gross) // 100.0),
    }


def compact_row(row: dict[str, Any], rule: dict[str, Any], path_by_market: dict[str, dict[str, Any]]) -> dict[str, Any]:
    cur = current_exit(row)
    cand = candidate_gross(row, rule)
    path = path_by_market.get(str(row.get("market"))) or {}
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "entry_depth": entry_depth(row),
        "exit_reason": exit_reason(row),
        "p_hold": exit_p_hold(row),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "current_cents": cur,
        "hold_cents": hold_to_settlement(row),
        "candidate_cents": cand,
        "delta_cents": None if cur is None or cand is None else float(cand) - float(cur),
        "suppressed": should_suppress(row, rule),
        "side_won": side_won(row),
        "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        out.append("settled_lt_30")
    if int(summary.get("suppressed_exits") or 0) <= 0:
        out.append("no_suppressed_exits_yet")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        out.append("delta_not_positive")
    if int(summary.get("suppressed_losers") or 0) > 0:
        out.append("suppressed_losers_present")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        out.append("suppressed_loss_control_cost_negative")
    if int(summary.get("full_loss_cushion_estimate") or 0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_lane(label: str, freeze_ts: str) -> dict[str, Any]:
    rows = future_rows(freeze_ts)
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    variants = []
    for name, rule in RULES.items():
        summary = summarize(rows, rule)
        selected_details = [
            compact_row(row, rule, path_by_market)
            for row in rows
            if should_suppress(row, rule)
        ]
        selected_details.sort(key=lambda row: float(row.get("delta_cents") or 0.0))
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "rule": rule,
                "summary": summary,
                "blockers": blockers(summary),
                "suppressed_rows": selected_details,
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("delta_vs_current_cents") or -999999.0),
            int((row.get("summary") or {}).get("suppressed_losers") or 999),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "rows": len(rows),
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    base_state = load_json(BASE_STATE_JSON)
    lanes = []
    if base_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_from_reduce_freeze", str(base_state["freeze_ts_utc"])))
    lanes.append(evaluate_lane("post_depth_gate_birth", str(state["freeze_ts_utc"])))
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "base_reduce_freeze": base_state,
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a forward-only entry-depth gate watch; pre-birth rows are diagnostic and cannot promote the rule.",
    ]
    signature = (report.get("state") or {}).get("signature_best_separator") or {}
    if signature:
        notes.append(
            f"Origin separator was {signature.get('feature')} {signature.get('direction')} {signature.get('threshold')}: selected W/L {signature.get('selected_helpful')}/{signature.get('selected_harmful')} and delta {signature.get('selected_delta_cents')}c."
        )
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"delta {summary.get('delta_vs_current_cents')}c, suppressed {summary.get('suppressed_exits')} "
            f"W/L {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}, "
            f"loss-control cost {summary.get('loss_control_cost_cents')}c, blockers {best.get('blockers')}."
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
        "# v28 Frozen Exit Reduce Entry-Depth Gate",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Depth-gate freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend(
            [
                "| rank | candidate | settled | current c | candidate c | delta c | suppressed | sup W/L | recovery c | loss cost c | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, variant in enumerate(lane.get("variants") or [], start=1):
            summary = variant.get("summary") or {}
            lines.append(
                f"| {idx} | {variant.get('candidate')} | {summary.get('settled')} | "
                f"{fmt(summary.get('current_gross_cents'))} | {fmt(summary.get('candidate_gross_cents'))} | "
                f"{fmt(summary.get('delta_vs_current_cents'))} | {summary.get('suppressed_exits')} | "
                f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
                f"{fmt(summary.get('winner_clip_recovered_cents'))} | {fmt(summary.get('loss_control_cost_cents'))} | "
                f"{summary.get('full_loss_cushion_estimate')} | {', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Best Suppressed Rows", ""])
        lines.extend(
            [
                "| market | side | result | reason | depth | p_hold | drawdown | current c | hold c | delta c | side won | worst mark |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|",
            ]
        )
        for row in (best.get("suppressed_rows") or [])[:24]:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
                f"{fmt(row.get('entry_depth'))} | {fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
                f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
                f"{fmt(row.get('delta_cents'))} | {row.get('side_won')} | {fmt(row.get('worst_post_exit_hold_mark_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
