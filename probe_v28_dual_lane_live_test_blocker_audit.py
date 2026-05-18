"""Live-test blocker audit for the v28 dual-lane request.

Research-only audit. This does not place orders, stop the live bot, or change
live bot behavior.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_LOCK = ROOT / "state" / "live_trading.lock"
LIVE_BOT = ROOT / "kalshi_btc15m_bot_ws.py"
HANDOFF_JSON = OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_live_test_blocker_audit_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_live_test_blocker_audit_latest.md"


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


def read_text_contains(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    return needle in path.read_text(encoding="utf-8", errors="ignore")


def money(value: Any) -> str:
    try:
        cents = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def build_report() -> dict[str, Any]:
    lock = load_json(LIVE_LOCK)
    handoff = load_json(HANDOFF_JSON)
    lock_guard_present = read_text_contains(LIVE_BOT, "Live trading lock already held")
    live_approval_gate_present = read_text_contains(
        LIVE_BOT,
        "DRY_RUN=false is only allowed for strategy tag",
    )
    candidate_live_engine_present = read_text_contains(LIVE_BOT, "dual_lane") or read_text_contains(
        LIVE_BOT,
        "boundary_clock",
    )
    same_window = handoff.get("same_window_live_compare") if isinstance(handoff.get("same_window_live_compare"), dict) else {}
    blockers = []
    if lock.get("pid"):
        blockers.append("single_live_lock_already_held_by_v28")
    if lock_guard_present:
        blockers.append("second_independent_live_process_blocked_by_code_guard")
    if not candidate_live_engine_present:
        blockers.append("dual_lane_not_integrated_as_production_decision_engine")
    if float(same_window.get("candidate_minus_live_same_markets_cents") or 0.0) <= 0:
        blockers.append("dual_lane_trails_live_v28_same_window")
    blockers.append("independent_bots_would_contaminate_same_account_exit_and_position_attribution")
    required_work = [
        "Do not bypass the existing live lock for two independent live traders.",
        "Build a single-process live-test coordinator if simultaneous real trades are required.",
        "Coordinator must keep separate strategy tags, client_order_id prefixes, state, logs, market ledger, and PnL attribution.",
        "Coordinator must share one account-risk budget and explicitly arbitrate same-market/side/opposite-side conflicts.",
        "Dual-lane must be implemented as a production entry/exit lane, not called from post-hoc settled research probes.",
        "Start with position size 1 and a hard notional/spend cap if the coordinator is approved.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "requested_action": "run live v28 and live dual-lane simultaneously",
        "decision": "blocked_do_not_start_second_live_bot",
        "live_lock": lock,
        "lock_guard_present": lock_guard_present,
        "live_approval_gate_present": live_approval_gate_present,
        "candidate_live_engine_present": candidate_live_engine_present,
        "same_window": {
            "candidate_policy": same_window.get("candidate_policy"),
            "candidate_minus_live_same_markets_cents": same_window.get("candidate_minus_live_same_markets_cents"),
            "candidate_summary": same_window.get("candidate_summary"),
            "live_same_candidate_markets_summary": same_window.get("live_same_candidate_markets_summary"),
        },
        "blockers": blockers,
        "required_work": required_work,
        "artifact_paths": {
            "live_bot": str(LIVE_BOT),
            "live_lock": str(LIVE_LOCK),
            "handoff": str(OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.md"),
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    same = report.get("same_window") if isinstance(report.get("same_window"), dict) else {}
    candidate = same.get("candidate_summary") if isinstance(same.get("candidate_summary"), dict) else {}
    live = same.get("live_same_candidate_markets_summary") if isinstance(same.get("live_same_candidate_markets_summary"), dict) else {}
    lock = report.get("live_lock") if isinstance(report.get("live_lock"), dict) else {}
    lines = [
        "# v28 Dual-Lane Live-Test Blocker Audit",
        "",
        "Research-only. No orders placed, no live bot stopped, no live bot logic changed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Requested action: `{report.get('requested_action')}`",
        f"- Decision: `{report.get('decision')}`",
        "",
        "## Live Lock",
        "",
        f"- Current lock PID/strategy: `{lock.get('pid')}` / `{lock.get('strategy_tag')}`",
        f"- Lock acquired at: `{lock.get('acquired_at')}`",
        f"- Lock guard present in live bot: `{report.get('lock_guard_present')}`",
        f"- DRY_RUN=false approval-tag gate present: `{report.get('live_approval_gate_present')}`",
        "",
        "## Same-Window Performance Context",
        "",
        f"- Candidate policy: `{same.get('candidate_policy')}`",
        f"- Candidate W/L/net: `{candidate.get('wins')}/{candidate.get('losses')}` / `{money(candidate.get('net_cents'))}`",
        f"- Live v28 same-market W/L/net: `{live.get('wins')}/{live.get('losses')}` / `{money(live.get('net_cents'))}`",
        f"- Candidate minus live: `{money(same.get('candidate_minus_live_same_markets_cents'))}`",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.get("blockers") or [])
    lines.extend(["", "## Required Work Before Simultaneous Live Test", ""])
    lines.extend(f"- {item}" for item in report.get("required_work") or [])
    lines.extend(["", "## Artifacts", ""])
    for name, path in (report.get("artifact_paths") or {}).items():
        lines.append(f"- `{name}`: `{path}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
