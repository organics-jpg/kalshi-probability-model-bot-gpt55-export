"""Frozen value-exit feature-side guard watch.

Research-only; no live bot changes or orders.

This freezes the observable mix suggested by the value-exit/feature-gate
contrast: suppress value-over-hold exits only when the feature-gate entry
geometry selects the same market side. Opposite-side value exits remain live
loss-control exits.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_value_exit_feature_gate_contrast import (
    OUT_DIR,
    TARGET_FEATURE_CANDIDATE,
    TARGET_VALUE_VARIANT,
    compact_row,
    feature_rows_by_market,
    fnum,
    load_json,
    summarize_rows,
)


ROOT = Path(__file__).resolve().parent
VALUE_ONLY_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.md"

MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "value_exit_feature_side_guard",
        "candidate": "value_only_gap15_or_p75_feature_gate_same_side",
        "value_exit_parent": TARGET_VALUE_VARIANT,
        "feature_gate_parent": TARGET_FEATURE_CANDIDATE,
        "rule": (
            "Apply the value_only_gap15_or_p75 exit suppression only when the "
            "feature-gate selected side for the same market equals the live position side."
        ),
        "physics": (
            "Value-over-hold exits look like winner clips when the entry geometry still agrees with the held side. "
            "When feature-gate geometry selects the opposite side, suppressing the exit can override a valid loss-control signal."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic context only.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def row_after_freeze(row: dict[str, Any], freeze_ts: str) -> bool:
    row_ts = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
    freeze = parse_ts(freeze_ts)
    return bool(row_ts and freeze and row_ts >= freeze)


def source_rows() -> dict[str, list[dict[str, Any]]]:
    payload = load_json(VALUE_ONLY_JSON)
    features = feature_rows_by_market()
    rows_by_lane: dict[str, list[dict[str, Any]]] = {}
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict) or variant.get("variant") != TARGET_VALUE_VARIANT:
                continue
            for row in variant.get("rows") or []:
                if isinstance(row, dict):
                    compacted = compact_row(row, features.get(str(row.get("market") or "")))
                    compacted["source_lane"] = lane_name
                    rows_by_lane.setdefault(lane_name, []).append(compacted)
    return rows_by_lane


def score_lane(label: str, rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    summary = summarize_rows(rows)
    value_only_suppressed = [row for row in rows if row.get("value_only_suppressed")]
    value_only_suppressed_winners = [row for row in value_only_suppressed if row.get("side_won")]
    value_only_suppressed_losers = [row for row in value_only_suppressed if not row.get("side_won")]
    guarded_suppressed = [row for row in rows if row.get("feature_side_guard_suppressed")]
    guarded_suppressed_winners = [row for row in guarded_suppressed if row.get("side_won")]
    guarded_suppressed_losers = [row for row in guarded_suppressed if not row.get("side_won")]
    summary.update(
        {
            "value_only_suppressed_exits": len(value_only_suppressed),
            "value_only_suppressed_winners": len(value_only_suppressed_winners),
            "value_only_suppressed_losers": len(value_only_suppressed_losers),
            "value_only_suppressed_loser_cost_cents": sum(
                fnum(row.get("value_only_delta_cents")) for row in value_only_suppressed_losers
            ),
            "value_only_suppressed_loser_markets": value_only_suppressed_losers,
            "value_only_suppressed_feature_class_counts": dict(
                Counter(row.get("feature_class") for row in value_only_suppressed)
            ),
            "feature_side_guard_suppressed_exits": len(guarded_suppressed),
            "feature_side_guard_suppressed_winners": len(guarded_suppressed_winners),
            "feature_side_guard_suppressed_losers": len(guarded_suppressed_losers),
            "feature_side_guard_suppressed_loser_cost_cents": sum(
                fnum(row.get("feature_side_guard_delta_cents")) for row in guarded_suppressed_losers
            ),
            "feature_side_guard_suppressed_loser_markets": guarded_suppressed_losers,
            "feature_side_guard_suppressed_feature_class_counts": dict(
                Counter(row.get("feature_class") for row in guarded_suppressed)
            ),
            "all_row_feature_class_counts": dict(Counter(row.get("feature_class") for row in rows)),
            "suppressed": len(guarded_suppressed),
            "suppressed_exits": len(guarded_suppressed),
            "suppressed_winners": len(guarded_suppressed_winners),
            "suppressed_losers": len(guarded_suppressed_losers),
            "suppressed_loser_cost_cents": sum(
                fnum(row.get("feature_side_guard_delta_cents")) for row in guarded_suppressed_losers
            ),
            "suppressed_loser_markets": guarded_suppressed_losers,
            "feature_class_counts": dict(Counter(row.get("feature_class") for row in guarded_suppressed)),
        }
    )
    net = fnum(summary.get("feature_side_guard_net_cents"))
    blockers: list[str] = []
    if strict_forward and int(summary.get("rows") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if net <= 0.0:
        blockers.append("net_not_positive")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    blockers.extend(["exit_overlap_only", "not_live_bot_logic"])
    summary["blockers"] = blockers
    summary["live_ready"] = False
    summary["full_loss_cushion_estimate"] = int(max(0.0, net) // 100.0)
    return {
        "label": label,
        "strict_forward": strict_forward,
        "summary": summary,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    rows_by_lane = source_rows()
    diagnostic_source = rows_by_lane.get("diagnostic_from_book_gap_freeze") or []
    post_source = rows_by_lane.get("post_value_only_birth") or []
    pre = [row for row in diagnostic_source if not row_after_freeze(row, freeze_ts)]
    post = [row for row in post_source if row_after_freeze(row, freeze_ts)]
    lanes = [
        score_lane("diagnostic_prefreeze_context", pre, False),
        score_lane("post_feature_side_guard_birth", post, True),
    ]
    post_summary = lanes[1]["summary"]
    interpretation = [
        "Research-only frozen watch; no live bot changes or orders.",
        (
            f"Post-birth has {post_summary.get('rows')} rows, feature-side-guard net "
            f"{post_summary.get('feature_side_guard_net_cents')}c, W/L "
            f"{post_summary.get('feature_side_guard_wins')}/{post_summary.get('feature_side_guard_losses')}."
        ),
        "The guard is observable, but evidence starts from this watch timestamp and cannot promote until forward rows settle.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "interpretation": interpretation,
        "lanes": lanes,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Value Exit Feature-Side Guard",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Candidate: `{state.get('candidate')}`",
        f"- Rule: `{state.get('rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lanes",
            "",
            "| lane | rows | current c | value-only c | guarded c | guarded delta current c | guarded delta value c | guarded W/L | guarded suppressed | guarded sup W/L | guarded sup loser cost c | value-only suppressed | value-only loser cost c | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.append(
            f"| `{lane.get('label')}` | {summary.get('rows')} | {fmt(summary.get('current_net_cents'))} | "
            f"{fmt(summary.get('value_only_net_cents'))} | {fmt(summary.get('feature_side_guard_net_cents'))} | "
            f"{fmt(summary.get('feature_side_guard_delta_cents'))} | "
            f"{fmt(summary.get('feature_side_guard_delta_vs_value_only_cents'))} | "
            f"{summary.get('feature_side_guard_wins')}/{summary.get('feature_side_guard_losses')} | "
            f"{summary.get('suppressed_exits')} | "
            f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
            f"{fmt(summary.get('suppressed_loser_cost_cents'))} | "
            f"{summary.get('value_only_suppressed_exits')} | "
            f"{fmt(summary.get('value_only_suppressed_loser_cost_cents'))} | "
            f"{summary.get('full_loss_cushion_estimate')} | {', '.join(summary.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Suppressed-Loser Attribution",
            "",
            "The guarded suppressed-loser fields count only exits actually suppressed by the feature-side guard. "
            "The value-only fields preserve the parent value-exit diagnostic that the guard is filtering.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
