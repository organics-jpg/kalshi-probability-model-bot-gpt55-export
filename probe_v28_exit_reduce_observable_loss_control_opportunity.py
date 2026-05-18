"""Opportunity denominator for observable reduce loss-control gates.

Research-only; no live bot changes or orders.

This explains whether the frozen observable loss-control watch is empty because
there were no post-birth exits, no probability-reduce exits, p_hold was too low,
features were missing, or the observable gates were genuinely not met.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import current_exit, exit_p_hold, exit_reason, hold_to_settlement, is_probability_reduce
from probe_v28_frozen_exit_reduce_observable_loss_control_watch import (
    RULES,
    STATE_JSON,
    as_float,
    entry_depth,
    entry_feature,
    exit_feature,
    future_rows,
    should_suppress,
    trade_duration_sec,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.md"


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


def value_fails(value: float | None, label: str, min_value: Any = None, max_value: Any = None) -> list[str]:
    if value is None:
        return [f"{label}_missing"]
    if min_value is not None and value < float(min_value):
        return [f"{label}_below_gate"]
    if max_value is not None and value > float(max_value):
        return [f"{label}_above_gate"]
    return []


def fail_reasons(row: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not is_probability_reduce(row):
        return ["not_probability_reduce"]
    p_hold = exit_p_hold(row)
    reasons.extend(value_fails(p_hold, "p_hold", min_value=rule.get("p_hold_min")))
    if reasons:
        return reasons

    if rule.get("entry_depth_max_or") is not None or rule.get("trade_duration_sec_max_or") is not None:
        depth_reasons = value_fails(entry_depth(row), "entry_depth", max_value=rule.get("entry_depth_max_or"))
        duration_reasons = value_fails(trade_duration_sec(row), "trade_duration_sec", max_value=rule.get("trade_duration_sec_max_or"))
        if depth_reasons and duration_reasons:
            reasons.extend([f"or_{reason}" for reason in depth_reasons + duration_reasons])
        return reasons

    checks = [
        ("entry_seconds_to_close", entry_feature(row, "mushroom_v28_seconds_to_close"), None, rule.get("entry_seconds_to_close_max")),
        ("trade_duration_sec", trade_duration_sec(row), None, rule.get("trade_duration_sec_max")),
        ("entry_book_age_ms", entry_feature(row, "mushroom_v28_book_age_ms"), rule.get("entry_book_age_ms_min"), None),
        ("exit_sigma_t_dollars", exit_feature(row, "mushroom_v28_sigma_t_dollars"), rule.get("exit_sigma_t_dollars_min"), None),
        ("exit_cents", as_float(row.get("exit_cents")), None, rule.get("exit_cents_max")),
        ("entry_volshock", entry_feature(row, "mushroom_v28_volshock"), rule.get("entry_volshock_min"), None),
        ("entry_depth", entry_depth(row), None, rule.get("entry_depth_max")),
    ]
    for label, value, min_value, max_value in checks:
        if min_value is None and max_value is None:
            continue
        reasons.extend(value_fails(value, label, min_value=min_value, max_value=max_value))
    return reasons


def compact(row: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": exit_reason(row),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "p_hold": exit_p_hold(row),
        "entry_depth": entry_depth(row),
        "entry_seconds_to_close": entry_feature(row, "mushroom_v28_seconds_to_close"),
        "trade_duration_sec": trade_duration_sec(row),
        "entry_book_age_ms": entry_feature(row, "mushroom_v28_book_age_ms"),
        "exit_sigma_t_dollars": exit_feature(row, "mushroom_v28_sigma_t_dollars"),
        "entry_volshock": entry_feature(row, "mushroom_v28_volshock"),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_if_suppressed_cents": None if cur is None or hold is None else float(hold) - float(cur),
        "would_suppress": should_suppress(row, rule),
        "fail_reasons": fail_reasons(row, rule),
    }


def evaluate_rule(rows: list[dict[str, Any]], name: str, rule: dict[str, Any]) -> dict[str, Any]:
    reduce_rows = [row for row in rows if is_probability_reduce(row)]
    p_hold_rows = [
        row for row in reduce_rows
        if exit_p_hold(row) is not None and float(exit_p_hold(row) or 0.0) >= float(rule.get("p_hold_min") or 0.0)
    ]
    would_suppress = [row for row in rows if should_suppress(row, rule)]
    reason_counts = Counter()
    for row in rows:
        for reason in fail_reasons(row, rule):
            reason_counts[reason] += 1
    return {
        "candidate": name,
        "rule": rule,
        "total_rows": len(rows),
        "probability_reduce_rows": len(reduce_rows),
        "p_hold_candidate_rows": len(p_hold_rows),
        "would_suppress_rows": len(would_suppress),
        "would_suppress_delta_cents": sum(
            float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
            for row in would_suppress
        ),
        "fail_reason_counts": dict(sorted(reason_counts.items())),
        "would_suppress_examples": [compact(row, rule) for row in would_suppress[:12]],
        "near_miss_examples": [compact(row, rule) for row in reduce_rows if not should_suppress(row, rule)][:12],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or utc_now_iso())
    rows = future_rows(freeze_ts)
    rules = [evaluate_rule(rows, name, rule) for name, rule in RULES.items()]
    report = {
        "generated_at_utc": utc_now_iso(),
        "observable_loss_control_freeze_ts_utc": freeze_ts,
        "post_birth_rows": len(rows),
        "rules": rules,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This report only explains opportunity availability for the frozen observable loss-control watch.",
    ]
    for row in report.get("rules") or []:
        notes.append(
            f"{row.get('candidate')}: post-birth rows {row.get('total_rows')}, "
            f"probability-reduce rows {row.get('probability_reduce_rows')}, "
            f"p_hold candidates {row.get('p_hold_candidate_rows')}, "
            f"would-suppress rows {row.get('would_suppress_rows')}, "
            f"delta if suppressed {row.get('would_suppress_delta_cents')}c, "
            f"fail reasons {row.get('fail_reason_counts')}."
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
        "# v28 Exit Reduce Observable Loss-Control Opportunity",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('observable_loss_control_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Rules",
        "",
        "| candidate | rows | reduce rows | p-hold candidates | would suppress | delta if suppressed | fail reasons |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rules") or []:
        lines.append(
            f"| `{row.get('candidate')}` | {row.get('total_rows')} | {row.get('probability_reduce_rows')} | "
            f"{row.get('p_hold_candidate_rows')} | {row.get('would_suppress_rows')} | "
            f"{fmt(row.get('would_suppress_delta_cents'))} | {row.get('fail_reason_counts')} |"
        )
    best = (report.get("rules") or [{}])[0]
    lines.extend(["", "## First-Rule Near Misses", ""])
    lines.extend([
        "| market | side | result | reason | entry | exit | p_hold | depth | stc | dur | book age | sigma | volshock | delta if suppressed | fail reasons |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in best.get("near_miss_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('entry_depth'))} | {fmt(row.get('entry_seconds_to_close'))} | "
            f"{fmt(row.get('trade_duration_sec'))} | {fmt(row.get('entry_book_age_ms'))} | "
            f"{fmt(row.get('exit_sigma_t_dollars'))} | {fmt(row.get('entry_volshock'))} | "
            f"{fmt(row.get('delta_if_suppressed_cents'))} | {', '.join(row.get('fail_reasons') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
