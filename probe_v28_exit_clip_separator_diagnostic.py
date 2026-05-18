"""Diagnostic separator for unresolved v28 exit-policy clip losses.

Research-only; no live bot changes or orders.

The control risk-stop is currently loss-count churn, not account drawdown. The
gap classifier shows two different states inside remaining matched losses:
exit-policy clips where holding would have helped, and FV/entry-timing losses
where holding would have hurt. This probe searches simple observable exit-state
rules that separate those states. It is diagnostic only; any deployable rule
must be frozen separately and earn forward rows.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
GAP_JSON = OUT_DIR / "v28_exit_repair_gap_classifier_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_clip_separator_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clip_separator_diagnostic_latest.md"


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


def best_effect(row: dict[str, Any]) -> dict[str, Any]:
    effect = row.get("best_policy_effect")
    return effect if isinstance(effect, dict) else {}


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def row_value(row: dict[str, Any], field: str) -> Any:
    effect = best_effect(row)
    if field in effect:
        return effect.get(field)
    return row.get(field)


def num(row: dict[str, Any], field: str) -> float | None:
    return as_float(row_value(row, field))


def exit_reason(row: dict[str, Any]) -> str:
    return str(row_value(row, "exit_reason") or row.get("exit_reason") or "unknown")


def has_tag(row: dict[str, Any], tag: str) -> bool:
    return tag in {str(item) for item in row.get("physics_tags") or []}


def matched_unchanged_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("loss_rows_with_details") or []
    if not isinstance(rows, list):
        return []
    return [
        row for row in rows
        if row.get("escape_class") == "loss_escapes_current_exit_repairs"
        and (best_effect(row).get("effect") in {None, "unchanged"} or best_effect(row).get("delta_cents") == 0)
    ]


class Rule:
    def __init__(self, name: str, fn: Callable[[dict[str, Any]], bool]) -> None:
        self.name = name
        self.fn = fn

    def __call__(self, row: dict[str, Any]) -> bool:
        try:
            return bool(self.fn(row))
        except Exception:
            return False


def atom_rules() -> list[Rule]:
    rules: list[Rule] = []
    for threshold in [0.55, 0.60, 0.65, 0.67, 0.70, 0.72, 0.74, 0.75]:
        rules.append(Rule(f"p_hold_ge_{threshold:.2f}", lambda row, t=threshold: (num(row, "p_hold") or -999.0) >= t))
    for threshold in [2.5, 5.0, 7.5, 10.0, 12.5, 15.0]:
        rules.append(Rule(f"fair_drawdown_lte_{threshold:.1f}", lambda row, t=threshold: (num(row, "fair_drawdown_cents") or 999.0) <= t))
    for threshold in [60, 62, 64, 66, 68, 70, 72, 74]:
        rules.append(Rule(f"exit_cents_ge_{threshold}", lambda row, t=threshold: (num(row, "exit_cents") or -999.0) >= t))
    for threshold in [0.65, 0.75, 0.85, 0.90]:
        rules.append(Rule(f"abs_d_ge_{threshold:.2f}", lambda row, t=threshold: (num(row, "abs_d_sigma") or -999.0) >= t))
    for threshold in [0.20, 0.35, 0.50, 0.65, 0.80]:
        rules.append(Rule(f"recross_lte_{threshold:.2f}", lambda row, t=threshold: (num(row, "recross_hazard_score") or 999.0) <= t))
    for threshold in [2.0, 4.0, 6.0, 8.0]:
        rules.append(Rule(f"raw_edge_ge_{threshold:.1f}", lambda row, t=threshold: (num(row, "raw_edge_cents") or -999.0) >= t))
    for reason in ["mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full"]:
        rules.append(Rule(f"exit_reason_eq_{reason}", lambda row, value=reason: exit_reason(row) == value))
    for tag in ["near_boundary", "rich_entry", "thin_raw_edge", "recross_hazard_high", "thin_touch_depth"]:
        rules.append(Rule(f"tag_{tag}", lambda row, value=tag: has_tag(row, value)))
    return rules


def evaluate_rule(name: str, fn: Callable[[dict[str, Any]], bool], rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if fn(row)]
    known = [row for row in selected if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    unknown = [row for row in selected if hold_delta(row) is None]
    delta = sum(hold_delta(row) or 0.0 for row in known)
    precision = len(helpful) / len(known) if known else None
    return {
        "rule": name,
        "selected_rows": len(selected),
        "known_rows": len(known),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "unknown_rows": len(unknown),
        "known_hold_delta_cents": delta,
        "precision_on_known": precision,
        "failure_class_counts": dict(Counter(str(row.get("failure_class") or "unknown") for row in selected)),
        "exit_reason_counts": dict(Counter(exit_reason(row) for row in selected)),
        "selected_examples": [
            compact(row) for row in sorted(selected, key=lambda item: hold_delta(item) if hold_delta(item) is not None else -999.0, reverse=True)[:8]
        ],
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    effect = best_effect(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "failure_class": row.get("failure_class"),
        "actual_cents": row.get("actual_gross_cents"),
        "hold_cents": row.get("hold_gross_cents"),
        "hold_delta_cents": hold_delta(row),
        "p_hold": effect.get("p_hold"),
        "fair_drawdown_cents": effect.get("fair_drawdown_cents"),
        "exit_cents": effect.get("exit_cents") if effect.get("exit_cents") is not None else row.get("exit_cents"),
        "exit_reason": exit_reason(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "raw_edge_cents": row.get("raw_edge_cents"),
        "tags": row.get("physics_tags") or [],
    }


def build_report() -> dict[str, Any]:
    loss_escape = load_json(LOSS_ESCAPE_JSON)
    gap = load_json(GAP_JSON)
    rows = matched_unchanged_rows(loss_escape)
    known = [row for row in rows if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    unknown = [row for row in rows if hold_delta(row) is None]

    atoms = atom_rules()
    candidates: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [(rule.name, rule) for rule in atoms]
    for left in atoms:
        for right in atoms:
            if left.name >= right.name:
                continue
            candidates.append((f"{left.name} AND {right.name}", lambda row, a=left, b=right: a(row) and b(row)))

    scored = [evaluate_rule(name, fn, rows) for name, fn in candidates]
    scored = [
        row for row in scored
        if row["known_rows"] >= 4 and row["helpful_rows"] >= 3 and row["known_hold_delta_cents"] > 0
    ]
    scored.sort(
        key=lambda row: (
            row["harmful_rows"],
            -row["known_hold_delta_cents"],
            -(row["precision_on_known"] or 0.0),
            -row["helpful_rows"],
            row["unknown_rows"],
        )
    )

    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(LOSS_ESCAPE_JSON),
        "gap_classifier_source": str(GAP_JSON),
        "gap_summary": gap.get("summary") or {},
        "summary": {
            "matched_unchanged_rows": len(rows),
            "known_hold_rows": len(known),
            "hold_helpful_rows": len(helpful),
            "hold_harmful_rows": len(harmful),
            "hold_unknown_rows": len(unknown),
            "known_hold_delta_cents": sum(hold_delta(row) or 0.0 for row in known),
            "helpful_failure_classes": dict(Counter(str(row.get("failure_class") or "unknown") for row in helpful)),
            "harmful_failure_classes": dict(Counter(str(row.get("failure_class") or "unknown") for row in harmful)),
        },
        "top_rules": scored[:25],
        "helpful_examples": [compact(row) for row in sorted(helpful, key=lambda item: hold_delta(item) or 0.0, reverse=True)[:12]],
        "harmful_examples": [compact(row) for row in sorted(harmful, key=lambda item: hold_delta(item) or 0.0)[:12]],
        "interpretation": [],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.0f}c"


def write_outputs(report: dict[str, Any]) -> None:
    summary = report["summary"]
    top = (report.get("top_rules") or [{}])[0]
    interpretation = [
        "Diagnostic only; this does not create or promote an exit rule.",
        (
            f"Matched-unchanged losses have {summary['hold_helpful_rows']} hold-helpful rows, "
            f"{summary['hold_harmful_rows']} hold-harmful rows, and {summary['hold_unknown_rows']} unknown-hold rows."
        ),
        (
            f"Best diagnostic separator is {top.get('rule')} with {top.get('helpful_rows')} helpful, "
            f"{top.get('harmful_rows')} harmful, {top.get('unknown_rows')} unknown, and "
            f"{top.get('known_hold_delta_cents')}c known hold delta."
            if top.get("rule")
            else "No simple separator met the minimum diagnostic support threshold."
        ),
    ]
    report["interpretation"] = interpretation
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Clip Separator Diagnostic",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched unchanged rows: `{summary['matched_unchanged_rows']}`",
        f"- Known hold helpful/harmful/unknown: `{summary['hold_helpful_rows']}/{summary['hold_harmful_rows']}/{summary['hold_unknown_rows']}`",
        f"- Known hold delta: `{money(summary['known_hold_delta_cents'])}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in interpretation)
    lines.extend([
        "",
        "## Top Diagnostic Separators",
        "",
        "| rule | selected | known | helpful | harmful | unknown | delta | precision | failure classes | exit reasons |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("top_rules") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | {row.get('known_rows')} | "
            f"{row.get('helpful_rows')} | {row.get('harmful_rows')} | {row.get('unknown_rows')} | "
            f"{money(row.get('known_hold_delta_cents'))} | {fmt(row.get('precision_on_known'))} | "
            f"`{row.get('failure_class_counts')}` | `{row.get('exit_reason_counts')}` |"
        )
    lines.extend(["", "## Harmful Hold Examples", ""])
    lines.extend(example_lines(report.get("harmful_examples") or []))
    lines.extend(["", "## Helpful Hold Examples", ""])
    lines.extend(example_lines(report.get("helpful_examples") or []))
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def example_lines(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| market | failure | actual | hold | delta | p_hold | drawdown | exit | abs_d | recross | tags |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('failure_class')}` | {money(row.get('actual_cents'))} | "
            f"{money(row.get('hold_cents'))} | {money(row.get('hold_delta_cents'))} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"`{row.get('exit_reason')}` | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | `{row.get('tags')}` |"
        )
    return lines


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
