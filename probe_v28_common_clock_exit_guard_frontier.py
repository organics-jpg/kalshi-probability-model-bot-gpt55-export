"""Promotion frontier for the common-clock v28 exit guard family.

Research-only; no live bot changes, process control, or orders.

The full-policy scorecard picks the highest-net common-clock guard, but the
fastest path to a live-test review may be a sibling window with more strict
suppression density. This probe keeps both views explicit.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RUNWAY_JSON = OUT_DIR / "v28_common_clock_exit_guard_runway_latest.json"
FULL_POLICY_JSON = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"
SPEC_JSON = OUT_DIR / "v28_common_clock_exit_guard_live_test_spec_latest.json"
OUT_JSON = OUT_DIR / "v28_common_clock_exit_guard_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_common_clock_exit_guard_frontier_latest.md"

MIN_SUPPRESSED = 30


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
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def inum(value: Any) -> int:
    return int(fnum(value))


def money(cents: Any) -> str:
    value = fnum(cents)
    return f"{value:.0f}c (${value / 100.0:.2f})"


def suppression_needed(row: dict[str, Any]) -> int:
    return max(0, MIN_SUPPRESSED - inum(row.get("suppressed_exits")))


def rank_row(row: dict[str, Any]) -> tuple[Any, ...]:
    """Sort by promotion distance first, then safety, then economics."""
    harmful = inum(row.get("harmful_suppressed_rows"))
    loss_cost = fnum(row.get("loss_control_cost_cents"))
    return (
        suppression_needed(row),
        harmful,
        1 if loss_cost < 0 else 0,
        -inum(row.get("full_loss_cushion")),
        -fnum(row.get("delta_vs_current_cents")),
        -fnum(row.get("candidate_cents")),
        str(row.get("window") or ""),
    )


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "window": row.get("window"),
        "settled": row.get("settled"),
        "candidate_cents": row.get("candidate_cents"),
        "current_cents": row.get("current_cents"),
        "delta_vs_current_cents": row.get("delta_vs_current_cents"),
        "candidate_wl": row.get("candidate_wl"),
        "current_wl": row.get("current_wl"),
        "suppressed_exits": row.get("suppressed_exits"),
        "suppressed_needed": suppression_needed(row),
        "helpful_suppressed_rows": row.get("helpful_suppressed_rows"),
        "harmful_suppressed_rows": row.get("harmful_suppressed_rows"),
        "loss_control_cost_cents": row.get("loss_control_cost_cents"),
        "full_loss_cushion": row.get("full_loss_cushion"),
        "missing_gates": row.get("missing_gates"),
    }


def build_report() -> dict[str, Any]:
    runway = load_json(RUNWAY_JSON)
    full_policy = load_json(FULL_POLICY_JSON)
    spec = load_json(SPEC_JSON)

    windows = [
        row for row in (runway.get("strict_windows") or [])
        if isinstance(row, dict)
    ]
    ranked = sorted(windows, key=rank_row)
    net_ranked = sorted(windows, key=lambda row: fnum(row.get("candidate_cents")), reverse=True)
    delta_ranked = sorted(windows, key=lambda row: fnum(row.get("delta_vs_current_cents")), reverse=True)
    readiness_frontier = ranked[0] if ranked else {}
    net_leader = net_ranked[0] if net_ranked else {}
    delta_leader = delta_ranked[0] if delta_ranked else {}

    all_clean = [
        row for row in windows
        if inum(row.get("harmful_suppressed_rows")) == 0
        and fnum(row.get("loss_control_cost_cents")) >= 0.0
        and fnum(row.get("candidate_cents")) > 0.0
        and fnum(row.get("delta_vs_current_cents")) > 0.0
    ]

    if not windows:
        decision = "no_common_clock_windows"
    elif suppression_needed(readiness_frontier) > 0:
        decision = "monitor_readiness_frontier"
    elif spec.get("decision") != "manual_live_test_review_required":
        decision = "review_blocked_by_global_live_gates"
    else:
        decision = "manual_live_test_review_required"

    return {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Compare common-clock exit-guard siblings by promotion distance and economics.",
        "decision": decision,
        "target_policy": runway.get("target_policy"),
        "live_baseline_cents": runway.get("live_baseline_cents"),
        "readiness_frontier": compact(readiness_frontier) if readiness_frontier else {},
        "net_leader": compact(net_leader) if net_leader else {},
        "delta_leader": compact(delta_leader) if delta_leader else {},
        "clean_positive_windows": [compact(row) for row in all_clean],
        "ranked_windows": [compact(row) for row in ranked],
        "interpretation": [
            "Use the readiness frontier for the next live-review runway because it needs the fewest strict suppressions.",
            "Keep the net leader alive as a sibling watch; do not switch solely for higher net while it has less forward density.",
            "No common-clock window may trade live until full-policy, live-readiness, single-process ownership, and reconciliation gates pass.",
        ],
        "sources": {
            "runway": str(RUNWAY_JSON),
            "full_policy": str(FULL_POLICY_JSON),
            "live_test_spec": str(SPEC_JSON),
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ready = report.get("readiness_frontier") or {}
    net = report.get("net_leader") or {}
    lines = [
        "# v28 Common-Clock Exit Guard Frontier",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Target policy: `{report.get('target_policy')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        "",
        "## Readiness Frontier",
        "",
        f"- Window: `{ready.get('window')}`",
        f"- Candidate/current/delta: `{money(ready.get('candidate_cents'))}` / `{money(ready.get('current_cents'))}` / `{money(ready.get('delta_vs_current_cents'))}`",
        f"- W/L: `{ready.get('candidate_wl')}`",
        f"- Suppressions needed: `{ready.get('suppressed_exits')}/{MIN_SUPPRESSED}`; missing `{ready.get('suppressed_needed')}`",
        f"- Helpful/harmful: `{ready.get('helpful_suppressed_rows')}/{ready.get('harmful_suppressed_rows')}`",
        f"- Loss cost/cushion: `{money(ready.get('loss_control_cost_cents'))}` / `{ready.get('full_loss_cushion')}`",
        "",
        "## Net Leader",
        "",
        f"- Window: `{net.get('window')}`",
        f"- Candidate/current/delta: `{money(net.get('candidate_cents'))}` / `{money(net.get('current_cents'))}` / `{money(net.get('delta_vs_current_cents'))}`",
        f"- Suppressions needed: `{net.get('suppressed_exits')}/{MIN_SUPPRESSED}`; missing `{net.get('suppressed_needed')}`",
        "",
        "## Ranked Windows",
        "",
        "| window | candidate | delta | W/L | suppressions | need | helpful/harmful | loss cost | cushion | missing gates |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.get("ranked_windows") or []:
        lines.append(
            f"| `{row.get('window')}` | {money(row.get('candidate_cents'))} | "
            f"{money(row.get('delta_vs_current_cents'))} | `{row.get('candidate_wl')}` | "
            f"{row.get('suppressed_exits')} | {row.get('suppressed_needed')} | "
            f"{row.get('helpful_suppressed_rows')}/{row.get('harmful_suppressed_rows')} | "
            f"{money(row.get('loss_control_cost_cents'))} | {row.get('full_loss_cushion')} | "
            f"`{', '.join(row.get('missing_gates') or [])}` |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
