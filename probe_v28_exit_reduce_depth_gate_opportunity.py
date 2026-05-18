"""Opportunity denominator for the frozen exit reduce entry-depth gate.

Research-only; no live bot changes or orders.

The depth-gate post-birth watch can show zero suppressed exits for several
different reasons: no probability-reduce exits occurred, p_hold was below the
floor, entry depth was too deep, or required features were missing. This report
keeps those causes separate without changing or searching exit rules.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import build_rows, current_exit, exit_p_hold, exit_reason, hold_to_settlement, is_probability_reduce
from probe_v28_frozen_exit_reduce_depth_gate import RULES, STATE_JSON, entry_depth, parse_ts, should_suppress


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.md"


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows: list[dict[str, Any]] = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def fail_reasons(row: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not is_probability_reduce(row):
        reasons.append("not_probability_reduce")
        return reasons
    p_hold = exit_p_hold(row)
    if p_hold is None:
        reasons.append("p_hold_missing")
    elif p_hold < float(rule.get("p_hold_min") or 0.0):
        reasons.append("p_hold_below_floor")
    depth = entry_depth(row)
    if depth is None:
        reasons.append("entry_depth_missing")
    elif depth > float(rule.get("entry_depth_max") or 0.0):
        reasons.append("entry_depth_above_gate")
    drawdown_max = rule.get("drawdown_max")
    if drawdown_max is not None:
        # Import lazily through the depth-gate rule behavior by matching its reason shape.
        from probe_v28_exit_policy_candidates import exit_fair_drawdown

        drawdown = exit_fair_drawdown(row)
        if drawdown is None:
            reasons.append("fair_drawdown_missing")
        elif drawdown > float(drawdown_max):
            reasons.append("fair_drawdown_above_gate")
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
        "current_cents": cur,
        "hold_cents": hold,
        "delta_if_suppressed_cents": None if cur is None or hold is None else float(hold) - float(cur),
        "would_suppress": should_suppress(row, rule),
        "fail_reasons": fail_reasons(row, rule),
    }


def evaluate_rule(rows: list[dict[str, Any]], name: str, rule: dict[str, Any]) -> dict[str, Any]:
    reduce_rows = [row for row in rows if is_probability_reduce(row)]
    would_suppress = [row for row in rows if should_suppress(row, rule)]
    reason_counts = Counter()
    for row in rows:
        for reason in fail_reasons(row, rule):
            reason_counts[reason] += 1
    p_hold_floor = float(rule.get("p_hold_min") or 0.0)
    depth_gate = float(rule.get("entry_depth_max") or 0.0)
    p_hold_candidates = [
        row for row in reduce_rows
        if (exit_p_hold(row) is not None and float(exit_p_hold(row) or 0.0) >= p_hold_floor)
    ]
    depth_candidates = [
        row for row in p_hold_candidates
        if (entry_depth(row) is not None and float(entry_depth(row) or 0.0) <= depth_gate)
    ]
    return {
        "candidate": name,
        "rule": rule,
        "total_rows": len(rows),
        "probability_reduce_rows": len(reduce_rows),
        "p_hold_candidate_rows": len(p_hold_candidates),
        "entry_depth_candidate_rows": len(depth_candidates),
        "would_suppress_rows": len(would_suppress),
        "fail_reason_counts": dict(sorted(reason_counts.items())),
        "would_suppress_examples": [compact(row, rule) for row in would_suppress[:12]],
        "near_miss_examples": [
            compact(row, rule)
            for row in reduce_rows
            if not should_suppress(row, rule)
        ][:12],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or utc_now_iso())
    rows = future_rows(freeze_ts)
    rules = [evaluate_rule(rows, name, rule) for name, rule in RULES.items()]
    report = {
        "generated_at_utc": utc_now_iso(),
        "depth_gate_freeze_ts_utc": freeze_ts,
        "post_birth_rows": len(rows),
        "rules": rules,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This report only explains opportunity availability for the frozen depth gate; it does not change exit behavior.",
    ]
    for row in report.get("rules") or []:
        notes.append(
            f"{row.get('candidate')}: post-birth rows {row.get('total_rows')}, "
            f"probability-reduce rows {row.get('probability_reduce_rows')}, "
            f"p_hold candidates {row.get('p_hold_candidate_rows')}, "
            f"depth candidates {row.get('entry_depth_candidate_rows')}, "
            f"would-suppress rows {row.get('would_suppress_rows')}, "
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
        "# v28 Exit Reduce Depth-Gate Opportunity Denominator",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Depth-gate freeze UTC: `{report.get('depth_gate_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "| candidate | rows | reduce rows | p-hold candidates | depth candidates | would suppress | fail reasons |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rules") or []:
        lines.append(
            f"| {row.get('candidate')} | {row.get('total_rows')} | {row.get('probability_reduce_rows')} | "
            f"{row.get('p_hold_candidate_rows')} | {row.get('entry_depth_candidate_rows')} | "
            f"{row.get('would_suppress_rows')} | {row.get('fail_reason_counts')} |"
        )
    best = (report.get("rules") or [{}])[0]
    lines.extend(["", "## First-Rule Near Misses", ""])
    lines.extend(
        [
            "| market | side | result | reason | entry | exit | p_hold | depth | current c | hold c | delta if suppressed | fail reasons |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in best.get("near_miss_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('entry_depth'))} | {fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
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
