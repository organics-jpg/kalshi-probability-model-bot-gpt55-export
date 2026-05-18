"""Implementation-gap audit for the common-clock v28 exit guard.

Research-only; no live bot changes, process control, or orders.

This answers a narrow blocker from the live-test spec: can the candidate exit
guard currently own exits in the same live process, or at least run as a paper
shadow with complete attribution? The answer must be based on source evidence,
not intent.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_BOT = ROOT / "kalshi_btc15m_bot_ws.py"
SPEC_JSON = OUT_DIR / "v28_common_clock_exit_guard_live_test_spec_latest.json"
FRONTIER_JSON = OUT_DIR / "v28_common_clock_exit_guard_frontier_latest.json"
OUT_JSON = OUT_DIR / "v28_common_clock_exit_guard_implementation_gap_latest.json"
OUT_MD = OUT_DIR / "v28_common_clock_exit_guard_implementation_gap_latest.md"


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


def bot_source() -> str:
    if not LIVE_BOT.exists():
        return ""
    return LIVE_BOT.read_text(encoding="utf-8", errors="ignore")


def contains(src: str, needle: str) -> bool:
    return needle in src


def check(name: str, present: bool, evidence: str, required: str, note: str) -> dict[str, Any]:
    return {
        "name": name,
        "present": bool(present),
        "status": "present" if present else "missing",
        "evidence": evidence,
        "required": required,
        "note": note,
    }


def present_note(present: bool, when_present: str, when_missing: str) -> str:
    return when_present if present else when_missing


def build_report() -> dict[str, Any]:
    src = bot_source()
    spec = load_json(SPEC_JSON)
    frontier = load_json(FRONTIER_JSON)
    readiness = frontier.get("readiness_frontier") if isinstance(frontier.get("readiness_frontier"), dict) else {}

    existing_controls = [
        check(
            "single_live_lock",
            contains(src, "live_trading.lock") and contains(src, "Live trading lock already held"),
            "live_trading.lock + Live trading lock already held",
            "One DRY_RUN=false owner for the account.",
            "The bot already prevents a second independent live process.",
        ),
        check(
            "dry_run_strategy_approval",
            contains(src, "DRY_RUN=false is only allowed for strategy tag"),
            "DRY_RUN=false is only allowed for strategy tag",
            "Production trading requires an explicit approved strategy tag.",
            "The existing approval tag gate can protect a future candidate launch.",
        ),
        check(
            "separate_storage_tags",
            contains(src, "BOT_STORAGE_TAG") and contains(src, "resolve_strategy_paths"),
            "BOT_STORAGE_TAG + resolve_strategy_paths",
            "Separate state/log/stats paths per candidate.",
            "The bot can already isolate state and logs by storage tag.",
        ),
        check(
            "v28_live_exit_owner_path",
            contains(src, "MUSHROOM_V28_LIVE_EXIT_ENABLED") and contains(src, "detect_mushroom_v28_exit_signal"),
            "MUSHROOM_V28_LIVE_EXIT_ENABLED + detect_mushroom_v28_exit_signal",
            "Candidate rule must run inside the existing v28 exit path.",
            "There is a single-process v28 exit path to extend later.",
        ),
        check(
            "execution_telemetry",
            contains(src, "execution_events.ndjson") and contains(src, "telemetry.emit"),
            "execution_events.ndjson + telemetry.emit",
            "Decision, fill, and error telemetry must be available for scoring.",
            "Base telemetry exists, but candidate-specific guard decisions still need their own event.",
        ),
        check(
            "account_state_refresh",
            contains(src, "maybe_refresh_live_account_state") or contains(src, "LIVE_ACCOUNT_STATE"),
            "maybe_refresh_live_account_state/LIVE_ACCOUNT_STATE",
            "Live trial must stop on stale account state.",
            "Account-state controls exist for the broader bot.",
        ),
    ]

    common_clock_guard_mode_env = contains(src, "MUSHROOM_V28_EXIT_GUARD_MODE") or contains(src, "COMMON_CLOCK_EXIT_GUARD")
    side_effect_free_guard_evaluator = contains(src, "loss_guard_value_p85_reduce_p79_gap0") or contains(src, "should_loss_guard_suppress")
    paper_shadow_ledger = contains(src, "exit_guard_shadow") or contains(src, "MUSHROOM_V28_EXIT_GUARD_LEDGER_PATH")
    guard_applied_before_execute_exit_signal = (
        contains(src, "execute_exit_signal(signal, exit_source=\"mushroom_v28_ev\")")
        and (
            contains(src, "exit_guard_shadow")
            or contains(src, "COMMON_CLOCK_EXIT_GUARD")
            or contains(src, "MUSHROOM_V28_EXIT_GUARD_MODE")
        )
    )
    candidate_kill_state = contains(src, "EXIT_GUARD_MAX_DRAWDOWN") or contains(src, "EXIT_GUARD_KILL") or contains(src, "harmful_suppressed")
    exchange_reconciliation_writer = contains(src, "exchange_reconciliation.ndjson") or contains(src, "realized_pnl") or contains(src, "get_fills")

    missing_items = [
        check(
            "common_clock_guard_mode_env",
            common_clock_guard_mode_env,
            "MUSHROOM_V28_EXIT_GUARD_MODE or COMMON_CLOCK_EXIT_GUARD",
            "A disabled/paper/enforce switch for the exact loss_guard_value_p85_reduce_p79_gap0 rule.",
            present_note(
                common_clock_guard_mode_env,
                "A disabled/paper/enforce source-level switch is present.",
                "No source-level switch currently selects the common-clock guard.",
            ),
        ),
        check(
            "side_effect_free_guard_evaluator",
            side_effect_free_guard_evaluator,
            "loss_guard_value_p85_reduce_p79_gap0 or should_loss_guard_suppress",
            "A real-time evaluator using only current exit features, not settled outcomes.",
            present_note(
                side_effect_free_guard_evaluator,
                "A real-time evaluator is present in source.",
                "The rule exists in research probes, not in the live bot source.",
            ),
        ),
        check(
            "paper_shadow_ledger",
            paper_shadow_ledger,
            "exit_guard_shadow or MUSHROOM_V28_EXIT_GUARD_LEDGER_PATH",
            "Every would-suppress/keep decision must be logged before enforcement.",
            present_note(
                paper_shadow_ledger,
                "A dedicated candidate guard shadow ledger path/event is present.",
                "No dedicated candidate guard ledger is present in the live bot.",
            ),
        ),
        check(
            "guard_applied_before_execute_exit_signal",
            guard_applied_before_execute_exit_signal,
            "guard check before execute_exit_signal(... mushroom_v28_ev ...)",
            "The candidate must decide keep/suppress before real exit submission.",
            present_note(
                guard_applied_before_execute_exit_signal,
                "The v28 exit path has a guard decision point before real exit submission.",
                "The current v28 exit path submits the detected v28 signal directly.",
            ),
        ),
        check(
            "candidate_kill_state",
            candidate_kill_state,
            "EXIT_GUARD_* kill state or harmful_suppressed tracking",
            "Stop on harmful suppressed hold, loss cluster, drawdown, stale account, or accounting mismatch.",
            present_note(
                candidate_kill_state,
                "Candidate-specific kill-state hooks are present.",
                "The future kill rules are specified but not implemented for this candidate.",
            ),
        ),
        check(
            "exchange_reconciliation_writer",
            exchange_reconciliation_writer,
            "exchange_reconciliation.ndjson or fills/realized-pnl writer",
            "Pre/post balances, positions, fills, fees, exposure, and orders must be reconciled for live trial.",
            present_note(
                exchange_reconciliation_writer,
                "An exchange reconciliation writer is present.",
                "The candidate reconciliation artifact is planned, not written by the live bot.",
            ),
        ),
    ]

    blockers = [item["name"] for item in missing_items if not item["present"]]
    owner_blockers = {
        "common_clock_guard_mode_env",
        "side_effect_free_guard_evaluator",
        "paper_shadow_ledger",
        "guard_applied_before_execute_exit_signal",
    }
    if any(item in owner_blockers for item in blockers):
        decision = "blocked_no_single_process_exit_owner"
    elif blockers:
        decision = "blocked_kill_or_reconciliation_missing"
    else:
        decision = "implementation_ready_for_paper_shadow_review"
    return {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Source-backed implementation gap for the common-clock exit guard live-test blocker.",
        "decision": decision,
        "target_policy": "loss_guard_value_p85_reduce_p79_gap0",
        "candidate_rule": {
            "value_over_hold": "suppress when p_hold >= 0.85 or hold_book_gap >= 0.00",
            "probability_reduce": "suppress only when p_hold >= 0.79 and hold_book_gap >= 0.00",
            "collapse_or_full_drawdown": "keep current live exit behavior",
            "source": "probe_v28_frozen_exit_book_gap_loss_guard.py",
        },
        "readiness_frontier": readiness,
        "live_test_spec_decision": spec.get("decision"),
        "existing_controls": existing_controls,
        "missing_items": missing_items,
        "blockers": blockers,
        "next_build_steps": [
            "Exercise MUSHROOM_V28_EXIT_GUARD_MODE=paper in a dry-run or supervised shadow process before any enforce review.",
            "Add candidate kill-state and exchange reconciliation artifacts before DRY_RUN=false candidate approval.",
            "Only after density/live/kill/reconciliation gates pass, allow enforce mode to suppress qualifying soft exits before execute_exit_signal.",
        ],
        "sources": {
            "live_bot": str(LIVE_BOT),
            "live_test_spec": str(SPEC_JSON),
            "frontier": str(FRONTIER_JSON),
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ready = report.get("readiness_frontier") or {}
    lines = [
        "# v28 Common-Clock Exit Guard Implementation Gap",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Target policy: `{report.get('target_policy')}`",
        f"- Readiness frontier: `{ready.get('window')}` with `{ready.get('suppressed_exits')}/30` suppressions; missing `{ready.get('suppressed_needed')}`",
        f"- Live-test spec decision: `{report.get('live_test_spec_decision')}`",
        "",
        "## Candidate Rule",
        "",
    ]
    for key, value in (report.get("candidate_rule") or {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Existing Controls", "", "| control | status | evidence | note |", "|---|---|---|---|"])
    for item in report.get("existing_controls") or []:
        lines.append(f"| `{item.get('name')}` | `{item.get('status')}` | `{item.get('evidence')}` | {item.get('note')} |")
    lines.extend(["", "## Missing Implementation Items", "", "| item | status | required | note |", "|---|---|---|---|"])
    for item in report.get("missing_items") or []:
        lines.append(f"| `{item.get('name')}` | `{item.get('status')}` | {item.get('required')} | {item.get('note')} |")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- `{item}`" for item in report.get("blockers") or [])
    lines.extend(["", "## Next Build Steps", ""])
    lines.extend(f"- {item}" for item in report.get("next_build_steps") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
