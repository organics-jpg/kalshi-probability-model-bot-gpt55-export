"""Frozen watch for observable loss-control gates on reduce-exit suppression.

Research-only; no live bot changes or orders.

The reduce-exit actionability report found several observable separators that
kept the winner-recovery benefit while avoiding suppressed losers in the
diagnostic window. This freezes those separators from a new timestamp so future
probability-reduce exits can test the mechanism without promoting a
retrospective threshold.
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
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    side_won,
)
from probe_v28_frozen_exit_reduce_depth_gate import entry_depth
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
ACTIONABILITY_JSON = OUT_DIR / "v28_exit_reduce_loss_control_actionability_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_EXITS = 30
MIN_FULL_LOSS_CUSHION = 3

RULES = {
    "reduce_suppress_p75_entry_stc_lte_596": {
        "p_hold_min": 0.75,
        "entry_seconds_to_close_max": 596.372,
        "physics": "Late-entry reduce exits are more likely to be transient mark churn than a real change in settlement odds.",
    },
    "reduce_suppress_p75_duration_lte_52": {
        "p_hold_min": 0.75,
        "trade_duration_sec_max": 52.304092,
        "physics": "Very short-lived reduce exits after entry look like microstructure churn clipping a still-valid position.",
    },
    "reduce_suppress_p75_entry_book_age_gte_672": {
        "p_hold_min": 0.75,
        "entry_book_age_ms_min": 672.0,
        "physics": "A slightly older but accepted entry book followed by high p_hold reduce may represent stale-ish entry conservatism rather than true loss control.",
    },
    "reduce_suppress_p75_exit_sigma_gte_110": {
        "p_hold_min": 0.75,
        "exit_sigma_t_dollars_min": 110.113616,
        "physics": "High remaining sigma at exit means the reduce trigger has more path-noise risk and should need more confirmation before clipping.",
    },
    "reduce_suppress_p75_exit_cents_lte_72": {
        "p_hold_min": 0.75,
        "exit_cents_max": 72.0,
        "physics": "Lower exit marks under high p_hold may be underpriced churn where holding recovers value.",
    },
    "reduce_suppress_p75_entry_volshock_gte_0468": {
        "p_hold_min": 0.75,
        "entry_volshock_min": 0.468181,
        "physics": "Positive entry volshock may make early reduce exits overreact to path turbulence rather than settlement odds.",
    },
    "reduce_suppress_p75_depth_lte384_or_duration_lte52": {
        "p_hold_min": 0.75,
        "entry_depth_max_or": 384.0,
        "trade_duration_sec_max_or": 52.304092,
        "physics": "Union of the strongest existing shallow-depth mechanism and short-duration churn mechanism.",
    },
    "reduce_suppress_p75_depth_lte384_and_duration_lte75": {
        "p_hold_min": 0.75,
        "entry_depth_max": 384.0,
        "trade_duration_sec_max": 75.0,
        "physics": "Conservative composite: suppress only when shallow entry depth and fast reduce churn agree.",
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
    actionability = load_json(ACTIONABILITY_JSON)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "exit_reduce_observable_loss_control_watch",
        "origin": "Derived from observable separators in v28_exit_reduce_loss_control_actionability; earlier rows are diagnostic only.",
        "actionability_interpretation": actionability.get("interpretation") or [],
        "rules": RULES,
        "strict_forward_note": "Only post_observable_birth lanes count as forward evidence.",
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


def entry_feature(row: dict[str, Any], key: str) -> float | None:
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    return as_float(entry.get(key))


def exit_feature(row: dict[str, Any], key: str) -> float | None:
    exit_features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return as_float(exit_features.get(key))


def trade_duration_sec(row: dict[str, Any]) -> float | None:
    entry = parse_ts(row.get("entry_ts"))
    exit_ts = parse_ts(row.get("exit_ts"))
    if entry is None or exit_ts is None:
        return None
    return (exit_ts - entry).total_seconds()


def value_passes(value: float | None, min_value: Any = None, max_value: Any = None) -> bool:
    if value is None:
        return False
    if min_value is not None and value < float(min_value):
        return False
    if max_value is not None and value > float(max_value):
        return False
    return True


def should_suppress(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if not is_probability_reduce(row):
        return False
    p_hold = exit_p_hold(row)
    if p_hold is None or p_hold < float(rule.get("p_hold_min") or 0.0):
        return False

    or_depth = rule.get("entry_depth_max_or")
    or_duration = rule.get("trade_duration_sec_max_or")
    if or_depth is not None or or_duration is not None:
        return (
            value_passes(entry_depth(row), max_value=or_depth)
            or value_passes(trade_duration_sec(row), max_value=or_duration)
        )

    checks = [
        value_passes(entry_feature(row, "mushroom_v28_seconds_to_close"), max_value=rule.get("entry_seconds_to_close_max")),
        value_passes(trade_duration_sec(row), max_value=rule.get("trade_duration_sec_max")),
        value_passes(entry_feature(row, "mushroom_v28_book_age_ms"), min_value=rule.get("entry_book_age_ms_min")),
        value_passes(exit_feature(row, "mushroom_v28_sigma_t_dollars"), min_value=rule.get("exit_sigma_t_dollars_min")),
        value_passes(as_float(row.get("exit_cents")), max_value=rule.get("exit_cents_max")),
        value_passes(entry_feature(row, "mushroom_v28_volshock"), min_value=rule.get("entry_volshock_min")),
        value_passes(entry_depth(row), max_value=rule.get("entry_depth_max")),
    ]
    active_checks = [
        check for check, key in zip(
            checks,
            (
                "entry_seconds_to_close_max",
                "trade_duration_sec_max",
                "entry_book_age_ms_min",
                "exit_sigma_t_dollars_min",
                "exit_cents_max",
                "entry_volshock_min",
                "entry_depth_max",
            ),
        )
        if rule.get(key) is not None
    ]
    return bool(active_checks) and all(active_checks)


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
        "exit_reason": exit_reason(row),
        "p_hold": exit_p_hold(row),
        "entry_depth": entry_depth(row),
        "entry_seconds_to_close": entry_feature(row, "mushroom_v28_seconds_to_close"),
        "trade_duration_sec": trade_duration_sec(row),
        "entry_book_age_ms": entry_feature(row, "mushroom_v28_book_age_ms"),
        "exit_sigma_t_dollars": exit_feature(row, "mushroom_v28_sigma_t_dollars"),
        "entry_volshock": entry_feature(row, "mushroom_v28_volshock"),
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
    if int(summary.get("suppressed_exits") or 0) < MIN_SUPPRESSED_EXITS:
        out.append("suppressed_decisions_lt_30")
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
        suppressed_rows = [
            compact_row(row, rule, path_by_market)
            for row in rows
            if should_suppress(row, rule)
        ]
        suppressed_rows.sort(key=lambda row: float(row.get("delta_cents") or 0.0))
        variants.append({
            "candidate": f"{label}_{name}",
            "rule": rule,
            "summary": summary,
            "blockers": blockers(summary),
            "suppressed_rows": suppressed_rows,
        })
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            int((row.get("summary") or {}).get("suppressed_losers") or 999),
            -float((row.get("summary") or {}).get("delta_vs_current_cents") or -999999.0),
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
    lanes.append(evaluate_lane("post_observable_birth", str(state["freeze_ts_utc"])))
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
        "This is a forward-only observable loss-control watch; pre-birth rows are diagnostic and cannot promote any rule.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"delta {summary.get('delta_vs_current_cents')}c, suppressed {summary.get('suppressed_exits')}, "
            f"suppressed W/L {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}, "
            f"loss cost {summary.get('loss_control_cost_cents')}c, blockers {best.get('blockers')}."
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
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Exit Reduce Observable Loss-Control Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend([
            "| rank | candidate | settled | cand W/L | delta c | suppressed | suppressed W/L | winner recovery | loss cost | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, variant in enumerate(lane.get("variants") or [], start=1):
            summary = variant.get("summary") or {}
            lines.append(
                f"| {idx} | `{variant.get('candidate')}` | {summary.get('settled')} | "
                f"{summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
                f"{fmt(summary.get('delta_vs_current_cents'))} | {summary.get('suppressed_exits')} | "
                f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
                f"{fmt(summary.get('winner_clip_recovered_cents'))} | {fmt(summary.get('loss_control_cost_cents'))} | "
                f"{summary.get('full_loss_cushion_estimate')} | {', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Best Variant Suppressed Rows", ""])
        lines.extend([
            "| market | side | result | reason | entry | exit | p_hold | depth | stc | dur | book age | sigma | volshock | current c | hold c | delta | won |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in best.get("suppressed_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
                f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
                f"{fmt(row.get('entry_depth'))} | {fmt(row.get('entry_seconds_to_close'))} | "
                f"{fmt(row.get('trade_duration_sec'))} | {fmt(row.get('entry_book_age_ms'))} | "
                f"{fmt(row.get('exit_sigma_t_dollars'))} | {fmt(row.get('entry_volshock'))} | "
                f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
                f"{fmt(row.get('delta_cents'))} | {row.get('side_won')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
