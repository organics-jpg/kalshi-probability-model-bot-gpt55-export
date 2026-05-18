"""Runway for the v28 book-gap loss-guard v1/v2/v3 decision.

Research-only; no live bot changes or orders.

V1 is less strict and has begun to recover small post-freeze value-over-hold
winner clips. V2 is stricter and is meant to avoid deep adverse fair-drawdown
holds. V3 is the newest small relaxation for extreme p-hold value exits. This
report turns that tradeoff into a forward runway instead of relying on
diagnostic upside.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
CONTRAST_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_v3_contrast_latest.json"
V1_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json"
V2_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json"
V3_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json"
V2_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_book_gap_loss_guard_v2_opportunity_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_runway_latest.json"
OUT_MD = OUT_DIR / "v28_exit_loss_guard_v1_v2_runway_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_FULL_LOSS_CUSHION = 3
FULL_LOSS_CENTS = 100.0


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


def window(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for row in payload.get("windows") or []:
        if isinstance(row, dict) and row.get("window") == name:
            return row
    return {}


def bucket(row: dict[str, Any], name: str) -> dict[str, Any]:
    return ((row.get("buckets") or {}).get(name) or {})


def summary_metrics(source: dict[str, Any]) -> dict[str, Any]:
    summary = source.get("summary") or {}
    return {
        "settled": int(as_float(summary.get("settled")) or 0),
        "suppressed_exits": int(as_float(summary.get("suppressed_exits")) or 0),
        "delta_vs_current_cents": float(as_float(summary.get("delta_vs_current_cents")) or 0.0),
        "winner_recovery_cents": float(as_float(summary.get("winner_clip_recovered_cents")) or 0.0),
        "loss_control_cost_cents": float(as_float(summary.get("loss_control_cost_cents")) or 0.0),
        "blockers": list(source.get("blockers") or []),
    }


def v2_decision_window(row: dict[str, Any]) -> dict[str, Any]:
    both = bucket(row, "both_suppress") or bucket(row, "all_three")
    v2_only = bucket(row, "v2_only")
    v2_v3_only = bucket(row, "v2_v3_only")
    v1_only = bucket(row, "v1_only")
    v1_v3_only = bucket(row, "v1_v3_only")
    settled = int(as_float(row.get("rows")) or 0)
    v2_suppressed = (
        int(as_float(both.get("rows")) or 0)
        + int(as_float(v2_only.get("rows")) or 0)
        + int(as_float(v2_v3_only.get("rows")) or 0)
    )
    v2_delta = (
        float(as_float(both.get("net_delta_cents")) or 0.0)
        + float(as_float(v2_only.get("net_delta_cents")) or 0.0)
        + float(as_float(v2_v3_only.get("net_delta_cents")) or 0.0)
    )
    v2_harm = (
        float(as_float(both.get("harmful_delta_cents")) or 0.0)
        + float(as_float(v2_only.get("harmful_delta_cents")) or 0.0)
        + float(as_float(v2_v3_only.get("harmful_delta_cents")) or 0.0)
    )
    v1_only_delta = (
        float(as_float(v1_only.get("net_delta_cents")) or 0.0)
        + float(as_float(v1_v3_only.get("net_delta_cents")) or 0.0)
    )
    full_losses_absorbable = int(max(0.0, v2_delta) // FULL_LOSS_CENTS)
    blockers: list[str] = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if v2_suppressed < MIN_SUPPRESSED_DECISIONS:
        blockers.append("v2_suppressed_decisions_lt_30")
    if v2_delta <= 0:
        blockers.append("v2_delta_not_positive")
    if v2_harm < 0:
        blockers.append("v2_harmful_suppression_cost_negative")
    if full_losses_absorbable < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "window": row.get("window"),
        "settled": settled,
        "v2_suppressed_decisions": v2_suppressed,
        "v2_delta_cents": v2_delta,
        "v2_harmful_delta_cents": v2_harm,
        "v1_only_opportunity_cost_cents": v1_only_delta,
        "v1_only_rows": int(as_float(v1_only.get("rows")) or 0) + int(as_float(v1_v3_only.get("rows")) or 0),
        "rows_needed": max(0, MIN_SETTLED - settled),
        "v2_suppressed_needed": max(0, MIN_SUPPRESSED_DECISIONS - v2_suppressed),
        "net_cents_needed_for_cushion3": max(0.0, MIN_FULL_LOSS_CUSHION * FULL_LOSS_CENTS - max(0.0, v2_delta)),
        "full_losses_absorbable": full_losses_absorbable,
        "blockers": blockers,
        "ready_for_review": not blockers,
    }


def variant_decision_window(row: dict[str, Any], variant: str) -> dict[str, Any]:
    selected_buckets = {
        "v1": ("all_three", "v1_only", "v1_v3_only"),
        "v2": ("all_three", "v2_only", "v2_v3_only"),
        "v3": ("all_three", "v3_only", "v2_v3_only", "v1_v3_only"),
    }[variant]
    settled = int(as_float(row.get("rows")) or 0)
    suppressed = 0
    delta = 0.0
    harm = 0.0
    for bucket_name in selected_buckets:
        bucket_row = bucket(row, bucket_name)
        suppressed += int(as_float(bucket_row.get("rows")) or 0)
        delta += float(as_float(bucket_row.get("net_delta_cents")) or 0.0)
        harm += float(as_float(bucket_row.get("harmful_delta_cents")) or 0.0)
    full_losses_absorbable = int(max(0.0, delta) // FULL_LOSS_CENTS)
    blockers: list[str] = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if suppressed < MIN_SUPPRESSED_DECISIONS:
        blockers.append(f"{variant}_suppressed_decisions_lt_30")
    if delta <= 0:
        blockers.append(f"{variant}_delta_not_positive")
    if harm < 0:
        blockers.append(f"{variant}_harmful_suppression_cost_negative")
    if full_losses_absorbable < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "window": row.get("window"),
        "variant": variant,
        "settled": settled,
        "suppressed_decisions": suppressed,
        "delta_cents": delta,
        "harmful_delta_cents": harm,
        "rows_needed": max(0, MIN_SETTLED - settled),
        "suppressed_needed": max(0, MIN_SUPPRESSED_DECISIONS - suppressed),
        "net_cents_needed_for_cushion3": max(0.0, MIN_FULL_LOSS_CUSHION * FULL_LOSS_CENTS - max(0.0, delta)),
        "full_losses_absorbable": full_losses_absorbable,
        "blockers": blockers,
        "ready_for_review": not blockers,
    }


def build_report() -> dict[str, Any]:
    contrast = load_json(CONTRAST_JSON)
    v1 = load_json(V1_JSON)
    v2 = load_json(V2_JSON)
    v3 = load_json(V3_JSON)
    v2_opp = load_json(V2_OPPORTUNITY_JSON)
    v1_strict = window(contrast, "v1_strict_forward")
    v2_strict = window(contrast, "v2_strict_forward")
    v3_strict = window(contrast, "v3_strict_forward")
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_paths": {
            "contrast": str(CONTRAST_JSON),
            "v1": str(V1_JSON),
            "v2": str(V2_JSON),
            "v3": str(V3_JSON),
            "v2_opportunity": str(V2_OPPORTUNITY_JSON),
        },
        "v1_freeze_ts_utc": contrast.get("v1_freeze_ts_utc"),
        "v2_freeze_ts_utc": contrast.get("v2_freeze_ts_utc"),
        "v3_freeze_ts_utc": contrast.get("v3_freeze_ts_utc"),
        "v1_summary": summary_metrics(v1),
        "v2_summary": summary_metrics(v2),
        "v3_summary": summary_metrics(v3),
        "v2_opportunity": {
            "total_rows": v2_opp.get("total_rows"),
            "soft_exit_rows": v2_opp.get("soft_exit_rows"),
            "value_over_hold_rows": v2_opp.get("value_over_hold_rows"),
            "probability_reduce_rows": v2_opp.get("probability_reduce_rows"),
            "would_suppress_rows": v2_opp.get("would_suppress_rows"),
            "fail_reason_counts": v2_opp.get("fail_reason_counts"),
        },
        "v1_strict_runway": v2_decision_window(v1_strict),
        "v2_strict_runway": v2_decision_window(v2_strict),
        "v3_strict_runway": variant_decision_window(v3_strict, "v3"),
        "strict_variant_runways": [
            variant_decision_window(v1_strict, "v1"),
            variant_decision_window(v2_strict, "v2"),
            variant_decision_window(v3_strict, "v3"),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    v1_runway = report.get("v1_strict_runway") or {}
    v2_runway = report.get("v2_strict_runway") or {}
    v3_runway = report.get("v3_strict_runway") or {}
    opp = report.get("v2_opportunity") or {}
    return [
        "This runway is research-only and does not change any live exit rule.",
        (
            f"V2 strict-forward has {v2_runway.get('settled')} settled rows, "
            f"{v2_runway.get('v2_suppressed_decisions')} v2 suppressions, "
            f"{v2_runway.get('v2_delta_cents')}c v2 delta, and blockers {v2_runway.get('blockers')}."
        ),
        (
            f"V1-only opportunity cost after the v2 freeze is {v2_runway.get('v1_only_opportunity_cost_cents')}c "
            f"over {v2_runway.get('v1_only_rows')} rows; this is the current cost of v2 strictness."
        ),
        (
            f"V2 opportunity denominator has {opp.get('soft_exit_rows')} soft exits and {opp.get('would_suppress_rows')} "
            f"would-suppress rows; fail reasons {opp.get('fail_reason_counts')}."
        ),
        (
            f"For promotion review, v2 still needs {v2_runway.get('rows_needed')} settled rows, "
            f"{v2_runway.get('v2_suppressed_needed')} v2 suppressions, and "
            f"{v2_runway.get('net_cents_needed_for_cushion3')}c additional cushion."
        ),
        (
            f"V3 strict-forward has {v3_runway.get('settled')} settled rows, "
            f"{v3_runway.get('suppressed_decisions')} v3 suppressions, "
            f"{v3_runway.get('delta_cents')}c v3 delta, and blockers {v3_runway.get('blockers')}."
        ),
        (
            f"V1 strict-forward remains an alternate watch: {v1_runway.get('settled')} settled rows, "
            f"{v1_runway.get('v2_suppressed_decisions')} v2-equivalent suppressions, "
            f"and {v1_runway.get('v1_only_opportunity_cost_cents')}c v1-only cost."
        ),
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Loss-Guard V1/V2/V3 Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- V1 freeze UTC: `{report.get('v1_freeze_ts_utc')}`",
        f"- V2 freeze UTC: `{report.get('v2_freeze_ts_utc')}`",
        f"- V3 freeze UTC: `{report.get('v3_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Strict Runways",
        "",
        "| window | settled | v2 suppressions | v2 delta c | v2 harmful c | v1-only rows | v1-only cost c | rows needed | suppressions needed | cushion c needed | absorbable losses | ready | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for key in ("v1_strict_runway", "v2_strict_runway"):
        row = report.get(key) or {}
        lines.append(
            f"| {row.get('window')} | {row.get('settled')} | {row.get('v2_suppressed_decisions')} | "
            f"{fmt(row.get('v2_delta_cents'))} | {fmt(row.get('v2_harmful_delta_cents'))} | "
            f"{row.get('v1_only_rows')} | {fmt(row.get('v1_only_opportunity_cost_cents'))} | "
            f"{row.get('rows_needed')} | {row.get('v2_suppressed_needed')} | "
            f"{fmt(row.get('net_cents_needed_for_cushion3'))} | {row.get('full_losses_absorbable')} | "
            f"{row.get('ready_for_review')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Strict Variant Runways",
        "",
        "| variant | window | settled | suppressed | delta c | harmful c | rows needed | suppressions needed | cushion c needed | absorbable losses | ready | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("strict_variant_runways") or []:
        lines.append(
            f"| {row.get('variant')} | {row.get('window')} | {row.get('settled')} | "
            f"{row.get('suppressed_decisions')} | {fmt(row.get('delta_cents'))} | "
            f"{fmt(row.get('harmful_delta_cents'))} | {row.get('rows_needed')} | "
            f"{row.get('suppressed_needed')} | {fmt(row.get('net_cents_needed_for_cushion3'))} | "
            f"{row.get('full_losses_absorbable')} | {row.get('ready_for_review')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## V2 Opportunity",
        "",
        f"- `{report.get('v2_opportunity')}`",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
