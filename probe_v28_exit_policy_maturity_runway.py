"""Maturity runway for active v28 exit-policy watches.

Research-only; no live bot changes or orders.

This derives a review-readiness view from the consolidated exit dashboard. It
does not score new rules. Its purpose is to separate strict watches that are
positive but immature from rules that are blocked by actual loss-control harm.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_policy_maturity_runway_latest.json"
OUT_MD = OUT_DIR / "v28_exit_policy_maturity_runway_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_CUSHION_CENTS = 300


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def primary_failure(row: dict[str, Any]) -> str:
    blockers = set(row.get("blockers") or [])
    status = str(row.get("status") or "")
    if status == "waiting_no_post_freeze_rows":
        return "strict_forward_denominator_missing"
    if "suppressed_loss_control_cost_negative" in blockers or status == "blocked_loss_control_cost":
        return "exit_policy_loss_control_harm"
    if "net_not_positive" in blockers or status == "blocked_net_not_positive":
        return "strict_net_not_positive"
    if int(fnum(row.get("suppressed_exits"))) < MIN_SUPPRESSED:
        return "suppression_density_immature"
    if fnum(row.get("candidate_net_cents")) < MIN_CUSHION_CENTS:
        return "fragility_cushion_immature"
    return "watch_only_not_live_ready"


def priority(row: dict[str, Any]) -> tuple[int, float, float]:
    status = str(row.get("status") or "")
    loss_cost = fnum(row.get("loss_control_cost_cents"))
    settled = int(fnum(row.get("settled")))
    suppressed = int(fnum(row.get("suppressed_exits")))
    candidate = fnum(row.get("candidate_net_cents"))
    delta = fnum(row.get("delta_vs_current_cents"))
    if status == "positive_but_under_sample" and loss_cost >= 0:
        bucket = 0
    elif status.startswith("waiting") and row.get("opportunity"):
        bucket = 1
    elif status.startswith("blocked"):
        bucket = 2
    else:
        bucket = 3
    rows_needed = max(0, MIN_SETTLED - settled)
    suppressed_needed = max(0, MIN_SUPPRESSED - suppressed)
    cushion_needed = max(0.0, MIN_CUSHION_CENTS - candidate)
    return (bucket, rows_needed, suppressed_needed, cushion_needed, -delta)


def runway_row(row: dict[str, Any]) -> dict[str, Any]:
    settled = int(fnum(row.get("settled")))
    suppressed = int(fnum(row.get("suppressed_exits")))
    candidate = fnum(row.get("candidate_net_cents"))
    delta = fnum(row.get("delta_vs_current_cents"))
    cushion_needed = max(0.0, MIN_CUSHION_CENTS - candidate)
    return {
        "lane": row.get("lane"),
        "status": row.get("status"),
        "candidate": row.get("candidate"),
        "freeze_ts_utc": row.get("freeze_ts_utc"),
        "settled": settled,
        "suppressed_exits": suppressed,
        "candidate_net_cents": candidate,
        "delta_vs_current_cents": delta,
        "loss_control_cost_cents": fnum(row.get("loss_control_cost_cents")),
        "full_loss_cushion": row.get("full_loss_cushion"),
        "rows_needed_for_30": max(0, MIN_SETTLED - settled),
        "suppressed_needed_for_30": max(0, MIN_SUPPRESSED - suppressed),
        "net_cents_needed_for_cushion3": cushion_needed,
        "primary_failure": primary_failure(row),
        "blockers": row.get("blockers") or [],
        "opportunity": row.get("opportunity") or {},
        "promotion_read": "not_promotable",
    }


def build_report() -> dict[str, Any]:
    dashboard = load_json(DASHBOARD_JSON)
    rows = [runway_row(row) for row in dashboard.get("rows") or [] if isinstance(row, dict)]
    rows.sort(key=priority)
    failure_counts: dict[str, int] = {}
    for row in rows:
        failure = str(row.get("primary_failure"))
        failure_counts[failure] = failure_counts.get(failure, 0) + 1
    closest_positive = [
        row for row in rows
        if row.get("status") == "positive_but_under_sample"
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "dashboard_source": str(DASHBOARD_JSON),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED,
            "min_cushion_cents": MIN_CUSHION_CENTS,
        },
        "failure_counts": dict(sorted(failure_counts.items())),
        "closest_positive_watches": closest_positive,
        "rows": rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    closest = report.get("closest_positive_watches") or []
    notes = [
        "Research-only maturity view; no row here is a promotion decision.",
        "A strict exit watch still needs >=30 settled rows, >=30 suppressed decisions, positive net, non-negative loss-control cost, and at least 300c net for a three-full-loss cushion.",
    ]
    if closest:
        best = closest[0]
        notes.append(
            f"Closest positive watch is {best.get('lane')}: settled {best.get('settled')}, "
            f"suppressed {best.get('suppressed_exits')}, net {best.get('candidate_net_cents')}c, "
            f"delta {best.get('delta_vs_current_cents')}c; it still needs "
            f"{best.get('rows_needed_for_30')} rows, {best.get('suppressed_needed_for_30')} suppressions, "
            f"and {best.get('net_cents_needed_for_cushion3')}c cushion."
        )
    notes.append(f"Primary failure counts: {report.get('failure_counts')}.")
    return notes


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Policy Maturity Runway",
        "",
        "Research-only maturity/runway view. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Failure counts: `{report.get('failure_counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Watch Runway",
            "",
            "| lane | status | failure | settled | suppressed | net c | delta c | rows need | suppressed need | cushion c need | blockers |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('status')}` | `{row.get('primary_failure')}` | "
            f"{row.get('settled')} | {row.get('suppressed_exits')} | {fmt(row.get('candidate_net_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('rows_needed_for_30')} | "
            f"{row.get('suppressed_needed_for_30')} | {fmt(row.get('net_cents_needed_for_cushion3'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
