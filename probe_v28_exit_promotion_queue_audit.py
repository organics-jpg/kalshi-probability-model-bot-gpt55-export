"""Promotion-queue audit for v28 exit-policy watches.

Research-only; no live bot changes or orders.

This probe reads the exit-policy dashboard and turns the current watch state
into an explicit queue of what is still missing before any exit lane can enter
promotion review. It does not create a candidate or override any gate.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_exit_promotion_queue_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_promotion_queue_audit_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3
MIN_DELTA_CUSHION = 3


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


def as_int(value: Any) -> int:
    parsed = as_float(value)
    return 0 if parsed is None else int(parsed)


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def live_net_cents() -> float | None:
    payload = load_json(LIVE_SUMMARY_JSON)
    dollars = as_float(payload.get("net_pnl_total_dollars"))
    return None if dollars is None else round(dollars * 100.0, 6)


def cushion(cents: float | None) -> int:
    if cents is None or cents <= 0:
        return 0
    return int(cents // 100)


def runway(row: dict[str, Any]) -> dict[str, Any]:
    settled = as_int(row.get("settled"))
    suppressed = as_int(row.get("suppressed_exits"))
    candidate_net = as_float(row.get("candidate_net_cents")) or 0.0
    delta = as_float(row.get("delta_vs_current_cents")) or 0.0
    loss_cost = as_float(row.get("loss_control_cost_cents")) or 0.0
    blockers = list(row.get("blockers") or [])
    candidate_cushion = cushion(candidate_net)
    delta_cushion = cushion(delta)
    computed_blockers: list[str] = []
    if settled < MIN_SETTLED:
        computed_blockers.append("settled_lt_30")
    if suppressed < MIN_SUPPRESSED:
        computed_blockers.append("suppressed_decisions_lt_30")
    if candidate_net <= 0:
        computed_blockers.append("candidate_net_not_positive")
    if delta <= 0:
        computed_blockers.append("delta_not_positive")
    if loss_cost < 0:
        computed_blockers.append("suppressed_loss_control_cost_negative")
    if candidate_cushion < MIN_FULL_LOSS_CUSHION:
        computed_blockers.append("candidate_full_loss_cushion_lt_3")
    if delta_cushion < MIN_DELTA_CUSHION:
        computed_blockers.append("delta_full_loss_cushion_lt_3")
    if any("suppressed_losers_present" == str(blocker) for blocker in blockers):
        computed_blockers.append("suppressed_losers_present")
    missing = {
        "settled_rows_needed": max(0, MIN_SETTLED - settled),
        "suppressed_decisions_needed": max(0, MIN_SUPPRESSED - suppressed),
        "candidate_cents_needed_for_cushion3": max(0.0, MIN_FULL_LOSS_CUSHION * 100.0 - candidate_net),
        "delta_cents_needed_for_cushion3": max(0.0, MIN_DELTA_CUSHION * 100.0 - delta),
    }
    return {
        "lane": row.get("lane"),
        "candidate": row.get("candidate"),
        "status": row.get("status"),
        "freeze_ts_utc": row.get("freeze_ts_utc"),
        "settled": settled,
        "suppressed_exits": suppressed,
        "current_net_cents": as_float(row.get("current_net_cents")),
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": delta,
        "winner_recovery_cents": as_float(row.get("winner_recovery_cents")),
        "loss_control_cost_cents": loss_cost,
        "candidate_full_loss_cushion": candidate_cushion,
        "delta_full_loss_cushion": delta_cushion,
        "dashboard_blockers": blockers,
        "computed_blockers": computed_blockers,
        "missing": missing,
        "review_ready": not computed_blockers,
    }


def priority_score(row: dict[str, Any]) -> tuple[int, float, int, int, float]:
    missing = row.get("missing") or {}
    return (
        len(row.get("computed_blockers") or []),
        -float(row.get("delta_vs_current_cents") or -999999.0),
        int(missing.get("suppressed_decisions_needed") or 0),
        int(missing.get("settled_rows_needed") or 0),
        -float(row.get("candidate_net_cents") or -999999.0),
    )


def build_report() -> dict[str, Any]:
    dashboard = load_json(DASHBOARD_JSON)
    live_cents = live_net_cents()
    rows = [runway(row) for row in dashboard.get("rows") or []]
    forward_positive = [
        row for row in rows
        if row.get("status") in {"forward_positive_under_review", "positive_but_under_sample"}
        and (as_float(row.get("delta_vs_current_cents")) or 0.0) > 0
    ]
    blocked = [row for row in rows if str(row.get("status") or "").startswith("blocked")]
    waiting = [row for row in rows if str(row.get("status") or "").startswith("waiting")]
    forward_positive.sort(key=priority_score)
    review_ready = [row for row in forward_positive if row.get("review_ready")]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dashboard": str(DASHBOARD_JSON),
        "dashboard_generated_at_utc": dashboard.get("generated_at_utc"),
        "live_net_cents": live_cents,
        "gate_policy": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED,
            "min_candidate_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
            "min_delta_full_loss_cushion": MIN_DELTA_CUSHION,
            "loss_control_cost_must_be_nonnegative": True,
        },
        "review_ready_rows": review_ready,
        "forward_positive_queue": forward_positive,
        "blocked_count": len(blocked),
        "waiting_count": len(waiting),
        "interpretation": interpretation(forward_positive, review_ready),
    }


def interpretation(queue: list[dict[str, Any]], ready: list[dict[str, Any]]) -> list[str]:
    if ready:
        return [
            f"{len(ready)} exit watch row(s) clear the queue audit. They still require a full live-readiness review before any live change.",
        ]
    notes = ["No exit watch clears the promotion queue audit."]
    if queue:
        top = queue[0]
        missing = top.get("missing") or {}
        notes.append(
            f"Closest row is {top.get('lane')} with {top.get('settled')} settled, "
            f"{top.get('suppressed_exits')} suppressions, delta {top.get('delta_vs_current_cents')}c, "
            f"candidate/delta cushion {top.get('candidate_full_loss_cushion')}/{top.get('delta_full_loss_cushion')}, "
            f"missing suppressions {missing.get('suppressed_decisions_needed')} and delta cushion cents "
            f"{missing.get('delta_cents_needed_for_cushion3')}."
        )
        notes.append(
            "The active bottleneck is suppression density and delta cushion, not settled-row count, for the top book-gap/common-clock guards."
        )
    return notes


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Promotion Queue Audit",
        "",
        "Research-only audit; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Input dashboard: `{report.get('input_dashboard')}`",
        f"- Dashboard generated UTC: `{report.get('dashboard_generated_at_utc')}`",
        f"- Live baseline net: `{fmt(report.get('live_net_cents'))}c`",
        f"- Review-ready rows: `{len(report.get('review_ready_rows') or [])}`",
        f"- Forward-positive queue rows: `{len(report.get('forward_positive_queue') or [])}`",
        f"- Blocked/waiting counts: `{report.get('blocked_count')}/{report.get('waiting_count')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Forward-Positive Queue",
        "",
        "| rank | lane | status | settled | suppressed | candidate c | delta c | loss cost | cushion cand/delta | missing settled/supp/delta c | review ready | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for idx, row in enumerate(report.get("forward_positive_queue") or [], start=1):
        missing = row.get("missing") or {}
        blockers = row.get("computed_blockers") or []
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('status')}` | {row.get('settled')} | "
            f"{row.get('suppressed_exits')} | {fmt(row.get('candidate_net_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"{row.get('candidate_full_loss_cushion')}/{row.get('delta_full_loss_cushion')} | "
            f"{missing.get('settled_rows_needed')}/{missing.get('suppressed_decisions_needed')}/"
            f"{fmt(missing.get('delta_cents_needed_for_cushion3'))} | {row.get('review_ready')} | "
            f"{', '.join(blockers) or 'none'} |"
        )
    lines.extend([
        "",
        "## Gate Notes",
        "",
        "- This queue is stricter than the dashboard status: it requires both candidate and delta full-loss cushion.",
        "- A row that clears this queue still needs the separate live-readiness gate and a no-live-change review.",
        "- Diagnostic opportunity notes are not counted as strict evidence here.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
