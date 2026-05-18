"""Coverage-valve diagnostics for raw-v28 broad entry.

Research-only; no live bot changes or orders.

The FV overlay work improved calibration, but the forward broad raw-p50 entry
surface is selecting too many weak boundary rows. This probe tests a simple
physics valve on the same raw-v28 p50 candidate family:

    keep the first raw-p50 entry only if raw edge >= 5pp OR raw probability >= 60%.

Interpretation: weak probability plus thin executable edge is not enough
terminal information in a noisy 15-minute BTC market. Strong edge or stronger
raw conviction may still justify broad participation.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS, score_overlay
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_state.json"
OUT_JSON = OUT_DIR / "v28_raw_entry_coverage_valve_latest.json"
OUT_MD = OUT_DIR / "v28_raw_entry_coverage_valve_latest.md"

FV_OVERLAY = "entry_conditioned_logit125_p60_only_probability"
EDGE_LADDER = [0.03, 0.04, 0.05]
MIN_P_KEEP = 0.60
TURBULENCE_EDGE = 0.04
TURBULENCE_RECROSS = 0.75
TURBULENCE_ABS_D = 0.25
TURBULENCE_GRID = [
    (0.03, 0.75, 0.25),
    (0.04, 0.75, 0.25),
    (0.04, 0.90, 0.25),
    (0.04, 0.90, 0.20),
]
MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def logloss(p: float, outcome: float) -> float:
    p = max(0.000001, min(0.999999, p))
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def selected_base_rows() -> list[dict[str, Any]]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    return selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)


def row_edge(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side") or row.get("p_eff"))
    ask = as_float(row.get("ask_prob"))
    if p is None or ask is None:
        return None
    return p - ask


def valve_reason(row: dict[str, Any], min_edge_keep: float) -> str:
    p = as_float(row.get("p_side") or row.get("p_eff")) or 0.0
    edge = row_edge(row)
    if edge is not None and edge >= min_edge_keep:
        return f"keep_edge_ge_{int(round(min_edge_keep * 100))}pp"
    if p >= MIN_P_KEEP:
        return "keep_p_ge_60"
    return "skip_weak_p_and_edge"


def turbulence_valve_reason(
    row: dict[str, Any],
    min_edge_keep: float = TURBULENCE_EDGE,
    recross_floor: float = TURBULENCE_RECROSS,
    near_abs_d: float = TURBULENCE_ABS_D,
) -> str:
    p = as_float(row.get("p_side") or row.get("p_eff")) or 0.0
    edge = row_edge(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    if p >= MIN_P_KEEP:
        return "keep_p_ge_60"
    if edge is not None and edge >= min_edge_keep:
        return f"keep_edge_ge_{int(round(min_edge_keep * 100))}pp"
    if edge is not None and recross >= recross_floor and abs_d <= near_abs_d:
        return f"skip_weak_thin_recross{int(round(recross_floor * 100))}_near{int(round(near_abs_d * 100))}"
    return "keep_not_turbulent"


def apply_valve(rows: list[dict[str, Any]], min_edge_keep: float) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for row in rows:
        reason = valve_reason(row, min_edge_keep)
        if reason.startswith("skip"):
            continue
        kept.append({
            **row,
            "coverage_valve_reason": reason,
            "raw_edge_prob": row_edge(row),
        })
    return kept


def apply_turbulence_valve(
    rows: list[dict[str, Any]],
    min_edge_keep: float = TURBULENCE_EDGE,
    recross_floor: float = TURBULENCE_RECROSS,
    near_abs_d: float = TURBULENCE_ABS_D,
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for row in rows:
        reason = turbulence_valve_reason(row, min_edge_keep, recross_floor, near_abs_d)
        if reason.startswith("skip"):
            continue
        kept.append({
            **row,
            "coverage_valve_reason": reason,
            "raw_edge_prob": row_edge(row),
        })
    return kept


def summarize(rows: list[dict[str, Any]], denominator: int, overlay: str) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    fn = OVERLAYS[overlay]
    probs = [float(fn(row)) for row in settled]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in settled]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / denominator * 100.0 if denominator else None,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(settled) if settled else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
        "avg_p": sum(probs) / len(probs) if probs else None,
    }


def blockers(summary: dict[str, Any], baseline: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = float(summary.get("settled") or 0.0)
    coverage = as_float(summary.get("coverage_pct"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if as_float(summary.get("net_cents_after_entry_fee")) is None or as_float(summary.get("net_cents_after_entry_fee")) <= 0.0:
        out.append("net_not_positive")
    base_net = as_float(baseline.get("net_cents_after_entry_fee"))
    net = as_float(summary.get("net_cents_after_entry_fee"))
    if base_net is not None and net is not None and net < base_net:
        out.append("net_worse_than_base")
    return out


def runway(summary: dict[str, Any]) -> dict[str, Any]:
    entries = int(as_float(summary.get("entries")) or 0)
    settled = int(as_float(summary.get("settled")) or 0)
    denominator = int(round(entries / ((as_float(summary.get("coverage_pct")) or 0.0) / 100.0))) if as_float(summary.get("coverage_pct")) else entries
    selected_needed = max(0, MIN_SETTLED - settled)
    selected_total = entries + selected_needed
    denom_after_selected = denominator + selected_needed
    misses_to_get_below_high = 0
    while denom_after_selected + misses_to_get_below_high > 0:
        coverage = selected_total / (denom_after_selected + misses_to_get_below_high) * 100.0
        if coverage <= COVERAGE_MAX:
            break
        misses_to_get_below_high += 1
    miss_budget_before_low = 0
    while denom_after_selected + miss_budget_before_low > 0:
        coverage = selected_total / (denom_after_selected + miss_budget_before_low) * 100.0
        if coverage < COVERAGE_MIN:
            miss_budget_before_low = max(0, miss_budget_before_low - 1)
            break
        miss_budget_before_low += 1
    return {
        "settled_rows_to_30": selected_needed,
        "future_selected_rows_to_30": selected_needed,
        "misses_needed_to_reenter_max_90_after_30": misses_to_get_below_high,
        "miss_budget_before_coverage_below_75_after_30": miss_budget_before_low,
    }


def detail_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for row in rows:
        details.append({
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_raw": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row_edge(row),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            "coverage_valve_reason": row.get("coverage_valve_reason") or row.get("coverage_valve_reason_fallback"),
        })
    return details


def build_policy(
    min_edge_keep: float,
    discovery_base: list[dict[str, Any]],
    forward_base: list[dict[str, Any]],
    discovery_denominator: int,
    forward_denominator: int,
) -> dict[str, Any]:
    discovery_valve = apply_valve(discovery_base, min_edge_keep)
    forward_valve = apply_valve(forward_base, min_edge_keep)
    discovery_base_summary = summarize(discovery_base, discovery_denominator, FV_OVERLAY)
    discovery_valve_summary = summarize(discovery_valve, discovery_denominator, FV_OVERLAY)
    forward_base_summary = summarize(forward_base, forward_denominator, FV_OVERLAY)
    forward_valve_summary = summarize(forward_valve, forward_denominator, FV_OVERLAY)
    selected_markets = {str(item.get("market") or "") for item in forward_valve}
    skipped_forward = [
        {**row, "coverage_valve_reason_fallback": valve_reason(row, min_edge_keep)}
        for row in forward_base
        if str(row.get("market") or "") not in selected_markets
    ]
    return {
        "policy": f"raw_p50_coverage_valve_edge{int(round(min_edge_keep * 100))}_or_p60",
        "min_edge_keep": min_edge_keep,
        "min_p_keep": MIN_P_KEEP,
        "discovery": {
            "baseline": discovery_base_summary,
            "coverage_valve": discovery_valve_summary,
            "delta_net_cents": (as_float(discovery_valve_summary.get("net_cents_after_entry_fee")) or 0.0) - (as_float(discovery_base_summary.get("net_cents_after_entry_fee")) or 0.0),
        },
        "forward": {
            "baseline": forward_base_summary,
            "coverage_valve": forward_valve_summary,
            "delta_net_cents": (as_float(forward_valve_summary.get("net_cents_after_entry_fee")) or 0.0) - (as_float(forward_base_summary.get("net_cents_after_entry_fee")) or 0.0),
            "blockers": blockers(forward_valve_summary, forward_base_summary),
            "runway": runway(forward_valve_summary),
        },
        "forward_selected_rows": detail_rows(forward_valve),
        "forward_skipped_rows": detail_rows(skipped_forward),
    }


def build_turbulence_policy(
    discovery_base: list[dict[str, Any]],
    forward_base: list[dict[str, Any]],
    discovery_denominator: int,
    forward_denominator: int,
    min_edge_keep: float = TURBULENCE_EDGE,
    recross_floor: float = TURBULENCE_RECROSS,
    near_abs_d: float = TURBULENCE_ABS_D,
) -> dict[str, Any]:
    discovery_valve = apply_turbulence_valve(discovery_base, min_edge_keep, recross_floor, near_abs_d)
    forward_valve = apply_turbulence_valve(forward_base, min_edge_keep, recross_floor, near_abs_d)
    discovery_base_summary = summarize(discovery_base, discovery_denominator, FV_OVERLAY)
    discovery_valve_summary = summarize(discovery_valve, discovery_denominator, FV_OVERLAY)
    forward_base_summary = summarize(forward_base, forward_denominator, FV_OVERLAY)
    forward_valve_summary = summarize(forward_valve, forward_denominator, FV_OVERLAY)
    selected_markets = {str(item.get("market") or "") for item in forward_valve}
    skipped_forward = [
        {**row, "coverage_valve_reason_fallback": turbulence_valve_reason(row, min_edge_keep, recross_floor, near_abs_d)}
        for row in forward_base
        if str(row.get("market") or "") not in selected_markets
    ]
    return {
        "policy": f"raw_p50_turbulence_valve_edge{int(round(min_edge_keep * 100))}_p60_recross{int(round(recross_floor * 100))}_near{int(round(near_abs_d * 100))}",
        "min_edge_keep": min_edge_keep,
        "min_p_keep": MIN_P_KEEP,
        "recross_floor": recross_floor,
        "near_abs_d": near_abs_d,
        "discovery": {
            "baseline": discovery_base_summary,
            "coverage_valve": discovery_valve_summary,
            "delta_net_cents": (as_float(discovery_valve_summary.get("net_cents_after_entry_fee")) or 0.0) - (as_float(discovery_base_summary.get("net_cents_after_entry_fee")) or 0.0),
        },
        "forward": {
            "baseline": forward_base_summary,
            "coverage_valve": forward_valve_summary,
            "delta_net_cents": (as_float(forward_valve_summary.get("net_cents_after_entry_fee")) or 0.0) - (as_float(forward_base_summary.get("net_cents_after_entry_fee")) or 0.0),
            "blockers": blockers(forward_valve_summary, forward_base_summary),
            "runway": runway(forward_valve_summary),
        },
        "forward_selected_rows": detail_rows(forward_valve),
        "forward_skipped_rows": detail_rows(skipped_forward),
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_dt = parse_ts(state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    all_rows = selected_base_rows()
    discovery_base = all_rows
    forward_base = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    discovery_denominator = len({str(row.get("market") or "") for row in all_rows if row.get("market")})
    forward_denominator = len(forward_markets)
    policies = [
        build_policy(edge, discovery_base, forward_base, discovery_denominator, forward_denominator)
        for edge in EDGE_LADDER
    ]
    for edge, recross, near_abs_d in TURBULENCE_GRID:
        policies.append(build_turbulence_policy(discovery_base, forward_base, discovery_denominator, forward_denominator, edge, recross, near_abs_d))
    ranked = sorted(
        policies,
        key=lambda item: (
            float((item.get("forward") or {}).get("coverage_valve", {}).get("coverage_pct") or -999.0) < COVERAGE_MIN,
            float((item.get("forward") or {}).get("coverage_valve", {}).get("coverage_pct") or 999.0) > COVERAGE_MAX,
            -float((item.get("forward") or {}).get("coverage_valve", {}).get("net_cents_after_entry_fee") or -999999.0),
            -float((item.get("discovery") or {}).get("coverage_valve", {}).get("net_cents_after_entry_fee") or -999999.0),
            -float((item.get("discovery") or {}).get("coverage_valve", {}).get("coverage_pct") or -999.0),
        ),
    )
    return {
        "policy_family": "raw_p50_coverage_valve_edge_ladder_or_p60",
        "fv_overlay": FV_OVERLAY,
        "physics": "Skip only weak raw-p50 entries where both executable edge is below a small physical margin and raw probability <60%.",
        "freeze_ts": state.get("freeze_ts"),
        "forward_denominator": forward_denominator,
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "policies": policies,
        "ranked": ranked,
        "best_policy": ranked[0].get("policy") if ranked else None,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def summary_line(name: str, row: dict[str, Any]) -> str:
    return (
        f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
        f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents_after_entry_fee'))} | "
        f"{fmt(row.get('avg_net_cents_after_entry_fee'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('avg_logloss'))} |"
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Raw-Entry Coverage Valve",
        "",
        "Shadow-only diagnostic for target coverage on the raw-v28 p50 entry surface.",
        "",
        f"- Policy family: `{report.get('policy_family')}`",
        f"- FV overlay: `{report.get('fv_overlay')}`",
        f"- Physics: {report.get('physics')}",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Best current forward policy: `{report.get('best_policy')}`",
        "",
        "## Ladder",
        "",
        "| policy | disc entries | disc coverage | disc net | fwd entries | fwd settled | fwd W/L | fwd coverage | fwd net | fwd brier | to30 | miss budget | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for policy in report.get("ranked") or []:
        disc = (policy.get("discovery") or {}).get("coverage_valve") or {}
        fwd = (policy.get("forward") or {}).get("coverage_valve") or {}
        run = (policy.get("forward") or {}).get("runway") or {}
        lines.append(
            f"| {policy.get('policy')} | {disc.get('entries')} | {fmt(disc.get('coverage_pct'))} | "
            f"{fmt(disc.get('net_cents_after_entry_fee'))} | {fwd.get('entries')} | {fwd.get('settled')} | "
            f"{fwd.get('wins')}/{fwd.get('losses')} | {fmt(fwd.get('coverage_pct'))} | "
            f"{fmt(fwd.get('net_cents_after_entry_fee'))} | {fmt(fwd.get('avg_brier'))} | "
            f"{run.get('settled_rows_to_30')} | {run.get('miss_budget_before_coverage_below_75_after_30')} | "
            f"{', '.join((policy.get('forward') or {}).get('blockers') or []) or 'none'} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Forward Selected Rows",
        "",
        "| market | side | p raw | ask | edge | stc | abs d | recross | won | net c | reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in best.get("forward_selected_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} | {row.get('coverage_valve_reason')} |"
        )
    lines.extend([
        "",
        "## Forward Skipped Rows",
        "",
        "| market | side | p raw | ask | edge | stc | abs d | recross | won | net c | reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in best.get("forward_skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} | {row.get('coverage_valve_reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
