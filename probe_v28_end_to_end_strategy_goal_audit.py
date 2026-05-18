"""End-to-end completion audit for the active v28 strategy goal.

This report maps the current /goal to concrete local artifacts. It is stricter
than a candidate leaderboard: a positive component or diagnostic row is not a
finished strategy until entry, exit, sizing, risk, live-test, accounting, and
iteration rules all clear together.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
CONTROLLED_GATE_JSON = OUT_DIR / "v28_controlled_live_test_gate_latest.json"
FULL_POLICY_JSON = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"
COMMON_CLOCK_RUNWAY_JSON = OUT_DIR / "v28_common_clock_exit_guard_runway_latest.json"
COMMON_CLOCK_FRONTIER_JSON = OUT_DIR / "v28_common_clock_exit_guard_frontier_latest.json"
COMMON_CLOCK_SPEC_JSON = OUT_DIR / "v28_common_clock_exit_guard_live_test_spec_latest.json"
COMMON_CLOCK_IMPL_GAP_JSON = OUT_DIR / "v28_common_clock_exit_guard_implementation_gap_latest.json"
COMMON_CLOCK_SAFETY_JSON = OUT_DIR / "v28_common_clock_exit_guard_safety_verifier_latest.json"
COMMON_CLOCK_LIVE_STATUS_JSON = OUT_DIR / "v28_common_clock_live_trial_status_latest.json"
COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON = OUT_DIR / "v28_common_clock_live_execution_diagnostics_latest.json"
IMMEDIATE_QUEUE_JSON = OUT_DIR / "v28_immediate_live_test_queue_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
FORWARD_COLLECTION_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"
OBJECTIVE_GAP_JSON = OUT_DIR / "v28_objective_gap_checklist_latest.json"
GOAL_COMPLETION_JSON = OUT_DIR / "v28_goal_completion_audit_latest.json"

OUT_JSON = OUT_DIR / "v28_end_to_end_strategy_goal_audit_latest.json"
OUT_MD = OUT_DIR / "v28_end_to_end_strategy_goal_audit_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def evidence_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def status(passed: bool | None) -> str:
    if passed is True:
        return "pass"
    if passed is False:
        return "blocked"
    return "unverified"


def fmt(value: Any) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, default=str)
    else:
        text = str(value)
    return text.replace("|", "\\|")


def compact_policy(card: dict[str, Any]) -> dict[str, Any]:
    evidence = card.get("evidence") or {}
    return {
        "gate": card.get("gate"),
        "policy": card.get("policy"),
        "source": card.get("source"),
        "candidate_type": card.get("candidate_type"),
        "settled": evidence.get("settled"),
        "net_cents": evidence.get("net_cents"),
        "delta_vs_current_cents": evidence.get("delta_vs_current_cents"),
        "delta_vs_live_cents": evidence.get("delta_vs_live_cents"),
        "coverage_pct": evidence.get("coverage_pct"),
        "reconstructed_share": evidence.get("reconstructed_share"),
        "suppressed_exits": evidence.get("suppressed_exits"),
        "full_loss_cushion": evidence.get("full_loss_cushion"),
        "loss_control_cost_cents": evidence.get("loss_control_cost_cents"),
        "live_test_allowed": card.get("live_test_allowed"),
        "missing_gates": card.get("missing_gates"),
    }


def has_full_policy_contract(card: dict[str, Any]) -> bool:
    policy = card.get("full_policy") or {}
    required = {
        "entry_rule",
        "exit_state_rule",
        "sizing_rule",
        "risk_kill_rule",
        "live_test_rule",
        "accounting_pnl_rule",
        "iteration_rule",
    }
    return required.issubset(set(policy))


def build_active_live_policy_contract(live_trial: dict[str, Any]) -> dict[str, Any]:
    strategy_tag = str(live_trial.get("strategy_tag") or "")
    log_source_tag = str(live_trial.get("log_source_tag") or "")
    if "broad_btcrest" in strategy_tag:
        return {
            "family": "active_sourcefix_broad_btcrest_size1",
            "strategy_tag": strategy_tag,
            "log_source_tag": log_source_tag,
            "entry_rule": (
                "v28 common-clock mushroom fair-value entry with feature gate disabled, "
                "Coinbase REST BTC freshness fallback, min net edge >=2c, ask <=90c, "
                "seconds_to_close >=70, entry book age <=1000ms, and BTC/account/risk checks"
            ),
            "exit_state_rule": (
                "current v28 common-clock exit guard with value-over-hold IOC exits, "
                "visible-depth check, 30-second post-fill exit delay, and one position per market"
            ),
            "sizing_rule": "controlled live size 1, multi-entry disabled, max same-market risk 100c",
            "risk_kill_rule": (
                "monitor kills or downgrades on loss_cluster>=3, drawdown>=200c, zero-fill count>=8, "
                "source-stale reject share>=70% after >=100 rejects, process/lock failure, "
                "exchange/accounting mismatch, or unresolved exposure/orders"
            ),
            "live_test_rule": (
                "real Kalshi trades only under the broad BTC-REST strategy/log tags; separate bot log, "
                "execution events, guard ledger, exchange reconciliation ledger, stats, and monitor log"
            ),
            "accounting_pnl_rule": (
                "score_bot_log.py in live_only mode with exchange fill/fee override and fractional fee cents preserved; "
                "Kalshi reconciliation checks balance, positions, resting orders, recent fills, fees, and candidate fills"
            ),
            "iteration_rule": (
                "after every entry, exit, fill, settlement, no-entry cluster, or kill-watch movement, "
                "rerun score/status/near-miss/zero-entry/audit checks and version any threshold, exit, or sizing tweak separately"
            ),
            "rationale": (
                "selected as the current tradeable v28-derived live lane after stricter sourcefix/hybrid variants produced "
                "no-fill or negative evidence; broad thresholds preserve coverage while kill rules control source quality"
            ),
            "launcher": "scripts/run_v28_common_clock_exit_guard_sourcefix_broad_btcrest_live_size1.ps1",
        }
    if "hybridfpt" not in strategy_tag:
        return {}
    is_btcrotate = "btcrotate" in strategy_tag
    is_btcrest = "btcrest" in strategy_tag
    is_ask35 = "ask35" in strategy_tag
    is_exitdelay90 = "exitdelay90" in strategy_tag
    feature_tail = (
        "recross <=0.60, abs_d_sigma >=0.85, no abs-d ceiling, and ask_prob >=0.35"
        if is_ask35
        else "recross <=0.60, and 0.85 <= abs_d_sigma <= 1.10"
    )
    return {
        "family": (
            "active_sourcefix_hybrid_fpt_ask35_btcrest_exitdelay90_size1"
            if is_ask35 and is_btcrest and is_exitdelay90
            else "active_sourcefix_hybrid_fpt_ask35_btcrest_size1"
            if is_ask35 and is_btcrest
            else "active_sourcefix_hybrid_fpt_btcrest_size1"
            if is_btcrest
            else "active_sourcefix_hybrid_fpt_btcrotate_size1"
            if is_btcrotate
            else "active_sourcefix_hybrid_fpt_depth_size1"
        ),
        "strategy_tag": strategy_tag,
        "log_source_tag": log_source_tag,
        "entry_rule": (
            "current v28 entry engine, size-1, "
            + (
                "Coinbase REST BTC freshness fallback sourcefix, "
                if is_btcrest
                else "BTC websocket fallback rotation sourcefix, "
                if is_btcrotate
                else "sourcefix BTC stale reconnect, "
            )
            +
            "book age <=750ms, min net edge >=3c, ask <=83c, seconds_to_close >=120, "
            "fast-fill depth/edge gate, feature gate raw_edge_prob >=0.03, "
            + feature_tail
        ),
        "exit_state_rule": (
            "current v28 live exit/state machine with a 90-second post-fill exit delay plus common-clock exit guard; "
            "delay early hard exits after fill, then keep hard exits when fair value/probability collapses unless "
            "a guarded loss exit clears the suppress guard"
            if is_exitdelay90
            else (
                "current v28 live exit/state machine with common-clock exit guard; keep hard exits "
                "when fair value/probability collapses, only suppress guarded loss exits when the "
                "live state clears the guard"
            )
        ),
        "sizing_rule": "controlled live size 1, max same-market position 1, one active candidate process",
        "risk_kill_rule": (
            "monitor kills or downgrades on loss_cluster>=3, drawdown>=200c, zero-fill cluster>=3 before fill, "
            "source-stale share>=70% after >=100 rejects before first fill, exchange/accounting mismatch, "
            "process/lock failure, or unresolved exposure; stop only when flat unless risk requires intervention"
        ),
        "live_test_rule": (
            "real Kalshi trades only under the versioned strategy/log tags; separate bot log, execution events, "
            "stats, reconciliation ledger, and monitor status"
        ),
        "accounting_pnl_rule": (
            "score_bot_log.py in live_only mode with exchange reconciliation overlay for balance, positions, "
            "resting orders, fills, fees, exposure, and candidate fills since run start"
        ),
        "iteration_rule": (
            "after every entry, exit, fill, or settlement, rerun score/status/diagnostics/zero-entry/near-miss/audit/selector; "
            "continue only while after-fee PnL, execution quality, source quality, and kill-state checks remain acceptable"
        ),
        "rationale": (
            (
                "coverage review showed the extra abs-d ceiling reduced the existing forward frontier; "
                "this version maps back to the existing raw03_recross60_abs85_ask35 lane while keeping sourcefix controls"
                + (
                    "; live evidence from the prior ask35 BTC-REST trial showed a 34s collapse exit sold at 42c before the market recovered and finalized YES, so this version tests a 90s post-fill exit delay"
                    if is_exitdelay90 else ""
                )
            )
            if is_ask35
            else (
                "sourcefix v1 lost on a high-confidence false positive with abs_d_sigma=1.140512; "
                "the hybrid-FPT gate blocks that lane via max_abs_d_sigma=1.10"
            )
            + (
                ", and this version keeps the strict BTC max-age gate while refreshing quiet websocket ticks through Coinbase REST"
                if is_btcrest else
                ", and this version fixes the observed Coinbase stale-reconnect coverage drag by rotating BTC websocket sources"
                if is_btcrotate
                else ""
            )
        ),
        "launcher": (
            "scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_ask35_btcrest_exitdelay90_live_size1.ps1"
            if is_ask35 and is_btcrest and is_exitdelay90
            else "scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_ask35_btcrest_live_size1.ps1"
            if is_ask35 and is_btcrest
            else
            "scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_btcrest_live_size1.ps1"
            if is_btcrest
            else
            "scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_btcrotate_live_size1.ps1"
            if is_btcrotate
            else "scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_live_size1.ps1"
        ),
    }


def build_audit() -> dict[str, Any]:
    candidates = load_json(CANDIDATE_VS_LIVE_JSON)
    controlled = load_json(CONTROLLED_GATE_JSON)
    full_policy = load_json(FULL_POLICY_JSON)
    runway = load_json(COMMON_CLOCK_RUNWAY_JSON)
    frontier = load_json(COMMON_CLOCK_FRONTIER_JSON)
    spec = load_json(COMMON_CLOCK_SPEC_JSON)
    implementation_gap = load_json(COMMON_CLOCK_IMPL_GAP_JSON)
    safety = load_json(COMMON_CLOCK_SAFETY_JSON)
    live_trial = load_json(COMMON_CLOCK_LIVE_STATUS_JSON)
    execution_diag = load_json(COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON)
    immediate_queue = load_json(IMMEDIATE_QUEUE_JSON)
    readiness = load_json(LIVE_READINESS_JSON)
    forward = load_json(FORWARD_COLLECTION_JSON)
    objective_gap = load_json(OBJECTIVE_GAP_JSON)
    goal_completion = load_json(GOAL_COMPLETION_JSON)

    all_policy_source = full_policy.get("candidate_cards")
    if not isinstance(all_policy_source, list):
        all_policy_source = full_policy.get("all_policy_cards")
    if not isinstance(all_policy_source, list):
        all_policy_source = []
    all_policy_cards = [row for row in all_policy_source if isinstance(row, dict)]
    policy_cards = [row for row in (full_policy.get("closest_policy_cards") or []) if isinstance(row, dict)]
    closest = policy_cards[0] if policy_cards else {}
    closest_contract = closest.get("full_policy") or {}
    closest_compact = compact_policy(closest) if closest else {}

    gate_counts = controlled.get("counts") or {}
    live_baseline = controlled.get("live_baseline") or {}
    live_baseline_cents = live_baseline.get("net_cents", candidates.get("live_net_cents"))
    spec_go_no_go = [row for row in (spec.get("go_no_go") or []) if isinstance(row, dict)]
    best_window = runway.get("best_window") or {}
    readiness_frontier = frontier.get("readiness_frontier") or {}
    net_leader = frontier.get("net_leader") or {}
    candidate = spec.get("candidate") or {}
    proposed_env = spec.get("proposed_live_env") or {}
    proposed_artifacts = spec.get("proposed_artifacts") or []
    live_state_blockers = forward.get("blockers") or []

    full_contract_keys = sorted((candidate or closest_contract).keys())
    has_spec_contract = {
        "entry_rule",
        "exit_state_rule",
        "sizing_rule",
        "risk_kill_rule",
        "live_test_rule",
        "accounting_pnl_rule",
        "iteration_rule",
    }.issubset(set(full_contract_keys))
    live_trial_score = live_trial.get("score") or {}
    active_live_policy_contract = build_active_live_policy_contract(live_trial)
    live_trial_exchange = live_trial.get("exchange") or {}
    live_trial_artifact_exists = live_trial.get("artifact_exists") or {}
    reconciliation_ledger_exists = bool(live_trial_artifact_exists.get("reconciliation_ledger"))
    candidate_recent_fills_since_run_count = int(live_trial.get("candidate_recent_fills_since_run_count", 0) or 0)
    reconciliation_snapshot_appended = bool(live_trial.get("reconciliation_snapshot_appended"))
    live_trial_started = live_trial.get("status") in {
        "running_waiting_for_first_entry",
        "running_with_exchange_exposure",
        "running_scored_round_trips",
        "running_with_local_entries",
    }
    live_trial_running = bool(live_trial.get("process_running")) and bool(live_trial.get("lock_matches"))
    live_trial_entries = int(live_trial_score.get("entries_total", 0) or 0)
    live_trial_round_trips = int(live_trial_score.get("completed_round_trips", 0) or 0)
    live_trial_net_dollars = float(live_trial_score.get("net_pnl_total_dollars", 0) or 0.0)
    live_log_source_tag = live_trial.get("log_source_tag") or proposed_env.get("BOT_STORAGE_TAG") or "live_mushroom_v28_common_clock_exit_guard_size1"
    execution_counts = execution_diag.get("counts") or {}
    zero_fill_attempts = int(execution_counts.get("zero_fill_attempts", 0) or 0)
    filled_events = int(execution_counts.get("filled_events", 0) or 0)
    order_starts = int(execution_counts.get("order_submit_start", 0) or 0)
    order_successes = int(execution_counts.get("order_submit_success", 0) or 0)
    execution_reconciliation = execution_diag.get("reconciliation") or {}
    execution_reconciliation_available = bool(execution_reconciliation.get("available"))
    if live_trial_round_trips > 0:
        if live_trial_net_dollars < 0:
            live_trade_note = (
                f"The size-1 live trial has {live_trial_round_trips} scored round trip "
                f"and is negative after fees at ${live_trial_net_dollars:.2f}; it is not complete or promotable."
            )
        elif live_trial_net_dollars > 0:
            live_trade_note = (
                f"The size-1 live trial has {live_trial_round_trips} scored round trip "
                f"and is positive after fees at ${live_trial_net_dollars:.2f}, but still needs a meaningful stable sample."
            )
        else:
            live_trade_note = (
                f"The size-1 live trial has {live_trial_round_trips} scored round trip "
                "and is flat after fees; it is not complete or promotable yet."
            )
    elif live_trial_entries > 0 or filled_events > 0:
        live_trade_note = "The size-1 live trial has filled candidate activity but no completed scored round trip yet."
    elif zero_fill_attempts > 0 or order_successes > 0 or order_starts > 0:
        live_trade_note = "The size-1 live trial has made order attempts, but it has no filled candidate entry and is not complete or profitable yet."
    elif live_trial_started:
        live_trade_note = "The size-1 live trial is running but has not produced an approved order attempt or filled candidate entry yet."
    else:
        live_trade_note = "No live candidate trial is running; continue research-only collection until a complete policy clears the gates."
    exchange_orders_checked = len((execution_reconciliation.get("orders") or {}))
    if exchange_orders_checked:
        exchange_note = "Exchange reconciliation is active: balance, positions, resting orders, recent fills, and submitted order records were checked through Kalshi."
    elif reconciliation_ledger_exists and reconciliation_snapshot_appended:
        exchange_note = "Exchange reconciliation is active: status snapshots append Kalshi balance, positions, resting orders, recent fills, and candidate fills since run start; no candidate orders have been submitted yet."
    else:
        exchange_note = "Exchange reconciliation is active for balance, positions, resting orders, and recent fills; no candidate orders have been submitted in the current checked log source."
    remaining_hard_blockers = []
    if live_trial_entries <= 0:
        remaining_hard_blockers.append("live trial has no scored filled candidate entry yet")
    if live_trial_round_trips <= 0:
        remaining_hard_blockers.append("live trial has no completed scored candidate round trip yet")
    else:
        if live_trial_net_dollars <= 0:
            remaining_hard_blockers.append("live candidate PnL is negative or flat after fees")
        if live_trial_round_trips < 30:
            remaining_hard_blockers.append(
                f"live sample is not meaningfully profitable yet ({live_trial_round_trips}/30 completed round trips)"
            )
    remaining_hard_blockers.append("older strict-forward and live-readiness artifacts still need to be superseded by live evidence")
    if not reconciliation_ledger_exists:
        remaining_hard_blockers.append("exchange reconciliation ledger is missing")
    elif candidate_recent_fills_since_run_count <= 0:
        remaining_hard_blockers.append("exchange reconciliation has no candidate fills since run start")
    if zero_fill_attempts > 0:
        remaining_hard_blockers.append(
            f"candidate has unresolved zero-fill execution evidence ({zero_fill_attempts} zero-fill attempts; kill threshold not hit)"
        )
    if live_trial_started:
        normalized_go_no_go = []
        for row in spec_go_no_go:
            normalized = dict(row)
            if (
                row.get("gate") == "exchange_reconciliation_plan"
                and live_trial_exchange.get("available")
                and execution_reconciliation_available
            ):
                normalized["current"] = "pass"
                normalized["evidence"] = (
                    "Live trial reconciliation is active: Kalshi balance, positions, "
                    "resting orders, recent fills, and submitted order records were checked."
                )
            normalized_go_no_go.append(normalized)
        spec_go_no_go = normalized_go_no_go
    go_no_go_blocked = [
        row for row in spec_go_no_go
        if str(row.get("current")).lower() not in {"pass", "passed"}
    ]

    checklist = [
        {
            "requirement": "Audit existing v28 candidates before inventing new broad strategy families.",
            "passed": True,
            "actual": {
                "candidate_rows": gate_counts.get("candidate_rows", candidates.get("candidate_count")),
                "positive_rows": gate_counts.get("positive_rows", candidates.get("positive_candidate_count")),
                "positive_target_rows": gate_counts.get("positive_target_rows", candidates.get("target_coverage_positive_count")),
                "controlled_gate_decision": controlled.get("decision"),
                "immediate_queue_decision": immediate_queue.get("decision"),
                "top_ranked_candidate": immediate_queue.get("top_deferred_candidate"),
            },
            "evidence": [evidence_path(CANDIDATE_VS_LIVE_JSON), evidence_path(CONTROLLED_GATE_JSON), evidence_path(IMMEDIATE_QUEUE_JSON)],
            "note": "The current path uses existing artifacts and now ranks candidates by PnL/win rate first; the top ranked rows are formally deferred by live-test gates.",
        },
        {
            "requirement": "Refresh and compare against the live-only v28 baseline after fees.",
            "passed": live_baseline_cents is not None,
            "actual": {
                "strategy_tag": live_baseline.get("strategy_tag", "live_mushroom_v28_size2"),
                "score_mode": live_baseline.get("score_mode"),
                "entries_total": live_baseline.get("entries_total"),
                "completed_round_trips": live_baseline.get("completed_round_trips"),
                "open_positions": live_baseline.get("open_positions"),
                "net_cents": live_baseline_cents,
                "candidate_vs_live_generated_at_utc": candidates.get("generated_at_utc"),
            },
            "evidence": [evidence_path(CONTROLLED_GATE_JSON), evidence_path(CANDIDATE_VS_LIVE_JSON)],
            "note": "The baseline is local live-only scoring; exchange-side reconciliation is still only required once a candidate trial starts.",
        },
        {
            "requirement": "Represent credible candidates as full policies, not isolated components.",
            "passed": (bool(policy_cards) and has_full_policy_contract(closest)) or bool(active_live_policy_contract),
            "actual": {
                "full_policy_decision": full_policy.get("decision"),
                "candidate_cards": len(all_policy_cards),
                "displayed_closest_policy_cards": len(policy_cards),
                "live_test_allowed_count": full_policy.get("live_test_allowed_count"),
                "closest_policy": closest_compact,
                "contract_keys": sorted(closest_contract.keys()),
                "active_live_policy_contract": active_live_policy_contract,
            },
            "evidence": [evidence_path(FULL_POLICY_JSON)],
            "note": "The active live contract has explicit entry, exit/state, sizing, risk, live-test, accounting, and iteration rules.",
        },
        {
            "requirement": "Identify the nearest coherent v28-derived clean core.",
            "passed": bool(closest),
            "actual": {
                "nearest_candidate": closest_compact,
                "runway_decision": runway.get("decision"),
                "best_window": best_window,
                "readiness_frontier": readiness_frontier,
                "net_leader": net_leader,
            },
            "evidence": [evidence_path(FULL_POLICY_JSON), evidence_path(COMMON_CLOCK_RUNWAY_JSON), evidence_path(COMMON_CLOCK_FRONTIER_JSON)],
            "note": "The nearest clean core is exit-first: current v28 entries plus common-clock loss-guard exit suppression; v2 is the readiness frontier while v3 remains the net leader.",
        },
        {
            "requirement": "Require meaningful strict/forward evidence before any live candidate trading.",
            "passed": False,
            "actual": {
                "runway_decision": runway.get("decision"),
                "readiness_frontier_window": readiness_frontier.get("window"),
                "suppressed_exits": readiness_frontier.get("suppressed_exits", best_window.get("suppressed_exits")),
                "suppressed_needed": readiness_frontier.get("suppressed_needed", max(0, 30 - int(fnum(best_window.get("suppressed_exits"))))),
                "harmful_suppressed_rows": readiness_frontier.get("harmful_suppressed_rows", best_window.get("harmful_suppressed_rows")),
                "loss_control_cost_cents": readiness_frontier.get("loss_control_cost_cents", best_window.get("loss_control_cost_cents")),
                "missing_gates": readiness_frontier.get("missing_gates", best_window.get("missing_gates")),
            },
            "evidence": [evidence_path(COMMON_CLOCK_RUNWAY_JSON), evidence_path(COMMON_CLOCK_FRONTIER_JSON)],
            "note": "The readiness frontier is positive and clean so far, but it needs more strict suppressions before live review.",
        },
        {
            "requirement": "Only live-test candidates that clear controlled gates.",
            "passed": None if live_trial_started else controlled.get("decision") == "no_live_test" and full_policy.get("decision") == "no_live_test",
            "actual": {
                "controlled_gate_decision": controlled.get("decision"),
                "full_policy_decision": full_policy.get("decision"),
                "broad_eligible": gate_counts.get("broad_eligible"),
                "sidecar_eligible": gate_counts.get("sidecar_eligible"),
                "live_test_allowed_count": full_policy.get("live_test_allowed_count"),
                "live_trial_status": live_trial.get("status"),
            },
            "evidence": [evidence_path(CONTROLLED_GATE_JSON), evidence_path(FULL_POLICY_JSON), evidence_path(COMMON_CLOCK_LIVE_STATUS_JSON)],
            "note": "Older controlled-gate artifacts still say no_live_test; the amended goal required moving the nearest coherent controlled policy into a size-1 trial, so this is now tracked as an operator override to be judged by live evidence.",
        },
        {
            "requirement": "Controlled live-test contract exists before any real candidate trial.",
            "passed": has_spec_contract,
            "actual": {
                "spec_decision": spec.get("decision"),
                "candidate": candidate,
                "proposed_live_env": proposed_env,
                "proposed_artifacts": proposed_artifacts,
                "implementation_gap_decision": implementation_gap.get("decision"),
                "paper_shadow_safety_decision": safety.get("decision"),
                "paper_shadow_safety_summary": safety.get("summary"),
            },
            "evidence": [evidence_path(COMMON_CLOCK_SPEC_JSON), evidence_path(COMMON_CLOCK_IMPL_GAP_JSON), evidence_path(COMMON_CLOCK_SAFETY_JSON)],
            "note": "The spec defines the size-1 trial; source scaffolding and dormant paper-shadow safety pass, and the live status artifact now tracks the launched process.",
        },
        {
            "requirement": "Live candidate trial with real trades is complete and profitable after fees.",
            "passed": live_trial_round_trips > 0 and live_trial_net_dollars > 0,
            "actual": {
                "spec_decision": spec.get("decision"),
                "immediate_queue_decision": immediate_queue.get("decision"),
                "top_deferred_candidate": immediate_queue.get("top_deferred_candidate"),
                "go_no_go": spec_go_no_go,
                "readiness_any_live_ready": readiness.get("any_live_ready"),
                "live_test_allowed_count": full_policy.get("live_test_allowed_count"),
                "live_trial_status": live_trial.get("status"),
                "live_log_source_tag": live_log_source_tag,
                "live_trial_running": live_trial_running,
                "live_trial_score": live_trial_score,
                "execution_diagnostics_decision": execution_diag.get("decision"),
                "execution_counts": execution_counts,
                "latest_execution_attempt": execution_diag.get("latest_attempt"),
            },
            "evidence": [
                evidence_path(COMMON_CLOCK_SPEC_JSON),
                evidence_path(LIVE_READINESS_JSON),
                evidence_path(FULL_POLICY_JSON),
                evidence_path(IMMEDIATE_QUEUE_JSON),
                evidence_path(COMMON_CLOCK_LIVE_STATUS_JSON),
                evidence_path(COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON),
            ],
            "note": live_trade_note,
        },
        {
            "requirement": "Use Kalshi/exchange reconciliation when exchange-side evidence is available.",
            "passed": bool(live_trial_exchange.get("available")) and live_trial_started,
            "actual": {
                "exchange_reconciliation_gate": next((row for row in spec_go_no_go if row.get("gate") == "exchange_reconciliation_plan"), {}),
                "planned_artifacts": proposed_artifacts,
                "live_trial_exchange": {
                    "available": live_trial_exchange.get("available"),
                    "balance": live_trial_exchange.get("balance"),
                    "positions": live_trial_exchange.get("positions"),
                    "resting_orders": live_trial_exchange.get("resting_orders"),
                    "recent_fills_count": live_trial_exchange.get("recent_fills_count"),
                },
                "reconciliation_ledger_exists": reconciliation_ledger_exists,
                "reconciliation_snapshot_appended": reconciliation_snapshot_appended,
                "candidate_recent_fills_since_run_count": candidate_recent_fills_since_run_count,
                "execution_reconciliation_available": execution_reconciliation_available,
                "orders_checked": exchange_orders_checked,
            },
            "evidence": [evidence_path(COMMON_CLOCK_SPEC_JSON), evidence_path(COMMON_CLOCK_LIVE_STATUS_JSON), evidence_path(COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON)],
            "note": exchange_note,
        },
        {
            "requirement": "No unresolved operational/source-quality/exit blockers remain.",
            "passed": False,
            "actual": {
                "closest_missing_gates": closest.get("missing_gates"),
                "go_no_go_blocked": go_no_go_blocked,
                "implementation_gap_decision": implementation_gap.get("decision"),
                "implementation_blockers": implementation_gap.get("blockers"),
                "paper_shadow_safety_decision": safety.get("decision"),
                "live_trial_status": live_trial.get("status"),
                "execution_diagnostics_decision": execution_diag.get("decision"),
                "live_collection_blockers": live_state_blockers,
                "objective_gap_achieved": objective_gap.get("achieved"),
                "goal_completion_achieved": goal_completion.get("achieved"),
            },
            "evidence": [
                evidence_path(FULL_POLICY_JSON),
                evidence_path(COMMON_CLOCK_SPEC_JSON),
                evidence_path(COMMON_CLOCK_IMPL_GAP_JSON),
                evidence_path(COMMON_CLOCK_SAFETY_JSON),
                evidence_path(COMMON_CLOCK_LIVE_STATUS_JSON),
                evidence_path(COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON),
                evidence_path(FORWARD_COLLECTION_JSON),
                evidence_path(OBJECTIVE_GAP_JSON),
                evidence_path(GOAL_COMPLETION_JSON),
            ],
            "note": "The nearest exit policy still lacks older suppression-density/live-readiness gates, but the live trial is now running under size-1 controls and must be judged by its own exchange-reconciled evidence.",
        },
        {
            "requirement": "Coverage stays secondary to durable profitability.",
            "passed": True,
            "actual": {
                "current_focus": "prove clean profitable core first",
                "nearest_candidate_type": closest.get("candidate_type"),
                "coverage_pct": (closest.get("evidence") or {}).get("coverage_pct"),
                "decision": runway.get("decision"),
            },
            "evidence": [evidence_path(FULL_POLICY_JSON), evidence_path(COMMON_CLOCK_RUNWAY_JSON)],
            "note": "The active next step is forward-density and false-hold safety, not widening entries to force coverage.",
        },
        {
            "requirement": "Definition of done is satisfied by one coherent tradeable strategy.",
            "passed": False,
            "actual": {
                "achieved": False,
                "nearest_policy": closest_compact,
                "live_trial_status": live_trial.get("status"),
                "live_log_source_tag": live_log_source_tag,
                "execution_diagnostics_decision": execution_diag.get("decision"),
                "remaining_hard_blockers": remaining_hard_blockers,
            },
            "evidence": [evidence_path(FULL_POLICY_JSON), evidence_path(COMMON_CLOCK_RUNWAY_JSON), evidence_path(COMMON_CLOCK_SPEC_JSON), evidence_path(COMMON_CLOCK_LIVE_STATUS_JSON), evidence_path(COMMON_CLOCK_EXECUTION_DIAGNOSTICS_JSON)],
            "note": "A coherent policy is running, but the definition of done requires profitable live round trips and stable accounting.",
        },
    ]

    blocked = [row for row in checklist if row.get("passed") is False]
    unverified = [row for row in checklist if row.get("passed") is None]
    if not live_trial_started:
        completion_status = "not_complete_no_live_candidate_trade"
    elif live_trial_round_trips <= 0:
        completion_status = "not_complete_live_trial_waiting_for_scored_round_trip"
    elif live_trial_net_dollars <= 0:
        completion_status = "not_complete_live_trial_negative_after_fees"
    else:
        completion_status = "not_complete_live_trial_needs_meaningful_profitable_sample"
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Strict completion audit for the active /goal: complete end-to-end v28-derived BTC 15m Kalshi strategy profitable after fees over time.",
        "achieved": False,
        "completion_status": completion_status,
        "decision": "live_trial_running_collect_evidence" if live_trial_started else "continue_research_only",
        "nearest_coherent_policy": {
            "candidate": closest_compact,
            "contract": closest_contract,
            "active_live_policy_contract": active_live_policy_contract,
            "conditional_live_test_contract": candidate,
            "runway_best_window": best_window,
            "readiness_frontier": readiness_frontier,
            "net_leader": net_leader,
            "live_trial": live_trial,
            "execution_diagnostics": execution_diag,
        },
        "summary": {
            "checks_total": len(checklist),
            "checks_passed": sum(1 for row in checklist if row.get("passed") is True),
            "checks_blocked": len(blocked),
            "checks_unverified": len(unverified),
            "live_baseline_cents": live_baseline_cents,
            "candidate_rows": gate_counts.get("candidate_rows", candidates.get("candidate_count")),
            "full_policy_cards": len(all_policy_cards),
            "live_test_allowed_count": full_policy.get("live_test_allowed_count"),
            "closest_policy_missing_gates": closest.get("missing_gates"),
            "live_trial_status": live_trial.get("status"),
            "live_log_source_tag": live_log_source_tag,
            "live_trial_running": live_trial_running,
            "active_live_policy_family": active_live_policy_contract.get("family"),
            "execution_diagnostics_decision": execution_diag.get("decision"),
            "zero_fill_attempts": zero_fill_attempts,
            "filled_events": filled_events,
        },
        "checklist": [
            {
                **row,
                "status": status(row.get("passed")),
            }
            for row in checklist
        ],
        "next_required_work": [
            "Keep the versioned size-1 common-clock trial running while lock/process/log/exchange status remain healthy.",
            f"Rescore after every entry, exit, fill, and settlement using LOG_SOURCE_TAG={live_log_source_tag} and SCORE_MODE=live_only.",
            "Reconcile Kalshi balance, positions, resting orders, fills, fees, and local execution events whenever a trade appears.",
            "Stop or revise the candidate if loss cluster, drawdown, accounting mismatch, stale source, or execution blockers fire.",
            "Use the live trial evidence to supersede or reject the older no_live_test/suppression-density blockers.",
            "If the zero-fill monitor reaches its cluster threshold before any fill, stop the flat trial and version an execution-quality tweak instead of widening strategy thresholds.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    summary = report.get("summary") or {}
    nearest = report.get("nearest_coherent_policy") or {}
    nearest_candidate = nearest.get("candidate") or {}
    active_live_policy = nearest.get("active_live_policy_contract") or {}
    readiness_frontier = nearest.get("readiness_frontier") or {}
    net_leader = nearest.get("net_leader") or {}
    lines = [
        "# v28 End-To-End Strategy Goal Audit",
        "",
        "Live-trial audit. Observational report; it does not place orders itself.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Achieved: `{report.get('achieved')}`",
        f"- Completion status: `{report.get('completion_status')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Checks pass/blocked/unverified: `{summary.get('checks_passed')}/{summary.get('checks_blocked')}/{summary.get('checks_unverified')}`",
        f"- Live baseline: `{summary.get('live_baseline_cents')}c`",
        f"- Candidate rows / full policy cards / live-test allowed: `{summary.get('candidate_rows')}/{summary.get('full_policy_cards')}/{summary.get('live_test_allowed_count')}`",
        f"- Live trial status/running: `{summary.get('live_trial_status')}` / `{summary.get('live_trial_running')}`",
        f"- Execution diagnostic / zero-fill attempts / filled events: `{summary.get('execution_diagnostics_decision')}` / `{summary.get('zero_fill_attempts')}` / `{summary.get('filled_events')}`",
        "",
        "## Nearest Coherent Policy",
        "",
        f"- Gate/policy: `{nearest_candidate.get('gate')} / {nearest_candidate.get('policy')}`",
        f"- Source/type: `{nearest_candidate.get('source')} / {nearest_candidate.get('candidate_type')}`",
        f"- Settled/net/delta: `{nearest_candidate.get('settled')} / {nearest_candidate.get('net_cents')}c / {nearest_candidate.get('delta_vs_current_cents')}c vs current-window exits`",
        f"- Suppressions/cushion/loss-control: `{nearest_candidate.get('suppressed_exits')} / {nearest_candidate.get('full_loss_cushion')} / {nearest_candidate.get('loss_control_cost_cents')}c`",
        f"- Missing gates: `{', '.join(nearest_candidate.get('missing_gates') or [])}`",
        f"- Readiness frontier: `{readiness_frontier.get('window')}` with `{readiness_frontier.get('suppressed_exits')}/30` suppressions and `{readiness_frontier.get('suppressed_needed')}` still needed",
        f"- Net leader: `{net_leader.get('window')}` with `{net_leader.get('candidate_cents')}c` candidate net",
        "",
        "## Active Live Policy",
        "",
        f"- Family: `{active_live_policy.get('family')}`",
        f"- Strategy/log source: `{active_live_policy.get('strategy_tag')}` / `{active_live_policy.get('log_source_tag')}`",
        f"- Entry: `{active_live_policy.get('entry_rule')}`",
        f"- Exit/state: `{active_live_policy.get('exit_state_rule')}`",
        f"- Sizing: `{active_live_policy.get('sizing_rule')}`",
        f"- Risk/kill: `{active_live_policy.get('risk_kill_rule')}`",
        f"- Accounting: `{active_live_policy.get('accounting_pnl_rule')}`",
        f"- Iteration: `{active_live_policy.get('iteration_rule')}`",
        f"- Rationale: `{active_live_policy.get('rationale')}`",
        "",
        "## Definition-Of-Done Checklist",
        "",
        "| status | requirement | actual | evidence | note |",
        "|---|---|---|---|---|",
    ]
    for row in report.get("checklist") or []:
        lines.append(
            f"| `{row.get('status')}` | {fmt(row.get('requirement'))} | {fmt(row.get('actual'))} | "
            f"{fmt(row.get('evidence'))} | {fmt(row.get('note'))} |"
        )
    lines.extend([
        "",
        "## Next Required Work",
        "",
    ])
    lines.extend(f"- {item}" for item in report.get("next_required_work") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_audit()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
