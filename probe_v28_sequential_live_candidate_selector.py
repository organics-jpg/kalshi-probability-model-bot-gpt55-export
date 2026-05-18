"""Sequential selector for v28-derived live-test candidates.

This is an operator-facing ledger, not a discovery probe. It ranks existing
candidate artifacts by PnL/win-rate first, then records whether each leading
family is launchable, rejected, deferred, or already in controlled live trial.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_sequential_live_candidate_selector_latest.json"
OUT_MD = OUT_DIR / "v28_sequential_live_candidate_selector_latest.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def fnum(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def win_rate(row: dict[str, Any]) -> float:
    wins = fnum(row.get("wins"))
    losses = fnum(row.get("losses"))
    if wins is not None and losses is not None and wins + losses > 0:
        return wins / (wins + losses)
    wl = row.get("wins_losses") or row.get("W/L")
    if isinstance(wl, str) and "/" in wl:
        left, right = wl.split("/", 1)
        w = fnum(left.strip())
        l = fnum(right.strip())
        if w is not None and l is not None and w + l > 0:
            return w / (w + l)
    return -1.0


def net_cents(row: dict[str, Any]) -> float:
    for key in ("net_cents_after_entry_fee", "net_cents", "gross_cents"):
        value = fnum(row.get(key))
        if value is not None:
            return value
    return float("-inf")


def settled(row: dict[str, Any]) -> int:
    value = fnum(row.get("settled"))
    return int(value or 0)


def compact_row(row: dict[str, Any], rank: int | None = None) -> dict[str, Any]:
    out = {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "settled": settled(row),
        "net_cents": net_cents(row),
        "win_rate": win_rate(row),
        "coverage_pct": row.get("coverage_pct"),
        "simulated_or_reconstructed_share": row.get("simulated_share", row.get("reconstructed_share")),
        "live_ready": row.get("live_ready"),
        "blockers": row.get("blockers") or row.get("missing_gates") or [],
    }
    if rank is not None:
        out = {"rank": rank, **out}
    return out


def first_matching(rows: list[dict[str, Any]], gate: str, policy_contains: str | None = None) -> dict[str, Any] | None:
    for row in rows:
        if row.get("gate") != gate:
            continue
        if policy_contains and policy_contains not in str(row.get("policy")):
            continue
        return row
    return None


def current_live_trial() -> dict[str, Any]:
    status_md = load_text(OUT_DIR / "v28_common_clock_live_trial_status_latest.md")
    status_json = load_json(OUT_DIR / "v28_common_clock_live_trial_status_latest.json", {})
    diag_md = load_text(OUT_DIR / "v28_common_clock_live_execution_diagnostics_latest.md")
    near_md = load_text(OUT_DIR / "v28_common_clock_live_near_miss_latest.md")
    zero_entry = load_json(OUT_DIR / "v28_common_clock_zero_entry_blocker_latest.json", {})
    strategy_tag = (
        status_json.get("strategy_tag")
        or "mushroom_v28_common_clock_exit_guard_v1_sourcefix_size1_live"
    )
    log_source_tag = (
        status_json.get("log_source_tag")
        or "live_mushroom_v28_common_clock_exit_guard_sourcefix_size1"
    )
    score = load_json(
        ROOT
        / "stats"
        / str(strategy_tag)
        / "summary.json",
        {},
    )
    return {
        "strategy_tag": strategy_tag,
        "log_source_tag": log_source_tag,
        "decision": "continue_active_controlled_trial",
        "status_excerpt": [line for line in status_md.splitlines() if line.startswith("- Status:") or line.startswith("- Lock/process:") or line.startswith("- Latest event:")][:6],
        "diagnostic_excerpt": [line for line in diag_md.splitlines() if "Approved/order" in line or "Zero-fill" in line][:4],
        "near_miss_excerpt": [line for line in near_md.splitlines() if "Latest-market decision" in line or "Events/rejected" in line or "Latest-market source stale" in line or "Max p_side" in line][:6],
        "zero_entry_decision": zero_entry.get("decision"),
        "zero_entry_totals": zero_entry.get("totals"),
        "zero_entry_decision_counts": zero_entry.get("decision_counts"),
        "zero_entry_no_entry_review_due": zero_entry.get("no_entry_review_due"),
        "zero_entry_markets_until_review": zero_entry.get("markets_until_no_entry_review"),
        "score": {
            "entries_total": score.get("entries_total"),
            "completed_round_trips": score.get("completed_round_trips"),
            "net_pnl_total_dollars": score.get("net_pnl_total_dollars"),
            "open_positions": score.get("open_positions"),
        },
        "operator_rule": "Do not switch while this flat, healthy size-1 trial is collecting unless a higher-ranked candidate becomes launchable or the active trial hits a kill rule.",
    }


def build_report() -> dict[str, Any]:
    tracker = load_json(OUT_DIR / "v28_candidate_pnl_tracker_latest.json", {})
    rows = [row for row in tracker.get("rows", []) if isinstance(row, dict) and fnum(row.get("net_cents_after_entry_fee")) is not None]
    ranked = sorted(rows, key=lambda row: (net_cents(row), win_rate(row), settled(row)), reverse=True)

    top_component_runway = load_json(OUT_DIR / "v28_top_observable_stack_runway_latest.json", {})
    top_component_gate = load_json(OUT_DIR / "v28_top_component_strict_gate_audit_latest.json", {})
    top_component_autopsy = load_json(OUT_DIR / "v28_top_component_strict_row_autopsy_latest.json", {})
    dual_lane = load_text(OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.md")
    sidecar_watch = load_json(OUT_DIR / "v28_sidecar_live_test_watch_latest.json", {})
    full_policy = load_json(OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json", {})
    live_readiness = load_json(OUT_DIR / "v28_live_trade_readiness_latest.json", {})
    book_blend_md = load_text(OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_latest.md")
    active_live = current_live_trial()
    active_score = active_live.get("score") or {}
    active_entries = int(fnum(active_score.get("entries_total")) or 0)
    active_round_trips = int(fnum(active_score.get("completed_round_trips")) or 0)
    active_net = fnum(active_score.get("net_pnl_total_dollars")) or 0.0

    top_parent = first_matching(ranked, "top_component_parent_fill_repair_child")
    dual = first_matching(ranked, "dual_lane_overlap_union")
    book_raw = first_matching(ranked, "approved_entry_book_raw_blend_fv", "book_raw_blend_alpha_0p50")
    if book_raw is None:
        for row in sidecar_watch.get("closest_positive", []):
            if row.get("gate") == "approved_entry_book_raw_blend_fv":
                book_raw = row
                break

    closest_sidecar = (sidecar_watch.get("closest_positive") or [{}])[0]
    closest_full_policy = (full_policy.get("all_policy_cards") or [{}])[0]

    families: list[dict[str, Any]] = []
    if top_parent:
        strict = top_component_runway.get("strict", {})
        families.append({
            "family": "top_component_parent_fill_repair_child",
            "rank_basis": compact_row(top_parent, 1),
            "decision": "reject_immediate_live_test",
            "why": [
                "raw PnL/win-rate leader is diagnostic/prefreeze, not strict-forward",
                "strict post-birth row does not beat refreshed live baseline",
                "exit-clock rescue mechanism is not forward-proven in this branch",
                "strict losses point to source-quality and FV/entry false positives",
            ],
            "minimum_blocker_to_clear": {
                "strict_rows_needed_for_30": strict.get("rows_needed_for_30"),
                "net_cents_needed_for_cushion3": strict.get("net_cents_needed_for_cushion3"),
                "net_cents_needed_to_beat_live": strict.get("net_cents_needed_to_beat_live"),
                "promotion_gate_pass_count": top_component_gate.get("promotion_gate_pass_count"),
                "strict_unique_rows": top_component_autopsy.get("strict_unique_rows"),
                "strict_net_cents": top_component_autopsy.get("strict_net_cents"),
            },
        })

    if dual:
        families.append({
            "family": "dual_lane_overlap_union",
            "rank_basis": compact_row(dual),
            "decision": "reject_immediate_live_test",
            "why": [
                "fresh dual-lane handoff decision is no_live_test",
                "same-window strict candidate trails live v28",
                "own-freeze/overlay/parent-shrink gates are still immature",
            ],
            "minimum_blocker_to_clear": {
                "handoff_decision_excerpt": [line for line in dual_lane.splitlines() if "Decision:" in line or "Candidate minus live" in line or "Blocked Checks" in line][:8],
                "required": "needs own-freeze strict sample, positive same-window live edge, and overlay/parent-shrink forward samples",
            },
        })

    if book_raw:
        families.append({
            "family": "approved_entry_book_raw_blend_fv",
            "rank_basis": compact_row(book_raw),
            "decision": "defer_as_calibration_overlay_not_entry_policy",
            "why": [
                "frozen report keeps entry selection fixed and changes only FV probability calibration",
                "sidecar watch marks it not ready because source is unknown and it does not beat the refreshed live baseline",
                "using the blend as a live entry gate would be a code/logic conversion not directly validated by its current PnL row",
            ],
            "minimum_blocker_to_clear": {
                "live_readiness_any_live_ready": live_readiness.get("any_live_ready"),
                "book_blend_live_ready_line": next((line for line in book_blend_md.splitlines() if "Candidate live ready" in line), None),
                "operator_requirement": "define and score a versioned full policy using the blend for sizing/exit/FV, or pre-register a code-level entry conversion before any switch",
            },
        })

    active_why = [
        "it is already the only live controlled v28-derived candidate process",
    ]
    if active_round_trips > 0:
        active_why.append(
            f"it has {active_entries} scored entry and {active_round_trips} scored round trip; current net after fees is ${active_net:.2f}"
        )
    elif active_entries > 0:
        active_why.append("it has a scored candidate entry but no completed scored round trip yet")
    else:
        active_why.append("it has not produced a scored filled candidate entry yet")
    active_why.extend([
        "exchange status is flat with no resting orders",
        "sourcefix repaired BTC websocket staleness without opening exposure",
        "the trial is not profitable evidence yet, but it has not hit a kill rule",
    ])
    if active_round_trips > 0 and active_net <= 0:
        active_needed = "recover from negative exchange-reconciled live PnL and build a meaningful positive after-fee sample"
    else:
        active_needed = "completed round trips, exchange-reconciled fees/PnL, and positive live-only score over a meaningful sample"
    active_family = "active_common_clock_exit_guard_sourcefix_size1"
    active_policy = "loss_guard_value_p85_reduce_p79_gap0 + sourcefix BTC websocket stale reconnect"
    if "hybridfpt" in str(active_live.get("strategy_tag")):
        active_family = "active_sourcefix_hybrid_fpt_depth_size1"
        active_policy = (
            "hybrid_fpt_depth_gate + sourcefix BTC websocket stale reconnect + "
            "common-clock exit guard"
        )
        if "btcrotate" in str(active_live.get("strategy_tag")):
            active_family = "active_sourcefix_hybrid_fpt_btcrotate_size1"
            active_policy = (
                "hybrid_fpt_depth_gate + BTC websocket fallback rotation + "
                "common-clock exit guard"
            )
        if (
            "ask35" in str(active_live.get("strategy_tag"))
            and "btcrest" in str(active_live.get("strategy_tag"))
            and "exitdelay90" in str(active_live.get("strategy_tag"))
        ):
            active_family = "active_sourcefix_hybrid_fpt_ask35_btcrest_exitdelay90_size1"
            active_policy = (
                "hybrid_fpt_depth_gate raw03_recross60_abs85_ask35 + "
                "Coinbase REST BTC freshness fallback + 90s post-fill v28 exit delay + "
                "common-clock exit guard"
            )
        elif "ask35" in str(active_live.get("strategy_tag")) and "btcrest" in str(active_live.get("strategy_tag")):
            active_family = "active_sourcefix_hybrid_fpt_ask35_btcrest_size1"
            active_policy = (
                "hybrid_fpt_depth_gate raw03_recross60_abs85_ask35 + "
                "Coinbase REST BTC freshness fallback + common-clock exit guard"
            )
        elif "btcrest" in str(active_live.get("strategy_tag")):
            active_family = "active_sourcefix_hybrid_fpt_btcrest_size1"
            active_policy = (
                "hybrid_fpt_depth_gate + Coinbase REST BTC freshness fallback + "
                "common-clock exit guard"
            )
        if "ask35" in str(active_live.get("strategy_tag")):
            active_why.append(
                "this version maps back to the existing raw03_recross60_abs85_ask35 forward frontier after coverage review showed the extra abs-d ceiling reduced row count"
            )
        else:
            active_why.append(
                "this is the versioned v2 iteration: the previous sourcefix live loss had abs_d_sigma=1.140512, and this existing gate caps abs_d_sigma at 1.10"
            )
        if "btcrotate" in str(active_live.get("strategy_tag")):
            active_why.append(
                "this is the versioned source-quality iteration after the hybrid-FPT trial lost twice and showed Coinbase stale-reconnect coverage drag"
            )
        if (
            "ask35" in str(active_live.get("strategy_tag"))
            and "btcrest" in str(active_live.get("strategy_tag"))
            and "exitdelay90" in str(active_live.get("strategy_tag"))
        ):
            active_why.append(
                "this is the versioned exit-state repair after live evidence showed a 34s probability-collapse exit sold at 42c before the market recovered and finalized YES"
            )
        elif "ask35" in str(active_live.get("strategy_tag")) and "btcrest" in str(active_live.get("strategy_tag")):
            active_why.append(
                "this is the versioned coverage-preserving source-quality iteration: ask>=35c avoids cheap-tail noise while Coinbase REST refreshes quiet websocket ticks"
            )
        elif "btcrest" in str(active_live.get("strategy_tag")):
            active_why.append(
                "this is the versioned source-quality iteration that keeps the strict BTC max-age gate but refreshes quiet websocket ticks through Coinbase REST"
            )

    families.append({
        "family": active_family,
        "rank_basis": {
            "gate": "hybrid_fpt_depth_gate" if "hybridfpt" in str(active_live.get("strategy_tag")) else "common_clock_strict_forward_v3",
            "policy": active_policy,
        },
        "decision": "continue_active_controlled_trial",
        "why": active_why,
        "minimum_blocker_to_clear": {
            "needed": active_needed,
            "do_not_change": "do not lower p floors or widen thresholds solely to create coverage",
        },
    })

    active_status = str(active_live.get("status") or "")
    active_running = bool(active_live.get("process_running")) and bool(active_live.get("lock_matches"))
    if "hybridfpt" in str(active_live.get("strategy_tag")):
        decision = "continue_active_hybridfpt_btcrotate_trial_no_switch" if "btcrotate" in str(active_live.get("strategy_tag")) else "continue_active_hybridfpt_trial_no_switch"
        if (
            "ask35" in str(active_live.get("strategy_tag"))
            and "btcrest" in str(active_live.get("strategy_tag"))
            and "exitdelay90" in str(active_live.get("strategy_tag"))
        ):
            decision = "continue_active_hybridfpt_ask35_btcrest_exitdelay90_trial_no_switch"
        elif "ask35" in str(active_live.get("strategy_tag")) and "btcrest" in str(active_live.get("strategy_tag")):
            decision = "continue_active_hybridfpt_ask35_btcrest_trial_no_switch"
        elif "btcrest" in str(active_live.get("strategy_tag")):
            decision = "continue_active_hybridfpt_btcrest_trial_no_switch"
        next_action = (
            "Keep the versioned hybrid-FPT sourcefix size-1 trial running under kill rules. "
            "It is the active live iteration after the sourcefix v1 losing round trip; the exact next blocker is first filled hybrid-FPT evidence."
        )
        if "btcrotate" in str(active_live.get("strategy_tag")):
            next_action = (
                "Keep the versioned hybrid-FPT BTC-rotation size-1 trial running under kill rules. "
                "Judge it by live source freshness, fills, exit execution, and after-fee PnL before changing entry thresholds."
            )
        if (
            "ask35" in str(active_live.get("strategy_tag"))
            and "btcrest" in str(active_live.get("strategy_tag"))
            and "exitdelay90" in str(active_live.get("strategy_tag"))
        ):
            next_action = (
                "Keep the versioned hybrid-FPT ask35 BTC-REST exitdelay90 size-1 trial running under kill rules. "
                "Judge whether the 90s post-fill exit delay repairs early false collapse exits without creating larger held losses."
            )
        elif "ask35" in str(active_live.get("strategy_tag")) and "btcrest" in str(active_live.get("strategy_tag")):
            next_action = (
                "Keep the versioned hybrid-FPT ask35 BTC-REST size-1 trial running under kill rules. "
                "Judge it by live source freshness, fills, exit execution, and after-fee PnL before changing entry thresholds."
            )
        elif "btcrest" in str(active_live.get("strategy_tag")):
            next_action = (
                "Keep the versioned hybrid-FPT BTC-REST size-1 trial running under kill rules. "
                "Judge it by live source freshness, fills, exit execution, and after-fee PnL before changing entry thresholds."
            )
        if not active_running:
            score = active_live.get("score") or {}
            net = float(score.get("net_pnl_total_dollars", 0.0) or 0.0)
            decision = "active_hybridfpt_trial_stopped_needs_next_candidate"
            next_action = (
                "Do not relaunch the stopped hybrid-FPT ask35 BTC-REST lane without a new blocker-specific version. "
                f"The stopped trial status is {active_status} with net ${net:.2f}; select the next existing v28-derived candidate or a formally versioned repair."
            )
            active_why.append(
                f"this trial is stopped rather than actively collecting; status={active_status}, running={active_running}"
            )
    else:
        decision = "continue_active_sourcefix_trial_no_switch"
        next_action = (
            "Keep the sourcefix size-1 trial running under kill rules. "
            "Top PnL families are rejected/deferred for immediate launch; the exact next launch blocker is live evidence, not another broad candidate."
        )
    if full_policy.get("live_test_allowed_count"):
        decision = "review_new_live_test_allowed_candidate"
        next_action = "A full-policy card now allows live test; verify exchange-flat and switch only after explicit operator review."

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "purpose": "Sequential operator selector for existing v28 candidates; no orders or live logic changes.",
        "candidate_rows_ranked": len(ranked),
        "top_ranked_rows": [compact_row(row, idx) for idx, row in enumerate(ranked[:20], start=1)],
        "live_baseline_cents": full_policy.get("live_baseline_cents") or top_component_gate.get("live_net_cents"),
        "full_policy_live_test_allowed_count": full_policy.get("live_test_allowed_count"),
        "sidecar_ready_count": len(sidecar_watch.get("ready") or []),
        "readiness_any_live_ready": live_readiness.get("any_live_ready"),
        "families": families,
        "active_live_trial": active_live,
        "decision": decision,
        "next_action": next_action,
        "sources": {
            "tracker": str(OUT_DIR / "v28_candidate_pnl_tracker_latest.json"),
            "full_policy": str(OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"),
            "top_component_runway": str(OUT_DIR / "v28_top_observable_stack_runway_latest.json"),
            "top_component_gate": str(OUT_DIR / "v28_top_component_strict_gate_audit_latest.json"),
            "top_component_autopsy": str(OUT_DIR / "v28_top_component_strict_row_autopsy_latest.json"),
            "dual_lane_handoff": str(OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.md"),
            "sidecar_watch": str(OUT_DIR / "v28_sidecar_live_test_watch_latest.json"),
            "live_status": str(OUT_DIR / "v28_common_clock_live_trial_status_latest.md"),
            "live_diagnostics": str(OUT_DIR / "v28_common_clock_live_execution_diagnostics_latest.md"),
        },
    }


def fmt_cents(value: Any) -> str:
    num = fnum(value)
    if num is None:
        return "n/a"
    return f"{num:.1f}c"


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Sequential Live Candidate Selector",
        "",
        "Operator-facing selector. It does not place orders or change live logic.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate rows ranked: `{report['candidate_rows_ranked']}`",
        f"- Live baseline: `{fmt_cents(report.get('live_baseline_cents'))}`",
        f"- Full-policy live-test allowed count: `{report.get('full_policy_live_test_allowed_count')}`",
        f"- Sidecar ready count: `{report.get('sidecar_ready_count')}`",
        f"- Readiness any_live_ready: `{report.get('readiness_any_live_ready')}`",
        "",
        "## Family Decisions",
        "",
    ]
    for family in report["families"]:
        rank = family.get("rank_basis", {})
        lines.extend([
            f"### {family['family']}",
            "",
            f"- Decision: `{family['decision']}`",
            f"- Gate/policy: `{rank.get('gate')}` / `{rank.get('policy')}`",
            f"- Settled/net/win-rate: `{rank.get('settled')}` / `{fmt_cents(rank.get('net_cents'))}` / `{rank.get('win_rate')}`",
            f"- Blockers: `{', '.join(str(x) for x in rank.get('blockers') or []) or 'none'}`",
            "",
            "Why:",
        ])
        lines.extend(f"- {item}" for item in family.get("why", []))
        lines.extend(["", "Minimum blocker to clear:", ""])
        blocker = family.get("minimum_blocker_to_clear", {})
        for key, value in blocker.items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append("")
    live = report["active_live_trial"]
    lines.extend([
        "## Active Live Trial",
        "",
        f"- Strategy: `{live['strategy_tag']}`",
        f"- Log source: `{live['log_source_tag']}`",
        f"- Decision: `{live['decision']}`",
        f"- Score: `{live['score']}`",
        f"- Zero-entry decision: `{live.get('zero_entry_decision')}`",
        f"- Zero-entry totals: `{live.get('zero_entry_totals')}`",
        f"- Zero-entry decision counts: `{live.get('zero_entry_decision_counts')}`",
        f"- No-entry review due / markets until review: `{live.get('zero_entry_no_entry_review_due')}` / `{live.get('zero_entry_markets_until_review')}`",
        f"- Operator rule: {live['operator_rule']}",
        "",
        "Status excerpts:",
    ])
    for line in live.get("status_excerpt", []) + live.get("diagnostic_excerpt", []) + live.get("near_miss_excerpt", []):
        lines.append(f"- {line}")
    lines.extend(["", "## Next Action", "", report["next_action"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
