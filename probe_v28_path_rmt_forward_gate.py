"""Frozen forward gate for the current best path/RMT v28 challenger.

The candidate was discovered after seeing earlier forward failures, so those
rows are discovery evidence only. This gate starts a fresh freeze timestamp and
scores only clean future BTC 15m markets.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_path_confirmed_entry_candidates import (
    approval_events,
    build_selective_candidate_rows,
    selected_detail,
    summarize,
)
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_path_rmt_forward_gate_state.json"
OUT_JSON = OUT_DIR / "v28_path_rmt_forward_gate_latest.json"
OUT_MD = OUT_DIR / "v28_path_rmt_forward_gate_latest.md"

POLICIES = [
    {
        "policy": "v28_raw_p50_edge0_base",
        "wait_seconds": 0,
        "mode": "baseline",
        "physics": "Fresh same-window baseline: first raw-v28 p>=0.50 nonnegative-edge side per clean market.",
    },
    {
        "policy": "selective_rmt_memory_gap_wait240_rmtedge02_or_opp",
        "wait_seconds": 240,
        "mode": "rmt_memory_gap_confirm_edge02_or_opp",
        "physics": "For fragile early raw-v28 rows, either require same-side RMT/book edge after 240s or follow a later opposite v28 approval.",
    },
    {
        "policy": "selective_rmt_repetition_gap_wait240_rmtedge02_or_opp",
        "wait_seconds": 240,
        "mode": "rmt_repetition_gap_confirm_edge02_or_opp",
        "physics": "Same path rule, using repetition-forgetting probability as the RMT edge check.",
    },
    {
        "policy": "weakraw_rmt_memory_margin02_wait240_or_opp",
        "wait_seconds": 240,
        "mode": "weakraw_rmt_memory_margin02_or_opp",
        "physics": "When raw v28 is below 60%, require at least 2pp RMT/book edge after 240s or follow a later opposite v28 approval.",
    },
    {
        "policy": "weakraw_rmt_repetition_margin02_wait240_or_opp",
        "wait_seconds": 240,
        "mode": "weakraw_rmt_repetition_margin02_or_opp",
        "physics": "Same weak-raw uncertainty gate, using repetition-forgetting probability as the RMT edge check.",
    },
]

MIN_SETTLED = 30
MAX_SIMULATED_SHARE = 0.35
COVERAGE_MIN = 70.0
COVERAGE_MAX = 90.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts"):
            policies = payload.get("policies") if isinstance(payload.get("policies"), list) else []
            existing = {str(item.get("policy") or "") for item in policies if isinstance(item, dict)}
            missing = [item for item in POLICIES if item["policy"] not in existing]
            if missing:
                payload["policies"] = missing + policies
                STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "policies": POLICIES,
        "promotion_floor": {
            "min_settled": MIN_SETTLED,
            "max_simulated_share": MAX_SIMULATED_SHARE,
            "coverage_min": COVERAGE_MIN,
            "coverage_max": COVERAGE_MAX,
        },
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def promotion_blockers(row: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    entries = float(row.get("entries") or 0.0)
    settled = float(row.get("settled") or 0.0)
    simulated = float(row.get("added_reject_count") or 0.0)
    sim_share = simulated / entries if entries else None
    coverage = row.get("coverage_pct")
    net = float(row.get("net_cents_after_entry_fee") or 0.0)
    brier_delta = row.get("brier_delta_mean_plus05_minus_raw")
    logloss_delta = row.get("logloss_delta_mean_plus05_minus_raw")
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if sim_share is None or sim_share > MAX_SIMULATED_SHARE:
        blockers.append("simulated_share_gt_0.35")
    if coverage is None or float(coverage) < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and float(coverage) > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net <= 0.0:
        blockers.append("net_not_positive")
    if brier_delta is None or float(brier_delta) >= 0.0:
        blockers.append("brier_delta_not_negative")
    if logloss_delta is None or float(logloss_delta) >= 0.0:
        blockers.append("logloss_delta_not_negative")
    return blockers


def candidate_runway(row: dict[str, Any]) -> dict[str, Any]:
    entries = int(float(row.get("entries") or 0.0))
    settled = int(float(row.get("settled") or 0.0))
    simulated = int(float(row.get("added_reject_count") or 0.0))
    future_actual_needed = 0
    while True:
        total = entries + future_actual_needed
        sim_share = simulated / total if total else 1.0
        if sim_share <= MAX_SIMULATED_SHARE:
            break
        future_actual_needed += 1
    return {
        "settled_rows_to_min_30": max(0, MIN_SETTLED - settled),
        "actual_entries_needed_for_simulated_share_lte_35pct": future_actual_needed,
    }


def gate_runway(forward_denominator: int) -> dict[str, Any]:
    return {
        "future_clean_markets_to_denominator_30": max(0, MIN_SETTLED - forward_denominator),
        "future_clean_markets_to_denominator_10": max(0, 10 - forward_denominator),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state.get("freeze_ts"))
    observations = enrich_state(attach_regime_rows(observation_pool()))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    base_rows = [
        row for row in selected_rows(observations, "v28_raw", p_raw, 0.50, 0.00)
        if str(row.get("market") or "") in forward_markets
    ]
    summaries: list[dict[str, Any]] = []
    approvals = approval_events()
    for item in state.get("policies") or POLICIES:
        if item.get("mode") == "baseline":
            rows = [selected_detail(row, str(item["policy"]), row) for row in base_rows]
            blocked = []
        else:
            rows, blocked = build_selective_candidate_rows(
                base_rows,
                observations,
                approvals,
                str(item["policy"]),
                int(item["wait_seconds"]),
                str(item["mode"]),
            )
        summary = summarize(str(item["policy"]), rows, blocked, len(forward_markets))
        blockers = promotion_blockers(summary)
        summary["promotion_blockers"] = blockers
        summary["promotable"] = not blockers
        summary["runway"] = candidate_runway(summary)
        summaries.append(summary)
    baseline = next((row for row in summaries if row.get("policy") == "v28_raw_p50_edge0_base"), {})
    for summary in summaries:
        summary["vs_baseline"] = comparison_vs_baseline(summary, baseline)
    return {
        "freeze_ts": state.get("freeze_ts"),
        "policies": state.get("policies") or POLICIES,
        "forward_market_denominator": len(forward_markets),
        "forward_markets": sorted(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "post_freeze_observed_markets": sorted(timing["post_freeze_observed_markets"]),
        "base_entries": len(base_rows),
        "base_markets": [str(row.get("market") or "") for row in base_rows],
        "summaries": summaries,
        "runway": gate_runway(len(forward_markets)),
        "any_promotable": any(row.get("promotable") for row in summaries),
    }


def comparison_vs_baseline(row: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    if not baseline or row.get("policy") == baseline.get("policy"):
        return {
            "net_cents_delta": 0.0 if baseline else None,
            "brier_delta": 0.0 if baseline else None,
            "entries_delta": 0 if baseline else None,
            "coverage_delta": 0.0 if baseline else None,
        }
    net = row.get("net_cents_after_entry_fee")
    base_net = baseline.get("net_cents_after_entry_fee")
    brier = row.get("avg_brier")
    base_brier = baseline.get("avg_brier")
    coverage = row.get("coverage_pct")
    base_coverage = baseline.get("coverage_pct")
    return {
        "net_cents_delta": None if net is None or base_net is None else float(net) - float(base_net),
        "brier_delta": None if brier is None or base_brier is None else float(brier) - float(base_brier),
        "entries_delta": int(row.get("entries") or 0) - int(baseline.get("entries") or 0),
        "coverage_delta": None if coverage is None or base_coverage is None else float(coverage) - float(base_coverage),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Path/RMT Fresh Forward Gate",
        "",
        "Fresh freeze for the current best path/RMT challenger. Discovery rows before this timestamp do not count.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Forward denominator/base entries: `{report.get('forward_market_denominator')}/{report.get('base_entries')}`",
        f"- Excluded in-progress post-freeze markets: `{len(report.get('excluded_in_progress_markets') or [])}`",
        f"- Any promotable: `{report.get('any_promotable')}`",
        f"- Future clean markets needed for denominator 10: `{(report.get('runway') or {}).get('future_clean_markets_to_denominator_10')}`",
        f"- Future clean markets needed for denominator 30: `{(report.get('runway') or {}).get('future_clean_markets_to_denominator_30')}`",
        "",
        "## Policies",
        "",
    ]
    for item in report.get("policies") or []:
        lines.append(f"- `{item.get('policy')}`: {item.get('physics')}")
    lines.extend([
        "",
        "## Forward Scorecard",
        "",
        "| policy | entries | settled | W/L | actual/sim | sim share | coverage | net c | brier | net vs base | brier vs base | promotable | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("summaries") or []:
        vs_base = row.get("vs_baseline") or {}
        lines.append(
            f"| {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{row.get('approved_entry_count')}/{row.get('added_reject_count')} | {fmt(row.get('simulated_share'))} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents_after_entry_fee'))} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(vs_base.get('net_cents_delta'))} | {fmt(vs_base.get('brier_delta'))} | "
            f"{row.get('promotable')} | {', '.join(row.get('promotion_blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Candidate Runway",
        "",
        "| policy | settled rows to 30 | actual entries needed for sim share <=35% |",
        "|---|---:|---:|",
    ])
    for row in report.get("summaries") or []:
        runway = row.get("runway") or {}
        lines.append(
            f"| {row.get('policy')} | {runway.get('settled_rows_to_min_30')} | "
            f"{runway.get('actual_entries_needed_for_simulated_share_lte_35pct')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
