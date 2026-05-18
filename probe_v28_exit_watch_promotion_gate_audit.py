"""Strict promotion-gate audit for active v28 exit/state watches.

Research-only; no live bot changes or orders.

This joins the exit dashboard, denominator audit, and dashboard coverage audit
into one gate table. It does not discover or score rules. Its purpose is to
make the current "why not promotable" answer explicit for each active exit
watch without weakening the existing forward-evidence gates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
DENOMINATOR_JSON = OUT_DIR / "v28_exit_watch_denominator_audit_latest.json"
COVERAGE_JSON = OUT_DIR / "v28_exit_dashboard_coverage_audit_latest.json"
REGISTRY_JSON = OUT_DIR / "v28_candidate_registry_coverage_audit_latest.json"
FALSE_HOLD_GUARDRAIL_JSON = OUT_DIR / "v28_exit_false_hold_guardrail_bridge_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_watch_promotion_gate_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_watch_promotion_gate_audit_latest.md"

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


def indexed_rows(payload: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        if isinstance(row, dict) and row.get(key):
            out[str(row.get(key))] = row
    return out


def coverage_by_lane(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        lane = row.get("dashboard_lane")
        if lane:
            out[str(lane)] = row
    return out


def hard_blockers(row: dict[str, Any], denominator_read: str) -> list[str]:
    blockers = set(str(item) for item in (row.get("blockers") or []))
    status = str(row.get("status") or "")
    settled = int(fnum(row.get("settled")))
    suppressed = int(fnum(row.get("suppressed_exits")))
    net = fnum(row.get("candidate_net_cents"))
    delta = fnum(row.get("delta_vs_current_cents"))
    loss_cost = fnum(row.get("loss_control_cost_cents"))
    reasons: list[str] = []
    if denominator_read == "too_new_no_base_exit_rows":
        reasons.append("no_base_exit_rows_after_freeze")
    if denominator_read == "watch_specific_overlap_not_collecting":
        reasons.append("watch_specific_overlap_not_collecting")
    if denominator_read == "watch_join_or_filter_not_collecting":
        reasons.append("possible_join_or_filter_gap")
    if status == "waiting_rule_has_not_fired" or denominator_read == "denominator_collecting_rule_not_firing":
        reasons.append("rule_not_firing_yet")
    if settled < MIN_SETTLED:
        reasons.append("settled_lt_30")
    if suppressed < MIN_SUPPRESSED:
        reasons.append("suppressed_decisions_lt_30")
    if net <= 0:
        reasons.append("net_not_positive")
    if delta <= 0:
        reasons.append("delta_not_positive")
    if net < MIN_CUSHION_CENTS:
        reasons.append("full_loss_cushion_lt_3")
    if loss_cost < 0 or "suppressed_loss_control_cost_negative" in blockers:
        reasons.append("loss_control_cost_negative")
    if "suppressed_losers_present" in blockers:
        reasons.append("suppressed_losers_present")
    return sorted(set(reasons))


def primary_read(blockers: list[str]) -> str:
    if "possible_join_or_filter_gap" in blockers:
        return "investigate_wiring"
    if "strict_false_hold_guardrail_unresolved" in blockers:
        return "blocked_false_hold_guardrail"
    if "loss_control_cost_negative" in blockers or "suppressed_losers_present" in blockers:
        return "blocked_loss_control_harm"
    if "no_base_exit_rows_after_freeze" in blockers:
        return "waiting_for_denominator"
    if "watch_specific_overlap_not_collecting" in blockers:
        return "waiting_for_watch_overlap"
    if "rule_not_firing_yet" in blockers:
        return "collecting_rule_not_firing"
    if "net_not_positive" in blockers or "delta_not_positive" in blockers:
        return "blocked_not_positive"
    if "settled_lt_30" in blockers or "suppressed_decisions_lt_30" in blockers:
        return "immature_sample_or_density"
    if "full_loss_cushion_lt_3" in blockers:
        return "fragility_cushion_short"
    return "review_ready"


def priority(row: dict[str, Any]) -> tuple[int, int, int, float, float]:
    read = str(row.get("primary_read") or "")
    bucket = {
        "review_ready": 0,
        "immature_sample_or_density": 1,
        "fragility_cushion_short": 2,
        "collecting_rule_not_firing": 3,
        "waiting_for_denominator": 4,
        "waiting_for_watch_overlap": 4,
        "blocked_not_positive": 5,
        "blocked_loss_control_harm": 6,
        "blocked_false_hold_guardrail": 6,
        "investigate_wiring": 7,
    }.get(read, 8)
    return (
        bucket,
        int(row.get("rows_needed_for_30") or 0),
        int(row.get("suppressed_needed_for_30") or 0),
        fnum(row.get("cushion_cents_needed")),
        -fnum(row.get("delta_vs_current_cents")),
    )


def guardrail_applies(lane: str, false_hold: dict[str, Any]) -> bool:
    if not false_hold:
        return False
    harmful = int(fnum(false_hold.get("strict_harmful_suppressions")))
    if harmful <= 0:
        return False
    lane_text = lane.lower()
    if "loss_guard" in lane_text and "v2" in lane_text:
        return False
    if "loss_guard" in lane_text and "v3" in lane_text:
        return False
    if lane_text in {"common_clock_strict_forward_v2", "common_clock_strict_forward_v3"}:
        return False
    return any(
        key in lane_text
        for key in (
            "book_gap",
            "dual_exit",
            "reduce",
            "value",
            "midband",
            "clip",
            "shallow",
        )
    )


def build_report() -> dict[str, Any]:
    dashboard = load_json(DASHBOARD_JSON)
    denominator = load_json(DENOMINATOR_JSON)
    coverage = load_json(COVERAGE_JSON)
    registry = load_json(REGISTRY_JSON)
    false_hold = load_json(FALSE_HOLD_GUARDRAIL_JSON)
    false_hold_summary = false_hold.get("summary") or {}
    denom_rows = indexed_rows(denominator, "lane")
    coverage_rows = coverage_by_lane(coverage)
    rows: list[dict[str, Any]] = []

    for item in dashboard.get("rows") or []:
        if not isinstance(item, dict):
            continue
        lane = str(item.get("lane") or "")
        if not lane:
            continue
        denom = denom_rows.get(lane, {})
        cov = coverage_rows.get(lane, {})
        settled = int(fnum(item.get("settled")))
        suppressed = int(fnum(item.get("suppressed_exits")))
        net = fnum(item.get("candidate_net_cents"))
        denominator_read = str(denom.get("denominator_read") or "missing_denominator_row")
        blockers = hard_blockers(item, denominator_read)
        false_hold_required = suppressed > 0 and guardrail_applies(lane, false_hold)
        if false_hold_required:
            blockers.append("strict_false_hold_guardrail_unresolved")
        primary = primary_read(blockers)
        rows.append(
            {
                "lane": lane,
                "gate": cov.get("gate"),
                "status": item.get("status"),
                "primary_read": primary,
                "promotion_gate_pass": primary == "review_ready",
                "freeze_ts_utc": item.get("freeze_ts_utc"),
                "denominator_read": denominator_read,
                "base_exit_rows_after_freeze": denom.get("base_exit_rows_after_freeze"),
                "settled": settled,
                "suppressed_exits": suppressed,
                "candidate_net_cents": net,
                "delta_vs_current_cents": fnum(item.get("delta_vs_current_cents")),
                "loss_control_cost_cents": fnum(item.get("loss_control_cost_cents")),
                "full_loss_cushion": item.get("full_loss_cushion"),
                "false_hold_guardrail_required": false_hold_required,
                "false_hold_guardrail_tags": false_hold_summary.get("top_guardrail_tags") if false_hold_required else {},
                "strict_false_hold_harm_cents": false_hold.get("strict_net_harm_cents") if false_hold_required else 0,
                "tracker_rows": cov.get("tracker_rows"),
                "diagnostic_rows": cov.get("diagnostic_rows"),
                "post_birth_rows": cov.get("post_birth_rows"),
                "rows_needed_for_30": max(0, MIN_SETTLED - settled),
                "suppressed_needed_for_30": max(0, MIN_SUPPRESSED - suppressed),
                "cushion_cents_needed": max(0.0, MIN_CUSHION_CENTS - net),
                "hard_blockers": blockers,
            }
        )

    rows.sort(key=priority)
    read_counts: dict[str, int] = {}
    for row in rows:
        read = str(row.get("primary_read"))
        read_counts[read] = read_counts.get(read, 0) + 1

    report = {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "dashboard": str(DASHBOARD_JSON),
            "denominator": str(DENOMINATOR_JSON),
            "coverage": str(COVERAGE_JSON),
            "registry": str(REGISTRY_JSON),
            "false_hold_guardrail": str(FALSE_HOLD_GUARDRAIL_JSON),
        },
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED,
            "min_cushion_cents": MIN_CUSHION_CENTS,
        },
        "registry_active_complete": bool(registry.get("active_registry_complete")),
        "registry_active_missing_rows": registry.get("active_missing_rows"),
        "coverage_missing_dashboard_review_gates": coverage.get("missing_dashboard_review_gates") or [],
        "false_hold_guardrail": {
            "strict_harmful_suppressions": false_hold.get("strict_harmful_suppressions"),
            "strict_net_harm_cents": false_hold.get("strict_net_harm_cents"),
            "top_guardrail_tags": false_hold_summary.get("top_guardrail_tags"),
        },
        "promotion_gate_pass_count": sum(1 for row in rows if row.get("promotion_gate_pass")),
        "primary_read_counts": dict(sorted(read_counts.items())),
        "rows": rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    rows = report.get("rows") or []
    pass_rows = [row for row in rows if row.get("promotion_gate_pass")]
    closest = [
        row for row in rows
        if row.get("primary_read") in {"immature_sample_or_density", "fragility_cushion_short"}
    ]
    notes = [
        "Research-only promotion gate audit; it does not score new rules, change live logic, or approve a candidate.",
        "Exit watches require strict post-freeze evidence: >=30 settled rows, >=30 suppressed decisions, positive net/delta, non-negative loss-control cost, and >=300c net cushion.",
        f"Promotion gate pass count is {len(pass_rows)}.",
        f"Registry active complete is {report.get('registry_active_complete')} with {report.get('registry_active_missing_rows')} missing active rows.",
        f"Dashboard coverage missing-review gates: {report.get('coverage_missing_dashboard_review_gates')}.",
    ]
    guardrail = report.get("false_hold_guardrail") or {}
    if guardrail.get("strict_harmful_suppressions"):
        notes.append(
            f"False-hold guardrail is active: strict harmful suppressions {guardrail.get('strict_harmful_suppressions')} "
            f"for {guardrail.get('strict_net_harm_cents')}c, top tags {guardrail.get('top_guardrail_tags')}."
        )
    if closest:
        best = closest[0]
        notes.append(
            f"Closest watch remains {best.get('lane')}: {best.get('settled')} settled, "
            f"{best.get('suppressed_exits')} suppressions, {best.get('candidate_net_cents')}c net, "
            f"{best.get('delta_vs_current_cents')}c delta, blockers {best.get('hard_blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if value is None:
        return "n/a"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Watch Promotion Gate Audit",
        "",
        "Research-only promotion-gate view. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion gate pass count: `{report.get('promotion_gate_pass_count')}`",
        f"- Primary read counts: `{report.get('primary_read_counts')}`",
        f"- Registry active complete/missing: `{report.get('registry_active_complete')}` / `{report.get('registry_active_missing_rows')}`",
        f"- Dashboard missing-review gates: `{report.get('coverage_missing_dashboard_review_gates')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    guardrail = report.get("false_hold_guardrail") or {}
    lines.extend(
        [
            "",
            "## False-Hold Guardrail",
            "",
            f"- Strict harmful suppressions: `{guardrail.get('strict_harmful_suppressions')}`",
            f"- Strict net harm: `{guardrail.get('strict_net_harm_cents')}` cents",
            f"- Top tags: `{guardrail.get('top_guardrail_tags')}`",
            "- Applied only to exit-watch lanes with at least one suppressed decision and a lane name matching the affected broad-hold mechanisms.",
        ]
    )
    lines.extend(
        [
            "",
            "## Gate Table",
            "",
            "| lane | gate | read | status | denom | base rows | settled | suppressed | net c | delta c | loss cost c | false hold guard | false hold harm c | rows need | supp need | cushion need | blockers |",
            "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('gate')}` | `{row.get('primary_read')}` | "
            f"`{row.get('status')}` | `{row.get('denominator_read')}` | "
            f"{fmt(row.get('base_exit_rows_after_freeze'))} | {row.get('settled')} | "
            f"{row.get('suppressed_exits')} | {fmt(row.get('candidate_net_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"`{row.get('false_hold_guardrail_required')}` | {fmt(row.get('strict_false_hold_harm_cents'))} | "
            f"{row.get('rows_needed_for_30')} | {row.get('suppressed_needed_for_30')} | "
            f"{fmt(row.get('cushion_cents_needed'))} | {', '.join(row.get('hard_blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
