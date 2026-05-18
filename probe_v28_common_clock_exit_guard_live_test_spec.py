"""Conditional live-test spec for the common-clock v28 exit guard.

Research-only; this probe never places orders or edits live bot logic.

The common-clock exit guard is currently the closest complete v28-derived
policy. This file defines the live-test contract that would be required after
the strict-forward density gate clears, while keeping the current state blocked.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RUNWAY_JSON = OUT_DIR / "v28_common_clock_exit_guard_runway_latest.json"
FRONTIER_JSON = OUT_DIR / "v28_common_clock_exit_guard_frontier_latest.json"
FULL_POLICY_JSON = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
LIVE_BOT = ROOT / "kalshi_btc15m_bot_ws.py"
OUT_JSON = OUT_DIR / "v28_common_clock_exit_guard_live_test_spec_latest.json"
OUT_MD = OUT_DIR / "v28_common_clock_exit_guard_live_test_spec_latest.md"


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


def source_contains(needle: str) -> bool:
    if not LIVE_BOT.exists():
        return False
    return needle in LIVE_BOT.read_text(encoding="utf-8", errors="ignore")


def money(cents: Any) -> str:
    value = fnum(cents)
    return f"{value:.0f}c (${value / 100.0:.2f})"


def build_report() -> dict[str, Any]:
    runway = load_json(RUNWAY_JSON)
    frontier = load_json(FRONTIER_JSON)
    full_policy = load_json(FULL_POLICY_JSON)
    live = load_json(LIVE_SUMMARY_JSON)
    best = runway.get("best_window") if isinstance(runway.get("best_window"), dict) else {}
    readiness = frontier.get("readiness_frontier") if isinstance(frontier.get("readiness_frontier"), dict) else {}
    density_window = readiness or best
    missing = list(density_window.get("missing_gates") or [])
    density_clear = not any(str(item).startswith("suppressed_needed_") for item in missing)
    loss_control_clear = (
        fnum(density_window.get("loss_control_cost_cents")) >= 0.0
        and int(fnum(density_window.get("harmful_suppressed_rows"))) == 0
    )
    full_policy_allows_live = any(card.get("live_test_allowed") for card in full_policy.get("all_policy_cards") or [])

    current_controls = {
        "live_lock": source_contains("live_trading.lock"),
        "strategy_approval_gate": source_contains("LIVE_APPROVED_STRATEGY_TAG"),
        "execution_events": source_contains("execution_events.ndjson"),
        "account_state_refresh": source_contains("maybe_refresh_live_account_state"),
        "separate_storage_tags": source_contains("BOT_STORAGE_TAG") and source_contains("resolve_strategy_paths"),
        "exit_signal_function": source_contains("detect_mushroom_v28_exit_signal"),
        "exit_guard_mode": source_contains("MUSHROOM_V28_EXIT_GUARD_MODE"),
        "exit_guard_evaluator": source_contains("evaluate_mushroom_v28_common_clock_exit_guard"),
        "exit_guard_shadow_ledger": source_contains("emit_mushroom_v28_exit_guard_shadow"),
    }
    single_process_exit_owner_ready = (
        current_controls["live_lock"]
        and current_controls["exit_signal_function"]
        and current_controls["exit_guard_mode"]
        and current_controls["exit_guard_evaluator"]
        and current_controls["exit_guard_shadow_ledger"]
    )
    candidate_kill_state_ready = (
        source_contains("EXIT_GUARD_MAX_DRAWDOWN")
        or source_contains("EXIT_GUARD_KILL")
        or source_contains("harmful_suppressed")
    )

    go_no_go = [
        {
            "gate": "strict_forward_density",
            "required": ">=30 strict suppressions in the selected common-clock window",
            "current": "pass" if density_clear else "blocked",
            "evidence": f"{density_window.get('window')} has {density_window.get('suppressed_exits')} suppressions; missing {missing}",
        },
        {
            "gate": "loss_control",
            "required": "0 harmful suppressions and non-negative loss-control cost",
            "current": "pass" if loss_control_clear else "blocked",
            "evidence": f"harmful={density_window.get('harmful_suppressed_rows')} loss_cost={density_window.get('loss_control_cost_cents')}c",
        },
        {
            "gate": "full_policy_live_gate",
            "required": "full-policy scorecard allows live test",
            "current": "pass" if full_policy_allows_live else "blocked",
            "evidence": full_policy.get("decision"),
        },
        {
            "gate": "single_process_exit_owner",
            "required": "candidate exit rule owns exits in the same live process or runs only as paper shadow",
            "current": "pass" if single_process_exit_owner_ready else "blocked",
            "evidence": "Source has live-lock, v28 exit path, guard mode, evaluator, and paper shadow ledger."
            if single_process_exit_owner_ready
            else "No source-level paper/enforce owner path for this guard.",
        },
        {
            "gate": "candidate_kill_state",
            "required": "candidate stops on harmful suppressed hold, loss cluster, drawdown, stale account, or accounting mismatch",
            "current": "pass" if candidate_kill_state_ready else "blocked",
            "evidence": "Candidate kill-state source hooks present."
            if candidate_kill_state_ready
            else "No candidate-specific kill-state source hooks found.",
        },
        {
            "gate": "exchange_reconciliation_plan",
            "required": "pre/post Kalshi balance, positions, fills, realized PnL, fees, exposure, and orders reconciled",
            "current": "planned_not_executed",
            "evidence": "No live candidate trial has started.",
        },
    ]

    blocked = [item for item in go_no_go if item["current"] != "pass"]
    decision = "blocked_do_not_live_test" if blocked else "manual_live_test_review_required"
    live_tag = "mushroom_v28_common_clock_exit_guard_v1_size1"
    storage_tag = "live_mushroom_v28_common_clock_exit_guard_size1"
    report = {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Conditional live-test contract for the nearest common-clock v28 exit guard. Research-only; no orders.",
        "decision": decision,
        "candidate": {
            "entry_rule": "Current v28 approved-entry stream.",
            "exit_state_rule": "Suppress selected current v28 exits using loss_guard_value_p85_reduce_p79_gap0.",
            "sizing_rule": "Start at size=1, max same-market position=1 for any future live trial.",
            "risk_kill_rule": "Stop candidate on any harmful suppressed hold, any net loss cluster >=3, drawdown >=200c, accounting mismatch, stale account state, or exchange reconciliation failure.",
            "live_test_rule": "Only one DRY_RUN=false process may own real exits. Until a production switch exists, run paper/virtual ledger only.",
            "accounting_pnl_rule": "Separate BOT_STORAGE_TAG, logs, stats, execution_events, exchange fills/orders/fees reconciliation, and live-only score comparison.",
            "iteration_rule": "No threshold tweaks during a live trial; version a new candidate after post-trial scoring names the blocker.",
        },
        "proposed_live_env": {
            "STRATEGY_TAG": live_tag,
            "BOT_STORAGE_TAG": storage_tag,
            "POSITION_SIZE": "1",
            "MULTI_ENTRY_SAME_MARKET_ENABLED": "false",
            "MULTI_ENTRY_MAX_POSITION_CONTRACTS": "1",
            "DRY_RUN": "false only after all go/no-go gates pass",
            "LIVE_APPROVED_STRATEGY_TAG": live_tag,
        },
        "proposed_artifacts": {
            "logs": f"logs/{storage_tag}/",
            "state": f"state/{storage_tag}/",
            "stats": f"stats/{storage_tag}/",
            "execution_events": f"logs/{storage_tag}/execution_events.ndjson",
            "exchange_reconciliation": f"logs/{storage_tag}/exchange_reconciliation.ndjson",
            "score_mode": "live_only",
        },
        "go_no_go": go_no_go,
        "current_controls": current_controls,
        "runway_best_window": best,
        "readiness_frontier_window": readiness,
        "live_baseline": {
            "strategy_tag": live.get("strategy_tag"),
            "entries_total": live.get("entries_total"),
            "completed_round_trips": live.get("completed_round_trips"),
            "net_cents": 100.0 * fnum(live.get("net_pnl_total_dollars")),
            "open_positions": live.get("open_positions"),
            "diagnosis": live.get("diagnosis"),
        },
    }
    return report


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    candidate = report.get("candidate") or {}
    env = report.get("proposed_live_env") or {}
    artifacts = report.get("proposed_artifacts") or {}
    best = report.get("runway_best_window") or {}
    readiness = report.get("readiness_frontier_window") or {}
    live = report.get("live_baseline") or {}
    lines: list[str] = [
        "# v28 Common-Clock Exit Guard Live-Test Spec",
        "",
        "Research-only. This probe does not place orders or edit live bot logic.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Live baseline: `{money(live.get('net_cents'))}`",
        f"- Best strict window: `{best.get('window')}`",
        f"- Readiness frontier window: `{readiness.get('window')}`",
        "",
        "## Candidate Contract",
        "",
    ]
    for key, value in candidate.items():
        lines.append(f"- {key.replace('_', ' ')}: {value}")
    lines.extend(
        [
            "",
            "## Go/No-Go Gates",
            "",
            "| gate | required | current | evidence |",
            "|---|---|---|---|",
        ]
    )
    for item in report.get("go_no_go") or []:
        lines.append(
            f"| `{item.get('gate')}` | {item.get('required')} | `{item.get('current')}` | {item.get('evidence')} |"
        )
    lines.extend(["", "## Proposed Live Env If Gates Pass", "", "| key | value |", "|---|---|"])
    for key, value in env.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Required Artifacts", "", "| artifact | path/value |", "|---|---|"])
    for key, value in artifacts.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Current Evidence",
            "",
            f"- Candidate/current: `{money(best.get('candidate_cents'))}` / `{money(best.get('current_cents'))}`",
            f"- Delta: `{money(best.get('delta_vs_current_cents'))}`",
            f"- Suppressions: `{best.get('suppressed_exits')}`",
            f"- Helpful/harmful: `{best.get('helpful_suppressed_rows')}/{best.get('harmful_suppressed_rows')}`",
            f"- Loss-control cost: `{money(best.get('loss_control_cost_cents'))}`",
            f"- Missing gates: `{', '.join(best.get('missing_gates') or [])}`",
            f"- Readiness frontier suppressions: `{readiness.get('suppressed_exits')}/30`; missing `{readiness.get('suppressed_needed')}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
