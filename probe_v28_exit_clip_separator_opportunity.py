"""Opportunity and margin audit for the frozen v28 exit-clip separator.

Research-only; no live bot changes or orders.

The frozen exit-clip separator has started firing, but the sample is tiny. This
probe explains whether the post-freeze denominator is selected cleanly, barely
misses the rule, or points toward a separate future child freeze. It does not
change the frozen rule.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_exit_clip_separator_watch import (
    LOSS_ESCAPE_JSON,
    OUT_DIR,
    STATE_JSON,
    as_float,
    best_effect,
    fail_reasons,
    hold_delta,
    is_matched_unchanged,
    load_json,
    parse_ts,
    row_ts,
    selected,
)


OUT_JSON = OUT_DIR / "v28_exit_clip_separator_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clip_separator_opportunity_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def compact(row: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    effect = best_effect(row)
    p_hold = as_float(effect.get("p_hold"))
    drawdown = as_float(effect.get("fair_drawdown_cents"))
    p_floor = float(state.get("p_hold_floor") or 0.0)
    drawdown_ceiling = float(state.get("fair_drawdown_cents_ceiling") or 0.0)
    reasons = fail_reasons(row, state)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "failure_class": row.get("failure_class"),
        "actual_cents": as_float(row.get("actual_gross_cents")),
        "hold_cents": as_float(row.get("hold_gross_cents")),
        "hold_delta_cents": hold_delta(row),
        "selected": selected(row, state),
        "fail_reasons": reasons,
        "fail_count": len(reasons),
        "p_hold": p_hold,
        "p_hold_margin": None if p_hold is None else p_hold - p_floor,
        "fair_drawdown_cents": drawdown,
        "fair_drawdown_margin_cents": None if drawdown is None else drawdown_ceiling - drawdown,
        "exit_cents": effect.get("exit_cents") if effect.get("exit_cents") is not None else row.get("exit_cents"),
        "exit_reason": effect.get("exit_reason") or row.get("exit_reason"),
        "physics_tags": row.get("physics_tags") or [],
    }


def hypothetical_selected(row: dict[str, Any], p_floor: float, drawdown_ceiling: float) -> bool:
    effect = best_effect(row)
    p_hold = as_float(effect.get("p_hold"))
    drawdown = as_float(effect.get("fair_drawdown_cents"))
    return p_hold is not None and drawdown is not None and p_hold >= p_floor and drawdown <= drawdown_ceiling


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    known = [row for row in rows if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    unknown = [row for row in rows if hold_delta(row) is None]
    return {
        "rows": len(rows),
        "known_rows": len(known),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "unknown_rows": len(unknown),
        "known_hold_delta_cents": sum(hold_delta(row) or 0.0 for row in known),
        "failure_class_counts": dict(Counter(str(row.get("failure_class") or "unknown") for row in rows)),
        "exit_reason_counts": dict(Counter(str((best_effect(row).get("exit_reason") or row.get("exit_reason") or "unknown")) for row in rows)),
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    payload = load_json(LOSS_ESCAPE_JSON)
    rows = payload.get("loss_rows_with_details") or []
    if not isinstance(rows, list):
        rows = []
    post = [
        row
        for row in rows
        if freeze_ts is not None
        and is_matched_unchanged(row)
        and (row_ts(row) or datetime.min.replace(tzinfo=timezone.utc)) >= freeze_ts
    ]
    picked = [row for row in post if selected(row, state)]
    missed = [row for row in post if not selected(row, state)]
    near = [row for row in missed if 0 < len(fail_reasons(row, state)) <= 2]
    p_floor = float(state.get("p_hold_floor") or 0.0)
    drawdown_ceiling = float(state.get("fair_drawdown_cents_ceiling") or 0.0)
    variants = []
    for label, p_candidate, drawdown_candidate in [
        ("frozen_rule", p_floor, drawdown_ceiling),
        ("drawdown_lte_12p5_same_p", p_floor, 12.5),
        ("p_hold_ge_055_same_drawdown", 0.55, drawdown_ceiling),
        ("drawdown_lte_12p5_p_hold_ge055", 0.55, 12.5),
    ]:
        selected_rows = [row for row in post if hypothetical_selected(row, p_candidate, drawdown_candidate)]
        summary = summarize(selected_rows)
        variants.append(
            {
                "variant": label,
                "p_hold_floor": p_candidate,
                "fair_drawdown_cents_ceiling": drawdown_candidate,
                "summary": summary,
                "rows": [compact(row, {"p_hold_floor": p_candidate, "fair_drawdown_cents_ceiling": drawdown_candidate}) for row in selected_rows],
            }
        )
    blockers = []
    selected_delta = sum(hold_delta(row) or 0.0 for row in picked)
    if len(post) < 30:
        blockers.append("post_rows_lt_30")
    if len(picked) < 30:
        blockers.append("selected_rows_lt_30")
    if selected_delta <= 0:
        blockers.append("selected_delta_not_positive")
    if selected_delta < 300:
        blockers.append("selected_delta_lt_300c")
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "source": str(LOSS_ESCAPE_JSON),
        "post_freeze_rows": len(post),
        "selected_rows": len(picked),
        "near_miss_rows": len(near),
        "post_summary": summarize(post),
        "selected_summary": summarize(picked),
        "near_miss_summary": summarize(near),
        "fail_reason_counts": dict(Counter(reason for row in missed for reason in fail_reasons(row, state))),
        "selected_examples": [compact(row, state) for row in picked[:12]],
        "near_miss_examples": sorted(
            [compact(row, state) for row in near],
            key=lambda item: (item.get("fail_count") or 99, -(fnum(item.get("hold_delta_cents")))),
        )[:12],
        "threshold_variants_on_post_rows": variants,
        "blockers": blockers,
        "live_ready": False,
        "interpretation": [
            "Research-only opportunity and margin audit; no live bot logic changes or orders.",
            f"The frozen rule has {len(post)} post-freeze denominator rows and selected {len(picked)} row(s).",
            f"Near misses with one or two failed gates: {len(near)}.",
            "Threshold variants are post-freeze diagnostics only; they do not create a new child freeze.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.0f}c"


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    selected_summary = report.get("selected_summary") or {}
    near_summary = report.get("near_miss_summary") or {}
    lines = [
        "# v28 Exit Clip Separator Opportunity",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Rule: `{state.get('rule')}`",
        f"- Post-freeze denominator rows: `{report.get('post_freeze_rows')}`",
        f"- Selected rows: `{report.get('selected_rows')}`",
        f"- Selected helpful/harmful/unknown: `{selected_summary.get('helpful_rows')}/{selected_summary.get('harmful_rows')}/{selected_summary.get('unknown_rows')}`",
        f"- Selected known hold delta: `{money(selected_summary.get('known_hold_delta_cents'))}`",
        f"- Near-miss rows: `{report.get('near_miss_rows')}`",
        f"- Near-miss helpful/harmful/unknown: `{near_summary.get('helpful_rows')}/{near_summary.get('harmful_rows')}/{near_summary.get('unknown_rows')}`",
        f"- Near-miss known hold delta: `{money(near_summary.get('known_hold_delta_cents'))}`",
        f"- Fail reasons: `{report.get('fail_reason_counts')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Threshold Variants On Post-Freeze Rows",
            "",
            "| variant | p floor | drawdown max | rows | known | helpful | harmful | unknown | known delta |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in report.get("threshold_variants_on_post_rows") or []:
        summary = item.get("summary") or {}
        lines.append(
            f"| `{item.get('variant')}` | {fmt(item.get('p_hold_floor'))} | "
            f"{fmt(item.get('fair_drawdown_cents_ceiling'))} | {summary.get('rows')} | "
            f"{summary.get('known_rows')} | {summary.get('helpful_rows')} | "
            f"{summary.get('harmful_rows')} | {summary.get('unknown_rows')} | "
            f"{money(summary.get('known_hold_delta_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Selected Rows",
            "",
            "| market | side | current | hold | delta | p hold | p margin | drawdown | drawdown margin | exit | failure |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report.get("selected_examples") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {money(row.get('actual_cents'))} | "
            f"{money(row.get('hold_cents'))} | {money(row.get('hold_delta_cents'))} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('p_hold_margin'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('fair_drawdown_margin_cents'))} | "
            f"{row.get('exit_reason')} | {row.get('failure_class')} |"
        )
    lines.extend(
        [
            "",
            "## Near Misses",
            "",
            "| market | side | current | hold | delta | p hold | p margin | drawdown | drawdown margin | failed gates | failure |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report.get("near_miss_examples") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {money(row.get('actual_cents'))} | "
            f"{money(row.get('hold_cents'))} | {money(row.get('hold_delta_cents'))} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('p_hold_margin'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('fair_drawdown_margin_cents'))} | "
            f"{', '.join(row.get('fail_reasons') or [])} | {row.get('failure_class')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
