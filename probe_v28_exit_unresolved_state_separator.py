"""Diagnostic separator for v28 unresolved matched exit-loss rows.

Research-only; no live bot changes or orders.

The exit-repair gap classifier shows that many matched-but-unchanged losses
would have been better if the bot had held, while a smaller group would have
become worse. This probe asks whether observable entry/exit state can separate
those groups before adding any new frozen exit watch.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
GAP_CLASSIFIER_JSON = OUT_DIR / "v28_exit_repair_gap_classifier_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_unresolved_state_separator_latest.json"
OUT_MD = OUT_DIR / "v28_exit_unresolved_state_separator_latest.md"


NUMERIC_FEATURES = {
    "p_hold": lambda row: (row.get("best_policy_effect") or {}).get("p_hold"),
    "fair_drawdown_cents": lambda row: (row.get("best_policy_effect") or {}).get("fair_drawdown_cents"),
    "exit_cents": lambda row: (row.get("best_policy_effect") or {}).get("exit_cents") or row.get("exit_cents"),
    "p_side": lambda row: row.get("p_side"),
    "raw_edge_cents": lambda row: row.get("raw_edge_cents"),
    "ask_cents": lambda row: row.get("ask_cents"),
    "abs_d_sigma": lambda row: row.get("abs_d_sigma"),
    "recross_hazard_score": lambda row: row.get("recross_hazard_score"),
    "eligible_depth": lambda row: row.get("eligible_depth"),
}

NICE_THRESHOLDS = {
    "p_hold": [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
    "fair_drawdown_cents": [-10.0, -5.0, 0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0, 40.0],
    "exit_cents": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 90.0],
    "p_side": [0.80, 0.85, 0.875, 0.90, 0.925, 0.95],
    "raw_edge_cents": [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0],
    "ask_cents": [50.0, 60.0, 65.0, 68.0, 70.0, 75.0, 80.0, 85.0, 90.0],
    "abs_d_sigma": [0.75, 0.85, 0.90, 1.00, 1.10, 1.25, 1.50],
    "recross_hazard_score": [0.10, 0.20, 0.30, 0.40, 0.50, 0.60],
    "eligible_depth": [2.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 5000.0],
}

CATEGORICAL_FEATURES = {
    "side": lambda row: row.get("side"),
    "exit_reason": lambda row: (row.get("best_policy_effect") or {}).get("exit_reason") or row.get("exit_reason") or "unknown",
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


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    best = row.get("best_policy_effect") or {}
    delta = hold_delta(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "failure_class": row.get("failure_class"),
        "actual_gross_cents": row.get("actual_gross_cents"),
        "hold_gross_cents": row.get("hold_gross_cents"),
        "hold_delta_cents": delta,
        "exit_reason": best.get("exit_reason") or row.get("exit_reason") or "unknown",
        "exit_cents": best.get("exit_cents") or row.get("exit_cents"),
        "p_hold": best.get("p_hold"),
        "fair_drawdown_cents": best.get("fair_drawdown_cents"),
        "p_side": row.get("p_side"),
        "raw_edge_cents": row.get("raw_edge_cents"),
        "ask_cents": row.get("ask_cents"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "eligible_depth": row.get("eligible_depth"),
        "physics_tags": row.get("physics_tags") or [],
    }


def pct(part: int, total: int) -> float | None:
    if not total:
        return None
    return part / total * 100.0


class Condition:
    def __init__(self, label: str, predicate: Callable[[dict[str, Any]], bool], feature: str, is_nice: bool = False):
        self.label = label
        self.predicate = predicate
        self.feature = feature
        self.is_nice = is_nice


def build_conditions(rows: list[dict[str, Any]]) -> list[Condition]:
    conditions: list[Condition] = []
    for feature, getter in NUMERIC_FEATURES.items():
        values = sorted({
            value for row in rows
            if (value := as_float(getter(row))) is not None
        })
        if not values:
            continue
        low = values[0]
        high = values[-1]
        nice = [
            threshold for threshold in NICE_THRESHOLDS.get(feature, [])
            if low <= threshold <= high
        ]
        for threshold in sorted(set(values + nice)):
            is_nice = threshold in nice
            conditions.append(Condition(
                f"{feature} le {threshold:.6g}",
                lambda row, getter=getter, threshold=threshold: (
                    (value := as_float(getter(row))) is not None and value <= threshold
                ),
                feature,
                is_nice,
            ))
            conditions.append(Condition(
                f"{feature} ge {threshold:.6g}",
                lambda row, getter=getter, threshold=threshold: (
                    (value := as_float(getter(row))) is not None and value >= threshold
                ),
                feature,
                is_nice,
            ))
    for feature, getter in CATEGORICAL_FEATURES.items():
        values = sorted({str(getter(row) or "unknown") for row in rows})
        for value in values:
            conditions.append(Condition(
                f"{feature} eq {value}",
                lambda row, getter=getter, value=value: str(getter(row) or "unknown") == value,
                feature,
                True,
            ))
    return conditions


def evaluate_rule(
    name: str,
    conditions: list[Condition],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    selected = [row for row in rows if all(condition.predicate(row) for condition in conditions)]
    known = [row for row in selected if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    neutral = [row for row in known if (hold_delta(row) or 0.0) == 0.0]
    failure_counts = Counter(str(row.get("failure_class") or "unknown") for row in selected)
    actual_loss = sum(as_float(row.get("actual_gross_cents")) or 0.0 for row in selected)
    total_hold_delta = sum(hold_delta(row) or 0.0 for row in known)
    blockers = []
    if len(selected) < 5:
        blockers.append("selected_rows_lt_5")
    if harmful:
        blockers.append("harmful_hold_rows_present")
    if len(rows) < 30:
        blockers.append("sample_lt_30")
    blockers.extend(["diagnostic_not_frozen", "no_post_freeze_evidence"])
    return {
        "rule": name,
        "conditions": [condition.label for condition in conditions],
        "nice_threshold_rule": all(condition.is_nice for condition in conditions),
        "selected_rows": len(selected),
        "helpful_hold_rows": len(helpful),
        "harmful_hold_rows": len(harmful),
        "neutral_hold_rows": len(neutral),
        "unknown_hold_rows": len(selected) - len(known),
        "helpful_share": pct(len(helpful), len(known)),
        "actual_loss_cents_selected": actual_loss,
        "hold_delta_cents_selected": total_hold_delta,
        "failure_class_counts": dict(failure_counts),
        "blockers": blockers,
        "examples": [compact_row(row) for row in sorted(
            selected,
            key=lambda item: hold_delta(item) or 0.0,
            reverse=True,
        )[:8]],
    }


def feature_ranges(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_class[str(row.get("failure_class") or "unknown")].append(row)
    out = []
    for feature, getter in NUMERIC_FEATURES.items():
        record: dict[str, Any] = {"feature": feature}
        for label, group in sorted(by_class.items()):
            values = sorted(
                value for row in group
                if (value := as_float(getter(row))) is not None
            )
            if not values:
                record[label] = None
                continue
            record[label] = {
                "min": values[0],
                "median": values[len(values) // 2],
                "max": values[-1],
                "rows": len(values),
            }
        out.append(record)
    return out


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    known = [row for row in rows if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    by_failure: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_failure[str(row.get("failure_class") or "unknown")].append(row)
    return {
        "rows": len(rows),
        "known_hold_rows": len(known),
        "hold_helpful_rows": len(helpful),
        "hold_harmful_rows": len(harmful),
        "hold_unknown_rows": len(rows) - len(known),
        "actual_loss_cents": sum(as_float(row.get("actual_gross_cents")) or 0.0 for row in rows),
        "hold_delta_cents": sum(hold_delta(row) or 0.0 for row in known),
        "by_failure_class": {
            label: {
                "rows": len(group),
                "hold_helpful_rows": sum(1 for row in group if (hold_delta(row) or 0.0) > 0.0),
                "hold_harmful_rows": sum(1 for row in group if (hold_delta(row) or 0.0) < 0.0),
                "actual_loss_cents": sum(as_float(row.get("actual_gross_cents")) or 0.0 for row in group),
                "hold_delta_cents": sum(hold_delta(row) or 0.0 for row in group if hold_delta(row) is not None),
            }
            for label, group in sorted(by_failure.items())
        },
    }


def build_report() -> dict[str, Any]:
    loss_escape = load_json(LOSS_ESCAPE_JSON)
    gap = load_json(GAP_CLASSIFIER_JSON)
    rows = [
        row for row in loss_escape.get("loss_rows_with_details") or []
        if row.get("escape_class") == "loss_escapes_current_exit_repairs"
        and (row.get("best_policy_effect") or {}).get("matched") is True
        and hold_delta(row) is not None
    ]
    first_freeze = parse_ts(gap.get("first_exit_repair_freeze_ts_utc"))
    post_first_freeze = [
        row for row in rows
        if first_freeze is not None
        and (parse_ts(row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc)) >= first_freeze
    ]
    conditions = build_conditions(rows)
    single_rules = [evaluate_rule(condition.label, [condition], rows) for condition in conditions]
    top_single_conditions = [
        condition for _, condition in sorted(
            zip(single_rules, conditions),
            key=lambda item: (
                item[0]["harmful_hold_rows"] == 0,
                item[0]["selected_rows"] >= 3,
                item[0]["hold_delta_cents_selected"],
                item[0]["selected_rows"],
            ),
            reverse=True,
        )[:50]
    ]
    pair_rules = []
    seen_pairs: set[tuple[str, str]] = set()
    for idx, left in enumerate(top_single_conditions):
        for right in top_single_conditions[idx + 1:]:
            pair_key = tuple(sorted((left.label, right.label)))
            if pair_key in seen_pairs or left.feature == right.feature:
                continue
            seen_pairs.add(pair_key)
            pair_rules.append(evaluate_rule(f"{left.label} and {right.label}", [left, right], rows))
    all_rules = single_rules + pair_rules
    clean_rules = [
        rule for rule in all_rules
        if rule["selected_rows"] >= 3 and rule["harmful_hold_rows"] == 0 and rule["hold_delta_cents_selected"] > 0.0
    ]
    tradeoff_rules = [
        rule for rule in all_rules
        if rule["selected_rows"] >= 5 and rule["hold_delta_cents_selected"] > 0.0
    ]
    clean_rules.sort(key=lambda rule: (rule["hold_delta_cents_selected"], rule["selected_rows"]), reverse=True)
    tradeoff_rules.sort(
        key=lambda rule: (
            -rule["harmful_hold_rows"],
            rule["hold_delta_cents_selected"],
            rule["selected_rows"],
        ),
        reverse=True,
    )
    nice_clean_rules = [rule for rule in clean_rules if rule.get("nice_threshold_rule")]
    nice_tradeoff_rules = [rule for rule in tradeoff_rules if rule.get("nice_threshold_rule")]
    best_clean = clean_rules[0] if clean_rules else None
    best_tradeoff = tradeoff_rules[0] if tradeoff_rules else None
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(LOSS_ESCAPE_JSON),
        "gap_classifier_source": str(GAP_CLASSIFIER_JSON),
        "scope": "matched_but_unchanged_loss_rows_only",
        "research_only": True,
        "first_exit_repair_freeze_ts_utc": gap.get("first_exit_repair_freeze_ts_utc"),
        "summary": summarize_rows(rows),
        "post_first_exit_repair_freeze_summary": summarize_rows(post_first_freeze),
        "feature_ranges": feature_ranges(rows),
        "best_clean_diagnostic_rule": best_clean,
        "best_tradeoff_diagnostic_rule": best_tradeoff,
        "best_nice_clean_diagnostic_rule": nice_clean_rules[0] if nice_clean_rules else None,
        "best_nice_tradeoff_diagnostic_rule": nice_tradeoff_rules[0] if nice_tradeoff_rules else None,
        "top_clean_diagnostic_rules": clean_rules[:12],
        "top_tradeoff_diagnostic_rules": tradeoff_rules[:12],
        "top_nice_clean_diagnostic_rules": nice_clean_rules[:12],
        "top_nice_tradeoff_diagnostic_rules": nice_tradeoff_rules[:12],
        "interpretation": [
            "This is a diagnostic separator only; it is selected on known loss rows and cannot be promoted.",
            "A useful next step is to freeze one simple observable rule only if the physical mechanism is defensible.",
            "Any frozen rule must then earn post-freeze suppressions, positive delta, no harmful loss-control cost, and enough cushion.",
        ],
    }


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "None"
    return f"{number:.0f}"


def fmt_num(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "None"
    return f"{number:.3f}"


def pct_fmt(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "None"
    return f"{number:.2f}%"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    summary = report.get("summary") or {}
    post = report.get("post_first_exit_repair_freeze_summary") or {}
    lines = [
        "# v28 Exit Unresolved State Separator",
        "",
        "Research-only diagnostic; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Scope: `{report.get('scope')}`",
        f"- Rows: `{summary.get('rows')}`",
        f"- Hold helpful/harmful: `{summary.get('hold_helpful_rows')}/{summary.get('hold_harmful_rows')}`",
        f"- Actual loss selected universe: `{fmt_cents(summary.get('actual_loss_cents'))}c`",
        f"- Hindsight hold delta in universe: `{fmt_cents(summary.get('hold_delta_cents'))}c`",
        f"- Post first repair-freeze rows: `{post.get('rows')}`",
        "",
        "## Interpretation",
        "",
    ]
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    lines.extend(["", "## Failure Split", "", "| failure class | rows | hold helpful | hold harmful | actual loss c | hold delta c |", "|---|---:|---:|---:|---:|---:|"])
    for label, row in (summary.get("by_failure_class") or {}).items():
        lines.append(
            f"| {label} | {row.get('rows')} | {row.get('hold_helpful_rows')} | "
            f"{row.get('hold_harmful_rows')} | {fmt_cents(row.get('actual_loss_cents'))} | "
            f"{fmt_cents(row.get('hold_delta_cents'))} |"
        )
    best_clean = report.get("best_clean_diagnostic_rule")
    if best_clean:
        lines.extend(["", "## Best Clean Diagnostic Rule", "", "| field | value |", "|---|---:|"])
        lines.append(f"| rule | `{best_clean.get('rule')}` |")
        lines.append(f"| selected rows | {best_clean.get('selected_rows')} |")
        lines.append(f"| helpful/harmful | {best_clean.get('helpful_hold_rows')}/{best_clean.get('harmful_hold_rows')} |")
        lines.append(f"| hold delta c | {fmt_cents(best_clean.get('hold_delta_cents_selected'))} |")
        lines.append(f"| actual loss c | {fmt_cents(best_clean.get('actual_loss_cents_selected'))} |")
        lines.append(f"| blockers | `{', '.join(best_clean.get('blockers') or [])}` |")
    best_nice = report.get("best_nice_clean_diagnostic_rule")
    if best_nice:
        lines.extend(["", "## Best Rounded Clean Diagnostic Rule", "", "| field | value |", "|---|---:|"])
        lines.append(f"| rule | `{best_nice.get('rule')}` |")
        lines.append(f"| selected rows | {best_nice.get('selected_rows')} |")
        lines.append(f"| helpful/harmful | {best_nice.get('helpful_hold_rows')}/{best_nice.get('harmful_hold_rows')} |")
        lines.append(f"| hold delta c | {fmt_cents(best_nice.get('hold_delta_cents_selected'))} |")
        lines.append(f"| actual loss c | {fmt_cents(best_nice.get('actual_loss_cents_selected'))} |")
        lines.append(f"| blockers | `{', '.join(best_nice.get('blockers') or [])}` |")
    best_tradeoff = report.get("best_tradeoff_diagnostic_rule")
    if best_tradeoff:
        lines.extend(["", "## Best Tradeoff Diagnostic Rule", "", "| field | value |", "|---|---:|"])
        lines.append(f"| rule | `{best_tradeoff.get('rule')}` |")
        lines.append(f"| selected rows | {best_tradeoff.get('selected_rows')} |")
        lines.append(f"| helpful/harmful | {best_tradeoff.get('helpful_hold_rows')}/{best_tradeoff.get('harmful_hold_rows')} |")
        lines.append(f"| helpful share | {pct_fmt(best_tradeoff.get('helpful_share'))} |")
        lines.append(f"| hold delta c | {fmt_cents(best_tradeoff.get('hold_delta_cents_selected'))} |")
        lines.append(f"| actual loss c | {fmt_cents(best_tradeoff.get('actual_loss_cents_selected'))} |")
        lines.append(f"| blockers | `{', '.join(best_tradeoff.get('blockers') or [])}` |")
    lines.extend(["", "## Top Clean Diagnostic Rules", "", "| rule | rows | helpful | harmful | hold delta c | actual loss c |", "|---|---:|---:|---:|---:|---:|"])
    for rule in (report.get("top_clean_diagnostic_rules") or [])[:10]:
        lines.append(
            f"| `{rule.get('rule')}` | {rule.get('selected_rows')} | {rule.get('helpful_hold_rows')} | "
            f"{rule.get('harmful_hold_rows')} | {fmt_cents(rule.get('hold_delta_cents_selected'))} | "
            f"{fmt_cents(rule.get('actual_loss_cents_selected'))} |"
        )
    lines.extend(["", "## Top Rounded Clean Diagnostic Rules", "", "| rule | rows | helpful | harmful | hold delta c | actual loss c |", "|---|---:|---:|---:|---:|---:|"])
    for rule in (report.get("top_nice_clean_diagnostic_rules") or [])[:10]:
        lines.append(
            f"| `{rule.get('rule')}` | {rule.get('selected_rows')} | {rule.get('helpful_hold_rows')} | "
            f"{rule.get('harmful_hold_rows')} | {fmt_cents(rule.get('hold_delta_cents_selected'))} | "
            f"{fmt_cents(rule.get('actual_loss_cents_selected'))} |"
        )
    lines.extend(["", "## Feature Ranges", "", "| feature | exit_policy_cost median | fv_or_entry_timing_error median |", "|---|---:|---:|"])
    for record in report.get("feature_ranges") or []:
        exit_policy = record.get("exit_policy_cost") or {}
        fv_error = record.get("fv_or_entry_timing_error") or {}
        lines.append(f"| {record.get('feature')} | {fmt_num(exit_policy.get('median'))} | {fmt_num(fv_error.get('median'))} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
