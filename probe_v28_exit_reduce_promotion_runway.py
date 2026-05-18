"""Promotion runway for frozen v28 probability-reduce suppression.

Research-only; no live bot changes or orders.

The frozen reduce-suppression lane is currently the only forward candidate with
positive realized delta. This report defines what still has to happen before it
can be considered, and what would invalidate it.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
ROBUSTNESS_JSON = OUT_DIR / "v28_exit_reduce_suppression_robustness_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_promotion_runway_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_promotion_runway_latest.md"

MIN_SETTLED = 30


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


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    robustness = load_json(ROBUSTNESS_JSON)
    summary = frozen.get("summary") or {}
    rows = frozen.get("rows") if isinstance(frozen.get("rows"), list) else []
    settled = int(as_float(summary.get("settled")) or 0)
    current_delta = float(summary.get("delta_vs_current_cents") or 0.0)
    suppressed = [row for row in rows if row.get("suppressed") is True]
    suppressed_deltas = [float(row.get("delta_cents") or 0.0) for row in suppressed]
    rows_needed = max(0, MIN_SETTLED - settled)
    loss_control_cost = float(summary.get("loss_control_cost_cents") or 0.0)
    winner_recovery = float(summary.get("winner_clip_recovered_cents") or 0.0)
    invalidators = []
    if settled >= MIN_SETTLED and current_delta > 0.0 and loss_control_cost >= 0.0:
        status = "promotion_sample_ready"
    else:
        status = "collecting"
    if current_delta <= 0.0:
        invalidators.append("delta_not_positive")
    if loss_control_cost < 0.0:
        invalidators.append("suppressed_loss_control_cost_negative")
    if robustness.get("shadow_interest") is not True:
        invalidators.append("robustness_shadow_interest_false")
    runway = {
        "settled": settled,
        "rows_needed_for_30": rows_needed,
        "current_delta_cents": current_delta,
        "current_suppressed_exits": len(suppressed),
        "winner_clip_recovered_cents": winner_recovery,
        "loss_control_cost_cents": loss_control_cost,
        "positive_delta_buffer_cents": max(0.0, current_delta),
        "avg_positive_suppressed_delta_cents": sum(suppressed_deltas) / len(suppressed_deltas) if suppressed_deltas else None,
        "smallest_positive_suppressed_delta_cents": min(suppressed_deltas) if suppressed_deltas else None,
    }
    future_tests = [
        "Continue collecting until settled >= 30.",
        "Reject if cumulative delta versus current exits becomes <= 0.",
        "Reject if suppressed exits begin adding net loss-control cost; one suppressed loser is enough to require review.",
        "Keep collapse exits separate; this lane only concerns probability_reduce exits with p_hold >= 0.75.",
    ]
    return {
        "freeze": frozen.get("freeze") or {},
        "status": status,
        "runway": runway,
        "invalidators_now": invalidators,
        "future_tests": future_tests,
        "suppressed_rows": suppressed,
        "robustness": {
            "shadow_interest": robustness.get("shadow_interest"),
            "promotion_ready": robustness.get("promotion_ready"),
            "blockers": robustness.get("blockers") or [],
            "worst_leave_one_market": (robustness.get("leave_one_market") or [{}])[0],
            "worst_leave_one_suppressed": (robustness.get("leave_one_suppressed") or [{}])[0],
        },
        "interpretation": [
            f"Need {rows_needed} more settled future rows to reach the 30-row gate.",
            f"Current frozen delta is {current_delta}c over {settled} settled rows.",
            f"Suppressed exits so far: {len(suppressed)}; winner recovery {winner_recovery}c; loss-control cost {loss_control_cost}c.",
            "The fragile part is not PnL buffer; it is whether future suppressed reduce exits include losers.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    runway = report.get("runway") or {}
    lines = [
        "# v28 Exit Reduce Promotion Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Status: `{report.get('status')}`",
        f"- Invalidators now: `{', '.join(report.get('invalidators_now') or []) or 'none'}`",
        "",
        "## Runway",
        "",
        f"- Settled rows: `{runway.get('settled')}`",
        f"- Rows needed for 30: `{runway.get('rows_needed_for_30')}`",
        f"- Current delta: `{fmt(runway.get('current_delta_cents'))}c`",
        f"- Suppressed exits: `{runway.get('current_suppressed_exits')}`",
        f"- Winner recovery: `{fmt(runway.get('winner_clip_recovered_cents'))}c`",
        f"- Loss-control cost: `{fmt(runway.get('loss_control_cost_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Future Tests", ""])
    for note in report.get("future_tests") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Suppressed Rows",
        "",
        "| market | side | result | p_hold | current c | hold c | candidate c | delta c | worst hold mark |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("suppressed_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('candidate_cents'))} | "
            f"{fmt(row.get('delta_cents'))} | {fmt(row.get('worst_post_exit_hold_mark_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
