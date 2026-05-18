"""Promotion runway for strict common-clock exit-policy windows.

Research-only; no live bot changes or orders.

The common-clock watch is the apples-to-apples surface for exit repairs. This
probe converts the strict forward v1/v2/v3 rows into concrete missing gates so
positive-but-immature exit candidates do not get overstated.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COMMON_CLOCK_JSON = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_promotion_runway_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_promotion_runway_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_CUSHION_CENTS = 300.0


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


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def strict_windows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    windows = []
    for window in payload.get("windows") or []:
        if not isinstance(window, dict):
            continue
        name = str(window.get("window") or "")
        if name.startswith("new_exit_mix_common_forward_"):
            windows.append(window)
    return windows


def summary_score(row: dict[str, Any]) -> tuple[int, int, float, float]:
    blockers = row.get("blockers") or []
    net = as_float(row.get("candidate_gross_cents"), -1e9)
    delta = as_float(row.get("delta_vs_current_cents"), -1e9)
    suppressed = as_int(row.get("suppressed_exits"))
    return (len(blockers), -suppressed, -net, -delta)


def runway_for_summary(window: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    settled = as_int(summary.get("settled"))
    suppressed = as_int(summary.get("suppressed_exits"))
    candidate_net = as_float(summary.get("candidate_gross_cents"))
    current_net = as_float(summary.get("current_gross_cents"))
    delta = as_float(summary.get("delta_vs_current_cents"))
    loss_cost = as_float(summary.get("loss_control_cost_cents"))
    net_needed = max(0.0, MIN_CUSHION_CENTS - candidate_net)
    settled_needed = max(0, MIN_SETTLED - settled)
    suppressed_needed = max(0, MIN_SUPPRESSED - suppressed)
    future_rows_needed = max(settled_needed, suppressed_needed)
    avg_net_needed_per_future_row = net_needed / future_rows_needed if future_rows_needed else 0.0
    missing = []
    if settled_needed:
        missing.append(f"settled+{settled_needed}")
    if suppressed_needed:
        missing.append(f"suppressed+{suppressed_needed}")
    if candidate_net <= 0:
        missing.append("positive_net")
    if delta <= 0:
        missing.append("positive_delta")
    if loss_cost < 0:
        missing.append("no_loss_control_cost")
    if net_needed > 0:
        missing.append(f"cushion_cents+{net_needed:.0f}")
    return {
        "window": window.get("window"),
        "freeze_ts_utc": window.get("freeze_ts_utc"),
        "policy": summary.get("policy"),
        "settled": settled,
        "suppressed_exits": suppressed,
        "current_gross_cents": current_net,
        "candidate_gross_cents": candidate_net,
        "delta_vs_current_cents": delta,
        "winner_clip_recovered_cents": summary.get("winner_clip_recovered_cents"),
        "loss_control_cost_cents": loss_cost,
        "loss_count_reduction": summary.get("loss_count_reduction"),
        "candidate_wins": summary.get("candidate_wins"),
        "candidate_losses": summary.get("candidate_losses"),
        "helpful_suppressed_rows": summary.get("helpful_suppressed_rows"),
        "harmful_suppressed_rows": summary.get("harmful_suppressed_rows"),
        "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
        "reported_blockers": summary.get("blockers") or [],
        "missing_gates": missing,
        "settled_rows_needed": settled_needed,
        "suppressed_decisions_needed": suppressed_needed,
        "net_cents_needed_for_cushion3": net_needed,
        "future_rows_needed_if_all_suppressible": future_rows_needed,
        "avg_net_needed_per_future_row": avg_net_needed_per_future_row,
        "live_ready_by_exit_gates": not missing,
        "interpretation": (
            "strict positive but immature"
            if candidate_net > 0 and delta > 0 and loss_cost >= 0 and missing
            else "blocked"
        ),
    }


def build_report() -> dict[str, Any]:
    payload = load_json(COMMON_CLOCK_JSON)
    rows = []
    for window in strict_windows(payload):
        summaries = [row for row in window.get("summaries") or [] if isinstance(row, dict)]
        if not summaries:
            continue
        best_by_gate = sorted(summaries, key=summary_score)[0]
        best_positive = sorted(
            [
                row for row in summaries
                if as_float(row.get("candidate_gross_cents")) > 0
                and as_float(row.get("delta_vs_current_cents")) > 0
                and as_float(row.get("loss_control_cost_cents")) >= 0
            ],
            key=summary_score,
        )
        row = runway_for_summary(window, best_positive[0] if best_positive else best_by_gate)
        row["selected_basis"] = "best_positive_clean_delta" if best_positive else "best_by_gate_count"
        rows.append(row)
    rows.sort(
        key=lambda row: (
            len(row.get("missing_gates") or []),
            row.get("suppressed_decisions_needed") or 0,
            row.get("net_cents_needed_for_cushion3") or 0,
            -(as_float(row.get("candidate_gross_cents"))),
        )
    )
    report = {
        "generated_at_utc": utc_now_iso(),
        "source": str(COMMON_CLOCK_JSON),
        "common_clock_generated_at_utc": payload.get("generated_at_utc"),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED,
            "min_cushion_cents": MIN_CUSHION_CENTS,
        },
        "rows": rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a strict common-clock exit runway, not a promotion decision.",
    ]
    best = (report.get("rows") or [{}])[0]
    if best:
        notes.append(
            f"Closest strict exit row is {best.get('window')} / {best.get('policy')}: "
            f"{best.get('settled')} settled, {best.get('suppressed_exits')} suppressed, "
            f"{best.get('candidate_gross_cents')}c candidate net, {best.get('delta_vs_current_cents')}c delta."
        )
        notes.append(
            f"It still needs {best.get('suppressed_decisions_needed')} suppressed decisions and "
            f"{best.get('net_cents_needed_for_cushion3')}c cushion; do not use it live until strict rows mature."
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
        "# v28 Exit Common-Clock Promotion Runway",
        "",
        "Research-only runway. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Common-clock generated UTC: `{report.get('common_clock_generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Strict Windows",
        "",
        "| window | policy | settled | suppressed | current c | candidate c | delta c | loss cost | loss reduction | needed | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("rows") or []:
        needed = (
            f"settled {row.get('settled_rows_needed')}, "
            f"suppressed {row.get('suppressed_decisions_needed')}, "
            f"cushion {fmt(row.get('net_cents_needed_for_cushion3'))}c"
        )
        lines.append(
            f"| {row.get('window')} | {row.get('policy')} | {row.get('settled')} | "
            f"{row.get('suppressed_exits')} | {fmt(row.get('current_gross_cents'))} | "
            f"{fmt(row.get('candidate_gross_cents'))} | {fmt(row.get('delta_vs_current_cents'))} | "
            f"{fmt(row.get('loss_control_cost_cents'))} | {row.get('loss_count_reduction')} | "
            f"{needed} | {', '.join(row.get('missing_gates') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
