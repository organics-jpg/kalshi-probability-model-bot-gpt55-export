"""Implementation spec for a safe dual-lane live-test coordinator.

Research-only. This writes a design/readiness artifact only; it does not place
orders, stop the live bot, or alter live bot behavior.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BLOCKER_JSON = OUT_DIR / "v28_dual_lane_live_test_blocker_audit_latest.json"
HANDOFF_JSON = OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.json"
LIVE_BOT = ROOT / "kalshi_btc15m_bot_ws.py"
OUT_JSON = OUT_DIR / "v28_dual_lane_live_test_coordinator_spec_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_live_test_coordinator_spec_latest.md"


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


def source_contains(needle: str) -> bool:
    if not LIVE_BOT.exists():
        return False
    return needle in LIVE_BOT.read_text(encoding="utf-8", errors="ignore")


def money(value: Any) -> str:
    try:
        cents = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def build_report() -> dict[str, Any]:
    blocker = load_json(BLOCKER_JSON)
    handoff = load_json(HANDOFF_JSON)
    same_window = handoff.get("same_window_live_compare") if isinstance(handoff.get("same_window_live_compare"), dict) else {}
    current_controls = {
        "single_live_lock": source_contains("Live trading lock already held"),
        "dry_run_false_strategy_approval": source_contains("DRY_RUN=false is only allowed for strategy tag"),
        "strategy_storage_tags": source_contains("BOT_STORAGE_TAG") and source_contains("resolve_strategy_paths"),
        "execution_events": source_contains("execution_events.ndjson"),
        "client_order_id_purpose_prefix": source_contains("btc15m-{purpose}-{uuid.uuid4()}"),
        "single_runtime_position_state": source_contains("self.state.position") and source_contains("opposite_side_position"),
    }
    missing_for_coordinator = [
        "production_dual_lane_decision_object",
        "single_process_strategy_router",
        "per_strategy_virtual_position_ledger",
        "shared_account_risk_budget",
        "same_market_conflict_policy",
        "per_strategy_client_order_id_prefix",
        "real_fill_attribution_replayer",
        "live_test_kill_switch_and_spend_cap",
    ]
    recommended_architecture = [
        {
            "component": "DualLaneDecisionAdapter",
            "purpose": "Emit a real-time entry/exit decision from the frozen dual-lane rules without reading settled outcomes.",
            "must_not_do": "Call post-hoc scorer rows that depend on settlement, reconstructed outcomes, or future exits.",
        },
        {
            "component": "LiveStrategyCoordinator",
            "purpose": "Run v28 and dual-lane decision adapters in one process behind the existing live lock.",
            "must_not_do": "Start a second DRY_RUN=false bot process or bypass state/live_trading.lock.",
        },
        {
            "component": "VirtualStrategyLedger",
            "purpose": "Attribute each order, fill, exit, and settlement to v28 or dual-lane using explicit strategy IDs.",
            "must_not_do": "Infer attribution only from market ticker after both strategies can trade the same market.",
        },
        {
            "component": "ConflictArbiter",
            "purpose": "Decide what happens when both strategies want the same market, same side, opposite side, or different sizes.",
            "must_not_do": "Allow two independent state machines to fight over the same account position.",
        },
        {
            "component": "RiskGovernor",
            "purpose": "Enforce size=1 initial dual-lane trades, max open exposure, max daily spend/loss, and emergency disable.",
            "must_not_do": "Let the test consume the whole account or assume v28 risk controls cover both strategies.",
        },
    ]
    go_no_go = [
        {
            "gate": "live_lock_respected",
            "required": "One DRY_RUN=false process holds the lock and coordinates both lanes.",
            "current_status": "blocked" if blocker.get("decision") == "blocked_do_not_start_second_live_bot" else "unknown",
        },
        {
            "gate": "dual_lane_realtime_engine",
            "required": "Dual-lane entry/exit rules run from current market/BTC/orderbook state only.",
            "current_status": "blocked",
        },
        {
            "gate": "attribution",
            "required": "Every order has lane-specific strategy ID/client_order_id and a fill replay can score each lane separately.",
            "current_status": "blocked",
        },
        {
            "gate": "risk_cap",
            "required": "Dual-lane size=1, configured max spend/loss, and operator-visible disable switch.",
            "current_status": "blocked",
        },
        {
            "gate": "evidence_context",
            "required": "Broad dual-lane no longer trails live v28 or is explicitly limited to overlay/risk-control tests.",
            "current_status": "blocked" if float(same_window.get("candidate_minus_live_same_markets_cents") or 0.0) <= 0 else "pass",
        },
    ]
    first_safe_milestone = {
        "name": "paper_coordinator_replay",
        "description": "Build the coordinator and run it in DRY_RUN=true/paper mode while the existing live v28 continues trading.",
        "success_criteria": [
            "Produces two separate ledgers: v28-live-compatible decisions and dual-lane decisions.",
            "Does not place orders or alter live bot state.",
            "Matches existing live v28 entries closely enough to prove the coordinator observes the same market stream.",
            "Shows dual-lane would have generated real-time actionable orders with no future-data dependencies.",
        ],
    }
    return {
        "generated_at_utc": utc_now_iso(),
        "decision": "coordinator_required_before_live_dual_lane",
        "current_controls": current_controls,
        "missing_for_coordinator": missing_for_coordinator,
        "recommended_architecture": recommended_architecture,
        "go_no_go": go_no_go,
        "first_safe_milestone": first_safe_milestone,
        "same_window_context": {
            "candidate_policy": same_window.get("candidate_policy"),
            "candidate_minus_live_same_markets_cents": same_window.get("candidate_minus_live_same_markets_cents"),
            "candidate_summary": same_window.get("candidate_summary"),
            "live_same_candidate_markets_summary": same_window.get("live_same_candidate_markets_summary"),
        },
        "next_build_steps": [
            "Extract a side-effect-free v28 decision adapter from the current bot path for paper comparison.",
            "Implement a side-effect-free dual-lane decision adapter from frozen observable rules only.",
            "Add a coordinator ledger schema with lane, market, side, action, intended_qty, order_id, client_order_id, fill_qty, fill_price, fees, and exit link.",
            "Run coordinator in paper mode against live market stream before enabling any dual-lane real orders.",
            "Only after paper coordinator passes attribution/replay checks, add a single-process live flag for dual-lane size=1 under hard spend/loss caps.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    same = report.get("same_window_context") if isinstance(report.get("same_window_context"), dict) else {}
    candidate = same.get("candidate_summary") if isinstance(same.get("candidate_summary"), dict) else {}
    live = same.get("live_same_candidate_markets_summary") if isinstance(same.get("live_same_candidate_markets_summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Live-Test Coordinator Spec",
        "",
        "Research-only. No orders placed, no live bot stopped, no live bot logic changed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        "",
        "## Why A Coordinator Is Required",
        "",
        "- The current live bot intentionally allows only one DRY_RUN=false process through `state/live_trading.lock`.",
        "- Running two independent bots would corrupt attribution and could make the two exit state machines fight over one account position.",
        "- Dual-lane is still a research scorer/probe family; it needs a real-time decision adapter before it can submit live orders.",
        "",
        "## Current Source Controls",
        "",
        "| control | present |",
        "|---|---|",
    ]
    for name, present in (report.get("current_controls") or {}).items():
        lines.append(f"| `{name}` | `{present}` |")
    lines.extend(
        [
            "",
            "## Same-Window Context",
            "",
            f"- Candidate policy: `{same.get('candidate_policy')}`",
            f"- Candidate W/L/net: `{candidate.get('wins')}/{candidate.get('losses')}` / `{money(candidate.get('net_cents'))}`",
            f"- Live v28 same-market W/L/net: `{live.get('wins')}/{live.get('losses')}` / `{money(live.get('net_cents'))}`",
            f"- Candidate minus live: `{money(same.get('candidate_minus_live_same_markets_cents'))}`",
            "",
            "## Required Architecture",
            "",
            "| component | purpose | must not do |",
            "|---|---|---|",
        ]
    )
    for item in report.get("recommended_architecture") or []:
        lines.append(f"| `{item.get('component')}` | {item.get('purpose')} | {item.get('must_not_do')} |")
    lines.extend(["", "## Go/No-Go Gates", "", "| gate | required | current |", "|---|---|---|"])
    for item in report.get("go_no_go") or []:
        lines.append(f"| `{item.get('gate')}` | {item.get('required')} | `{item.get('current_status')}` |")
    milestone = report.get("first_safe_milestone") if isinstance(report.get("first_safe_milestone"), dict) else {}
    lines.extend(
        [
            "",
            "## First Safe Milestone",
            "",
            f"- Name: `{milestone.get('name')}`",
            f"- Description: {milestone.get('description')}",
            "",
            "Success criteria:",
        ]
    )
    lines.extend(f"- {item}" for item in milestone.get("success_criteria") or [])
    lines.extend(["", "## Next Build Steps", ""])
    lines.extend(f"- {item}" for item in report.get("next_build_steps") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
