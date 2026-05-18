"""Audit harmful suppressions in the shallow-drawdown exit watch.

Research-only; no live bot changes or orders.

The frozen shallow-drawdown watch is intentionally broad enough to expose
failure modes. This diagnostic searches for observable child guards that keep
the clipped-winner recovery while removing known harmful suppressions.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
)
from probe_v28_frozen_exit_reduce_depth_gate import entry_depth
from probe_v28_frozen_exit_shallow_drawdown_watch import (
    COLLAPSE,
    SOFT_REDUCE,
    rows_after,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_REDUCE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_exit_shallow_drawdown_harm_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_shallow_drawdown_harm_audit_latest.md"

BASE_REASONS = {SOFT_REDUCE, COLLAPSE}
DRAW_MAX = 5.0


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


def entry_feature(row: dict[str, Any], key: str) -> float | None:
    features = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    return as_float(features.get(key))


def exit_feature(row: dict[str, Any], key: str) -> float | None:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return as_float(features.get(key))


def trade_duration_sec(row: dict[str, Any]) -> float | None:
    entry = parse_ts(row.get("entry_ts"))
    exit_ts = parse_ts(row.get("exit_ts"))
    if entry is None or exit_ts is None:
        return None
    return (exit_ts - entry).total_seconds()


def delta_if_suppressed(row: dict[str, Any]) -> float | None:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    if cur is None or hold is None:
        return None
    return hold - cur


def base_selected(row: dict[str, Any]) -> bool:
    drawdown = exit_fair_drawdown(row)
    return (
        exit_reason(row) in BASE_REASONS
        and drawdown is not None
        and drawdown <= DRAW_MAX
    )


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": exit_reason(row),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "current_cents": current_exit(row),
        "hold_cents": hold_to_settlement(row),
        "delta_if_suppressed_cents": delta_if_suppressed(row),
        "p_hold": exit_p_hold(row),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "entry_abs_d_sigma": entry_feature(row, "mushroom_v28_abs_d_sigma"),
        "entry_raw_edge_cents": entry_feature(row, "mushroom_v28_raw_edge_cents"),
        "entry_seconds_to_close": entry_feature(row, "mushroom_v28_seconds_to_close"),
        "entry_depth": entry_depth(row),
        "duration_sec": trade_duration_sec(row),
        "exit_sigma_t_dollars": exit_feature(row, "mushroom_v28_sigma_t_dollars"),
    }


class Condition:
    def __init__(self, label: str, predicate: Callable[[dict[str, Any]], bool], feature: str):
        self.label = label
        self.predicate = predicate
        self.feature = feature


FEATURES: dict[str, Callable[[dict[str, Any]], float | None]] = {
    "p_hold": exit_p_hold,
    "fair_drawdown_cents": exit_fair_drawdown,
    "exit_cents": lambda row: as_float(row.get("exit_cents")),
    "entry_cents": lambda row: as_float(row.get("entry_cents")),
    "entry_abs_d_sigma": lambda row: entry_feature(row, "mushroom_v28_abs_d_sigma"),
    "entry_raw_edge_cents": lambda row: entry_feature(row, "mushroom_v28_raw_edge_cents"),
    "entry_seconds_to_close": lambda row: entry_feature(row, "mushroom_v28_seconds_to_close"),
    "entry_depth": entry_depth,
    "duration_sec": trade_duration_sec,
    "exit_sigma_t_dollars": lambda row: exit_feature(row, "mushroom_v28_sigma_t_dollars"),
}

NICE_THRESHOLDS = {
    "p_hold": [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90],
    "fair_drawdown_cents": [-5.0, 0.0, 2.5, 5.0],
    "exit_cents": [40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0],
    "entry_cents": [50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0],
    "entry_abs_d_sigma": [0.75, 0.85, 0.90, 1.0, 1.1],
    "entry_raw_edge_cents": [0.0, 5.0, 10.0, 15.0, 20.0, 25.0],
    "entry_seconds_to_close": [60.0, 120.0, 240.0, 360.0, 596.0, 720.0],
    "entry_depth": [2.0, 25.0, 50.0, 100.0, 250.0, 384.0, 500.0, 1000.0],
    "duration_sec": [15.0, 30.0, 52.0, 75.0, 120.0, 180.0, 300.0],
    "exit_sigma_t_dollars": [50.0, 75.0, 100.0, 125.0, 150.0],
}


def build_conditions(rows: list[dict[str, Any]]) -> list[Condition]:
    conditions = [
        Condition("exit_reason eq probability_reduce", lambda row: exit_reason(row) == SOFT_REDUCE, "exit_reason"),
        Condition("exit_reason eq collapse_full", lambda row: exit_reason(row) == COLLAPSE, "exit_reason"),
    ]
    for feature, getter in FEATURES.items():
        values = [value for row in rows if (value := as_float(getter(row))) is not None]
        if not values:
            continue
        low, high = min(values), max(values)
        thresholds = [value for value in NICE_THRESHOLDS.get(feature, []) if low <= value <= high]
        for threshold in thresholds:
            conditions.append(Condition(
                f"{feature} le {threshold:g}",
                lambda row, getter=getter, threshold=threshold: (
                    (value := as_float(getter(row))) is not None and value <= threshold
                ),
                feature,
            ))
            conditions.append(Condition(
                f"{feature} ge {threshold:g}",
                lambda row, getter=getter, threshold=threshold: (
                    (value := as_float(getter(row))) is not None and value >= threshold
                ),
                feature,
            ))
    return conditions


def evaluate(name: str, conditions: list[Condition], rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [
        row for row in rows
        if base_selected(row) and all(condition.predicate(row) for condition in conditions)
    ]
    deltas = [delta_if_suppressed(row) for row in selected if delta_if_suppressed(row) is not None]
    helpful = [value for value in deltas if value > 0.0]
    harmful = [value for value in deltas if value < 0.0]
    current = sum(current_exit(row) or 0.0 for row in rows)
    candidate = sum(
        (hold_to_settlement(row) if row in selected else current_exit(row)) or 0.0
        for row in rows
    )
    blockers = ["diagnostic_prefreeze"]
    if len(selected) < 3:
        blockers.append("selected_lt_3")
    if len(harmful) > 0:
        blockers.append("harmful_suppressed_present")
    return {
        "rule": name,
        "conditions": [condition.label for condition in conditions],
        "selected": len(selected),
        "helpful": len(helpful),
        "harmful": len(harmful),
        "delta_cents": candidate - current,
        "selected_delta_cents": sum(deltas),
        "loss_control_cost_cents": sum(harmful),
        "current_gross_cents": current,
        "candidate_gross_cents": candidate,
        "suppressed_exit_reason_counts": dict(Counter(exit_reason(row) for row in selected)),
        "blockers": blockers,
        "examples": [compact(row) for row in sorted(selected, key=lambda item: delta_if_suppressed(item) or 0.0)[:8]],
    }


def build_report() -> dict[str, Any]:
    base_state = load_json(BASE_REDUCE_STATE_JSON)
    rows = rows_after(build_rows(), base_state.get("freeze_ts_utc"))
    base_rows = [row for row in rows if base_selected(row)]
    harmful_rows = [row for row in base_rows if (delta_if_suppressed(row) or 0.0) < 0.0]
    helpful_rows = [row for row in base_rows if (delta_if_suppressed(row) or 0.0) > 0.0]
    conditions = build_conditions(base_rows)
    single = [evaluate(condition.label, [condition], rows) for condition in conditions]
    top_conditions = [
        condition for _, condition in sorted(
            zip(single, conditions),
            key=lambda item: (
                item[0]["harmful"] == 0,
                item[0]["selected_delta_cents"],
                item[0]["selected"],
            ),
            reverse=True,
        )[:40]
    ]
    pairs = []
    seen: set[tuple[str, str]] = set()
    for idx, left in enumerate(top_conditions):
        for right in top_conditions[idx + 1:]:
            if left.feature == right.feature:
                continue
            key = tuple(sorted((left.label, right.label)))
            if key in seen:
                continue
            seen.add(key)
            pairs.append(evaluate(f"{left.label} and {right.label}", [left, right], rows))
    rules = single + pairs
    clean = [
        rule for rule in rules
        if rule["selected"] >= 3 and rule["harmful"] == 0 and rule["selected_delta_cents"] > 0.0
    ]
    tradeoff = [
        rule for rule in rules
        if rule["selected"] >= 5 and rule["selected_delta_cents"] > 0.0
    ]
    clean.sort(key=lambda row: (row["selected_delta_cents"], row["selected"]), reverse=True)
    tradeoff.sort(key=lambda row: (-row["harmful"], row["selected_delta_cents"], row["selected"]), reverse=True)
    return {
        "generated_at_utc": utc_now_iso(),
        "base_reduce_freeze_ts_utc": base_state.get("freeze_ts_utc"),
        "scope": "diagnostic_after_reduce_freeze_shallow_drawdown_reduce_or_collapse_lte5",
        "summary": {
            "denominator_rows": len(rows),
            "base_selected_rows": len(base_rows),
            "base_helpful": len(helpful_rows),
            "base_harmful": len(harmful_rows),
            "base_selected_delta_cents": sum(delta_if_suppressed(row) or 0.0 for row in base_rows),
        },
        "harmful_examples": [compact(row) for row in harmful_rows],
        "helpful_examples": [compact(row) for row in sorted(helpful_rows, key=lambda item: delta_if_suppressed(item) or 0.0, reverse=True)[:12]],
        "best_clean_child_rule": clean[0] if clean else None,
        "best_tradeoff_child_rule": tradeoff[0] if tradeoff else None,
        "top_clean_child_rules": clean[:12],
        "top_tradeoff_child_rules": tradeoff[:12],
        "interpretation": [
            "Diagnostic only; every rule here was chosen after seeing known outcomes.",
            "Clean child rules are candidates for separate frozen watches only if the physical mechanism is defensible.",
            "Promotion still requires strict post-freeze rows, positive delta, no harmful loss-control cost, and enough cushion.",
        ],
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return "None" if value is None else str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    lines = [
        "# v28 Exit Shallow-Drawdown Harm Audit",
        "",
        "Research-only diagnostic; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Base reduce freeze UTC: `{report.get('base_reduce_freeze_ts_utc')}`",
        f"- Denominator rows: `{summary.get('denominator_rows')}`",
        f"- Base selected/helpful/harmful: `{summary.get('base_selected_rows')}/{summary.get('base_helpful')}/{summary.get('base_harmful')}`",
        f"- Base selected delta: `{fmt(summary.get('base_selected_delta_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    for title, key in [
        ("Best Clean Child Rule", "best_clean_child_rule"),
        ("Best Tradeoff Child Rule", "best_tradeoff_child_rule"),
    ]:
        rule = report.get(key) or {}
        lines.extend(["", f"## {title}", "", "| field | value |", "|---|---:|"])
        lines.append(f"| rule | `{rule.get('rule')}` |")
        lines.append(f"| selected | {rule.get('selected')} |")
        lines.append(f"| helpful/harmful | {rule.get('helpful')}/{rule.get('harmful')} |")
        lines.append(f"| selected delta c | {fmt(rule.get('selected_delta_cents'))} |")
        lines.append(f"| total delta c | {fmt(rule.get('delta_cents'))} |")
        lines.append(f"| loss cost c | {fmt(rule.get('loss_control_cost_cents'))} |")
        lines.append(f"| blockers | `{', '.join(rule.get('blockers') or [])}` |")
    lines.extend([
        "",
        "## Top Clean Child Rules",
        "",
        "| rule | selected | helpful | harmful | selected delta c | total delta c | reasons |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for rule in report.get("top_clean_child_rules") or []:
        lines.append(
            f"| `{rule.get('rule')}` | {rule.get('selected')} | {rule.get('helpful')} | {rule.get('harmful')} | "
            f"{fmt(rule.get('selected_delta_cents'))} | {fmt(rule.get('delta_cents'))} | {rule.get('suppressed_exit_reason_counts')} |"
        )
    lines.extend([
        "",
        "## Harmful Base Examples",
        "",
        "| market | side | result | reason | current | hold | delta | p_hold | drawdown | entry | exit | duration |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("harmful_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('delta_if_suppressed_cents'))} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('entry_cents'))} | "
            f"{fmt(row.get('exit_cents'))} | {fmt(row.get('duration_sec'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
