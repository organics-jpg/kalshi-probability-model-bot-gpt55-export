"""Scan observable separators inside matched-but-unchanged v28 loss rows.

Research-only; no live bot changes or orders.

The exit-repair gap classifier shows a large matched-but-unchanged loss bucket.
This probe asks whether any observable exit/entry features separate rows where
holding to settlement would have helped from rows where holding would have made
the loss worse. It is diagnostic only: these rows are losses, and outcome labels
are used only to score candidate separators after the fact.
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
OUT_JSON = OUT_DIR / "v28_exit_matched_unchanged_separator_scan_latest.json"
OUT_MD = OUT_DIR / "v28_exit_matched_unchanged_separator_scan_latest.md"

MIN_SELECTED = 3


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


def fnum(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def best_effect(row: dict[str, Any]) -> dict[str, Any]:
    effect = row.get("best_policy_effect")
    return effect if isinstance(effect, dict) else {}


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = fnum(row.get("actual_gross_cents"))
    hold = fnum(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def feature(row: dict[str, Any], name: str) -> Any:
    effect = best_effect(row)
    if name in effect:
        return effect.get(name)
    return row.get(name)


def rows() -> list[dict[str, Any]]:
    payload = load_json(LOSS_ESCAPE_JSON)
    source_rows = payload.get("loss_rows_with_details") or []
    if not isinstance(source_rows, list):
        return []
    matched = [
        row for row in source_rows
        if isinstance(row, dict) and row.get("escape_class") == "loss_escapes_current_exit_repairs"
    ]
    return matched


Condition = tuple[str, Callable[[dict[str, Any]], bool]]


def numeric_conditions(field: str, thresholds: list[float]) -> list[Condition]:
    conditions: list[Condition] = []
    for threshold in thresholds:
        label = f"{field}_lte_{threshold:g}"
        conditions.append((label, lambda row, field=field, threshold=threshold: (fnum(feature(row, field)) is not None and fnum(feature(row, field), 0.0) <= threshold)))
        label = f"{field}_gte_{threshold:g}"
        conditions.append((label, lambda row, field=field, threshold=threshold: (fnum(feature(row, field)) is not None and fnum(feature(row, field), 0.0) >= threshold)))
    return conditions


def categorical_conditions(field: str, values: list[str]) -> list[Condition]:
    return [
        (
            f"{field}_eq_{value or 'blank'}",
            lambda row, field=field, value=value: str(feature(row, field) or "") == value,
        )
        for value in values
    ]


def all_conditions() -> list[Condition]:
    conditions: list[Condition] = []
    conditions.extend(numeric_conditions("p_hold", [0.40, 0.50, 0.60, 0.70, 0.75, 0.79, 0.85]))
    conditions.extend(numeric_conditions("exit_cents", [30, 40, 50, 60, 70, 80, 90]))
    conditions.extend(numeric_conditions("fair_drawdown_cents", [-10, -5, 0, 5, 10, 20]))
    conditions.extend(numeric_conditions("ask_cents", [35, 50, 60, 70, 80, 90]))
    conditions.extend(numeric_conditions("raw_edge_cents", [2, 5, 8, 10, 15, 25]))
    conditions.extend(numeric_conditions("recross_hazard_score", [0.05, 0.10, 0.20, 0.30, 0.40, 0.60]))
    conditions.extend(numeric_conditions("abs_d_sigma", [0.50, 0.75, 0.85, 1.00, 1.25, 1.50]))
    conditions.extend(numeric_conditions("eligible_depth", [25, 100, 384, 1000]))
    conditions.extend(numeric_conditions("p_side", [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]))
    conditions.extend(categorical_conditions(
        "exit_reason",
        ["mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full", "mushroom_v28_exit_value_over_hold", ""],
    ))
    return conditions


def score_rule(label: str, selected: list[dict[str, Any]], total_rows: int) -> dict[str, Any]:
    deltas = [(hold_delta(row) or 0.0) for row in selected]
    helpful = [delta for delta in deltas if delta > 0.0]
    harmful = [delta for delta in deltas if delta < 0.0]
    unknown = [row for row in selected if hold_delta(row) is None]
    actual_loss = sum(fnum(row.get("actual_gross_cents"), 0.0) or 0.0 for row in selected)
    hold_net = sum(fnum(row.get("hold_gross_cents"), 0.0) or 0.0 for row in selected)
    source_counts = Counter(str(row.get("failure_class") or "unknown") for row in selected)
    exit_counts = Counter(str(feature(row, "exit_reason") or "unknown") for row in selected)
    tags = Counter(tag for row in selected for tag in (row.get("physics_tags") or []))
    return {
        "rule": label,
        "selected_rows": len(selected),
        "selected_share": len(selected) / total_rows if total_rows else 0.0,
        "actual_loss_cents": actual_loss,
        "hold_net_cents": hold_net,
        "hold_delta_cents": sum(deltas),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "unknown_rows": len(unknown),
        "helpful_delta_cents": sum(helpful),
        "harmful_delta_cents": sum(harmful),
        "failure_class_counts": dict(source_counts),
        "exit_reason_counts": dict(exit_counts),
        "top_tags": dict(tags.most_common(6)),
        "examples": sorted(
            [
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "entry_ts": row.get("entry_ts"),
                    "actual_gross_cents": row.get("actual_gross_cents"),
                    "hold_gross_cents": row.get("hold_gross_cents"),
                    "hold_delta_cents": hold_delta(row),
                    "p_hold": feature(row, "p_hold"),
                    "exit_cents": feature(row, "exit_cents"),
                    "exit_reason": feature(row, "exit_reason"),
                    "fair_drawdown_cents": feature(row, "fair_drawdown_cents"),
                    "ask_cents": row.get("ask_cents"),
                    "raw_edge_cents": row.get("raw_edge_cents"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "eligible_depth": row.get("eligible_depth"),
                    "failure_class": row.get("failure_class"),
                    "tags": row.get("physics_tags") or [],
                }
                for row in selected
            ],
            key=lambda item: fnum(item.get("hold_delta_cents"), 0.0) or 0.0,
        )[:8],
    }


def pair_conditions(base: list[Condition], source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    promising = []
    for label, predicate in base:
        selected = [row for row in source_rows if predicate(row)]
        if len(selected) >= MIN_SELECTED:
            score = score_rule(label, selected, len(source_rows))
            if score["harmful_rows"] <= 1 and score["hold_delta_cents"] > 0:
                promising.append((label, predicate))
            scored.append(score)
    for left_index, (left_label, left_predicate) in enumerate(promising):
        for right_label, right_predicate in promising[left_index + 1:]:
            label = f"{left_label} AND {right_label}"
            selected = [row for row in source_rows if left_predicate(row) and right_predicate(row)]
            if len(selected) >= MIN_SELECTED:
                scored.append(score_rule(label, selected, len(source_rows)))
    return scored


def build_report() -> dict[str, Any]:
    source_rows = rows()
    total = len(source_rows)
    known = [row for row in source_rows if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    base_conditions = all_conditions()
    scored = pair_conditions(base_conditions, source_rows)
    clean = [
        score for score in scored
        if score["selected_rows"] >= MIN_SELECTED and score["harmful_rows"] == 0 and score["hold_delta_cents"] > 0
    ]
    robust = [
        score for score in scored
        if score["selected_rows"] >= 5 and score["harmful_rows"] == 0 and score["hold_delta_cents"] > 0
    ]
    risky = [
        score for score in scored
        if score["selected_rows"] >= MIN_SELECTED and score["harmful_rows"] > 0
    ]
    clean.sort(key=lambda row: (row["selected_rows"], row["hold_delta_cents"]), reverse=True)
    robust.sort(key=lambda row: (row["selected_rows"], row["hold_delta_cents"]), reverse=True)
    risky.sort(key=lambda row: (row["harmful_delta_cents"], -row["harmful_rows"]))
    interpretation = [
        "Research-only separator scan; no live bot logic changes or orders.",
        (
            f"Matched-but-unchanged loss rows split into {len(helpful)} hold-helpful and "
            f"{len(harmful)} hold-harmful rows, so broad hold suppression remains unsafe."
        ),
        (
            "Clean separator rows here are diagnostic failure-mode evidence only. A deployable exit rule would need "
            "its own frozen forward watch, row count, suppression density, path-risk review, and live-readiness gate."
        ),
    ]
    if robust:
        top = robust[0]
        interpretation.append(
            f"Best robust zero-harm diagnostic separator is `{top['rule']}` with "
            f"{top['selected_rows']} selected rows and {top['hold_delta_cents']}c hold delta."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(LOSS_ESCAPE_JSON),
        "summary": {
            "matched_unchanged_rows": total,
            "known_hold_rows": len(known),
            "hold_helpful_rows": len(helpful),
            "hold_harmful_rows": len(harmful),
            "hold_unknown_rows": total - len(known),
            "total_hold_delta_cents": sum(hold_delta(row) or 0.0 for row in known),
            "total_actual_loss_cents": sum(fnum(row.get("actual_gross_cents"), 0.0) or 0.0 for row in source_rows),
            "total_hold_net_cents": sum(fnum(row.get("hold_gross_cents"), 0.0) or 0.0 for row in source_rows),
        },
        "interpretation": interpretation,
        "top_clean_zero_harm_rules": clean[:20],
        "top_robust_zero_harm_rules": robust[:20],
        "top_risky_rules": risky[:20],
        "blockers": [
            "diagnostic_loss_rows_only",
            "needs_own_frozen_forward_watch",
            "needs_path_risk_review",
            "not_live_bot_logic",
        ],
        "live_ready": False,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    lines = [
        "# v28 Exit Matched-Unchanged Separator Scan",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched unchanged rows: `{summary.get('matched_unchanged_rows')}`",
        f"- Hold helpful/harmful/unknown: `{summary.get('hold_helpful_rows')}/{summary.get('hold_harmful_rows')}/{summary.get('hold_unknown_rows')}`",
        f"- Total actual loss: `{fmt(summary.get('total_actual_loss_cents'))}c`",
        f"- Total hold net: `{fmt(summary.get('total_hold_net_cents'))}c`",
        f"- Total hold delta: `{fmt(summary.get('total_hold_delta_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Top Robust Zero-Harm Rules",
        "",
        "| rule | rows | hold delta c | helpful/harmful | actual loss c | hold net c | failure classes | exit reasons |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("top_robust_zero_harm_rules") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | {fmt(row.get('hold_delta_cents'))} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')} | {fmt(row.get('actual_loss_cents'))} | "
            f"{fmt(row.get('hold_net_cents'))} | `{row.get('failure_class_counts')}` | `{row.get('exit_reason_counts')}` |"
        )
    lines.extend([
        "",
        "## Top Clean Zero-Harm Rules",
        "",
        "| rule | rows | hold delta c | helpful/harmful | top tags |",
        "|---|---:|---:|---:|---|",
    ])
    for row in (report.get("top_clean_zero_harm_rules") or [])[:12]:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | {fmt(row.get('hold_delta_cents'))} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')} | `{row.get('top_tags')}` |"
        )
    lines.extend([
        "",
        "## Highest-Risk Matched Rules",
        "",
        "| rule | rows | hold delta c | helpful/harmful | harmful delta c | top tags |",
        "|---|---:|---:|---:|---:|---|",
    ])
    for row in (report.get("top_risky_rules") or [])[:12]:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | {fmt(row.get('hold_delta_cents'))} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')} | {fmt(row.get('harmful_delta_cents'))} | "
            f"`{row.get('top_tags')}` |"
        )
    lines.extend([
        "",
        "## Blockers",
        "",
    ])
    lines.extend(f"- `{item}`" for item in report.get("blockers") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
