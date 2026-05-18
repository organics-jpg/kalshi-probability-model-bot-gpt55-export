"""Frozen Goldilocks-edge repair candidate for v28 target coverage.

Research-only; no live bot changes or orders.

Physics hypothesis:
    In noisy BTC boundary markets, raw FV edge is not monotonic. A small paid
    edge can mean book/model agreement, while a large apparent edge near a
    high-recross boundary can mean stale geometry or model overconfidence. This
    candidate rejects false-conviction edge phases and repairs coverage with
    cleaner rows that preserve the 75% participation floor.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    is_clean_repair,
    raw_edge,
    row_net_after_fee,
    summarize,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_goldilocks_edge_repair_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_goldilocks_edge_repair_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_goldilocks_edge_repair_entry_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MIN_SETTLED = 30


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "base_policy": POLICY,
        "candidate": "skip_false_edge_phase_repair_goldilocks",
        "coverage_floor": COVERAGE_FLOOR,
        "danger_rule": "early/boundary false-conviction edge phases: edge<2pp OR edge 4-8pp OR edge>=14pp when recross geometry is high-risk",
        "repair_rule": "clean repair rows ranked by Goldilocks edge distance, low recross, and far boundary",
        "physics": "When BTC is near strike with high recross hazard, apparent FV edge can measure model disagreement more than true edge; book/model agreement around a modest 2-4pp paid edge may be the more stable signal.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "").lower()


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def abs_d(row: dict[str, Any]) -> float | None:
    return as_float(row.get("abs_d_sigma"))


def stc(row: dict[str, Any]) -> float | None:
    return as_float(row.get("seconds_to_close"))


def high_risk_geometry(row: dict[str, Any]) -> bool:
    r = recross(row)
    d = abs_d(row)
    t = stc(row)
    if r is None or d is None or t is None:
        return False
    return t >= 660 and d <= 0.45 and r >= 0.55


def edge_bucket(row: dict[str, Any]) -> str:
    edge = raw_edge(row)
    if edge is None:
        return "edge_missing"
    if edge < 0.02:
        return "edge_lt_2pp"
    if edge < 0.04:
        return "edge_2_4pp"
    if edge < 0.08:
        return "edge_4_8pp"
    if edge < 0.14:
        return "edge_8_14pp"
    return "edge_ge_14pp"


def is_false_edge_phase(row: dict[str, Any]) -> bool:
    bucket = edge_bucket(row)
    if not high_risk_geometry(row):
        return False
    if bucket in {"edge_lt_2pp", "edge_ge_14pp"}:
        return True
    if bucket == "edge_4_8pp":
        return True
    return side(row) == "no" and bucket == "edge_8_14pp"


def danger_reasons(row: dict[str, Any]) -> list[str]:
    reasons = []
    if high_risk_geometry(row):
        reasons.append("early_boundary_high_recross")
    if is_false_edge_phase(row):
        reasons.append(f"false_edge_phase_{edge_bucket(row)}")
    if side(row) == "no":
        reasons.append("side_no")
    return reasons


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def goldilocks_distance(row: dict[str, Any]) -> float:
    edge = raw_edge(row)
    if edge is None:
        return 999.0
    return abs(edge - 0.03)


def recross_score(row: dict[str, Any]) -> float:
    value = recross(row)
    return value if value is not None else 999.0


def boundary_distance_score(row: dict[str, Any]) -> float:
    value = abs_d(row)
    return -(value if value is not None else 0.0)


def clean_rows_by_market(rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_clean_repair(row):
            continue
        candidates.append({
            **row,
            "raw_edge_prob": raw_edge(row),
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "repair_score": -goldilocks_distance(row) - recross_score(row) / 10.0,
        })
    candidates.sort(
        key=lambda row: (
            goldilocks_distance(row),
            recross_score(row),
            boundary_distance_score(row),
            str(row.get("ts_wall") or ""),
        )
    )
    out = []
    seen = set()
    for row in candidates:
        market = str(row.get("market") or "")
        if market in seen:
            continue
        out.append(row)
        seen.add(market)
    return out


def rows_for_freeze(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def diagnostic_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_ts = target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts")
    return rows_for_freeze(str(freeze_ts))


def build_candidate(all_rows: list[dict[str, Any]], target: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if is_false_edge_phase(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed = clean_rows_by_market(all_rows, all_markets - target_markets)
    chosen = missed[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        kept_markets = {str(row.get("market") or "") for row in kept}
        extras = clean_rows_by_market(all_rows, all_markets - kept_markets - chosen_markets)
        for row in extras:
            if len(chosen) >= needed:
                break
            market = str(row.get("market") or "")
            if market in chosen_markets:
                continue
            chosen.append(row)
            chosen_markets.add(market)
    return {
        "danger": danger,
        "kept": kept,
        "repairs": chosen,
        "candidate": kept + chosen,
        "needed_repairs": needed,
        "missed_repairs_available": len(missed),
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "edge_bucket": edge_bucket(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "seconds_to_close": row.get("seconds_to_close"),
        "danger_reasons": danger_reasons(row),
        "repair_score": row.get("repair_score"),
    }


def scenario_summary(label: str, all_rows: list[dict[str, Any]], target: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    built = build_candidate(all_rows, target, denominator)
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(built["candidate"], denominator)
    blockers = []
    if int(candidate_summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if candidate_summary.get("coverage_pct") is None or float(candidate_summary["coverage_pct"]) < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if float(candidate_summary.get("net_cents") or 0.0) <= 0.0:
        blockers.append("net_not_positive")
    return {
        "label": label,
        "future_denominator": denominator,
        "target_summary": target_summary,
        "danger_summary": summarize(built["danger"], denominator),
        "kept_summary": summarize(built["kept"], denominator),
        "repair_summary": summarize(built["repairs"], denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "needed_repairs": built["needed_repairs"],
        "missed_repairs_available": built["missed_repairs_available"],
        "danger_rows": [compact(row) for row in built["danger"]],
        "repair_rows": [compact(row) for row in built["repairs"]],
        "candidate_live_ready": not blockers,
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    diag_all, diag_target, diag_denominator = diagnostic_rows()
    future_all, future_target, future_denominator = rows_for_freeze(str(state["freeze_ts_utc"]))
    diagnostic = scenario_summary("diagnostic_existing_forward", diag_all, diag_target, diag_denominator)
    future = scenario_summary("frozen_future", future_all, future_target, future_denominator)
    return {
        "freeze": state,
        "diagnostic": diagnostic,
        "frozen_future": future,
        "candidate_live_ready": future["candidate_live_ready"],
        "blockers": future["blockers"],
        "interpretation": interpretation(diagnostic, future),
    }


def interpretation(diagnostic: dict[str, Any], future: dict[str, Any]) -> list[str]:
    diag_candidate = diagnostic.get("candidate_summary") or {}
    diag_target = diagnostic.get("target_summary") or {}
    fut_candidate = future.get("candidate_summary") or {}
    return [
        f"Diagnostic candidate has {diag_candidate.get('entries')} entries, {diag_candidate.get('settled')} settled, coverage {diag_candidate.get('coverage_pct')}, net {diag_candidate.get('net_cents')}c versus target {diag_target.get('net_cents')}c.",
        f"Diagnostic delta versus target is {diagnostic.get('delta_vs_target_cents')}c; danger rows removed {len(diagnostic.get('danger_rows') or [])}, repair rows added {len(diagnostic.get('repair_rows') or [])}.",
        f"Frozen future candidate has {fut_candidate.get('entries')} entries and {fut_candidate.get('settled')} settled rows since its own freeze.",
        f"Frozen future blockers: {', '.join(future.get('blockers') or []) or 'none'}.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    diagnostic = report.get("diagnostic") or {}
    future = report.get("frozen_future") or {}
    lines = [
        "# v28 Frozen Goldilocks Edge Repair Entry",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Policy: `{freeze.get('base_policy')}`",
        f"- Live ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Scenarios", ""])
    for scenario in [diagnostic, future]:
        target = scenario.get("target_summary") or {}
        danger = scenario.get("danger_summary") or {}
        repairs = scenario.get("repair_summary") or {}
        candidate = scenario.get("candidate_summary") or {}
        lines.extend([
            f"### {scenario.get('label')}",
            "",
            f"- Denominator: `{scenario.get('future_denominator')}`",
            f"- Target entries/settled/coverage/net: `{target.get('entries')}/{target.get('settled')}/{fmt(target.get('coverage_pct'))}/{fmt(target.get('net_cents'))}c`",
            f"- Danger entries/settled/net: `{danger.get('entries')}/{danger.get('settled')}/{fmt(danger.get('net_cents'))}c`",
            f"- Repair entries/settled/net: `{repairs.get('entries')}/{repairs.get('settled')}/{fmt(repairs.get('net_cents'))}c`",
            f"- Candidate entries/settled/coverage/net: `{candidate.get('entries')}/{candidate.get('settled')}/{fmt(candidate.get('coverage_pct'))}/{fmt(candidate.get('net_cents'))}c`",
            f"- Delta vs target: `{fmt(scenario.get('delta_vs_target_cents'))}c`",
            f"- Needed repairs: `{scenario.get('needed_repairs')}`",
            f"- Blockers: `{', '.join(scenario.get('blockers') or []) or 'none'}`",
            "",
        ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
