"""Sample-size runway for v28 calibrated FV overlay candidates.

This report answers a narrow operational question: how much forward evidence is
still needed before a raw-entry FV overlay can be considered validated?

It does not promote or trade. It only translates the existing readiness gates
into concrete remaining sample counts and early warning conditions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
READINESS_JSON = OUT_DIR / "v28_fv_model_readiness_latest.json"
OVERLAY_READINESS_JSON = OUT_DIR / "v28_fv_overlay_challenger_readiness_latest.json"
MONITOR_JSON = OUT_DIR / "v28_calibrated_fv_forward_monitor_latest.json"
PATH_CONFIRMED_JSON = OUT_DIR / "v28_path_confirmed_entry_candidates_latest.json"
FROZEN_RAW_ENTRY_CALIBRATED_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json"
OUT_JSON = OUT_DIR / "v28_calibrated_fv_sample_plan_latest.json"
OUT_MD = OUT_DIR / "v28_calibrated_fv_sample_plan_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 70.0
COVERAGE_MAX = 90.0
MAX_SIMULATED_SHARE = 0.35


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


def needed_misses_to_reenter_coverage(selected: int, denominator: int) -> int:
    """How many missed future markets would bring high coverage <= COVERAGE_MAX."""
    misses = 0
    while denominator + misses > 0:
        coverage = selected / (denominator + misses) * 100.0
        if coverage <= COVERAGE_MAX:
            return misses
        misses += 1
    return 0


def max_misses_before_low_coverage(selected: int, denominator: int, future_selected: int) -> int:
    """How many future misses after future_selected selected rows keep coverage >= min."""
    misses = 0
    selected_total = selected + future_selected
    while True:
        denom_total = denominator + future_selected + misses
        coverage = selected_total / denom_total * 100.0 if denom_total else 0.0
        if coverage < COVERAGE_MIN:
            return max(0, misses - 1)
        misses += 1


def best_path_candidate(path_payload: dict[str, Any]) -> dict[str, Any]:
    summaries = path_payload.get("summaries") if isinstance(path_payload.get("summaries"), list) else []
    eligible = [
        row for row in summaries
        if row.get("coverage_pct") is not None
        and COVERAGE_MIN <= float(row.get("coverage_pct") or 0.0) <= COVERAGE_MAX
    ]
    rows = eligible or summaries
    if not rows:
        return {}
    return sorted(
        rows,
        key=lambda row: (
            float(row.get("net_cents_after_entry_fee") or -999999.0),
            -float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
            float(row.get("coverage_pct") or 0.0),
        ),
        reverse=True,
    )[0]


def path_runway(row: dict[str, Any]) -> dict[str, Any]:
    entries = int(as_float(row.get("entries")) or 0)
    settled = int(as_float(row.get("settled")) or 0)
    approved = int(as_float(row.get("approved_entry_count")) or 0)
    simulated = int(as_float(row.get("added_reject_count")) or 0)
    future_actual_needed = 0
    while True:
        total = entries + future_actual_needed
        sim_share = simulated / total if total else 1.0
        if sim_share <= MAX_SIMULATED_SHARE:
            break
        future_actual_needed += 1
    return {
        "policy": row.get("policy"),
        "entries": entries,
        "settled": settled,
        "approved_entry_count": approved,
        "added_reject_count": simulated,
        "simulated_share": row.get("simulated_share"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents_after_entry_fee": row.get("net_cents_after_entry_fee"),
        "avg_brier": row.get("avg_brier"),
        "brier_delta_mean_plus05_minus_raw": row.get("brier_delta_mean_plus05_minus_raw"),
        "logloss_delta_mean_plus05_minus_raw": row.get("logloss_delta_mean_plus05_minus_raw"),
        "settled_rows_to_min_30": max(0, MIN_SETTLED - settled),
        "actual_entries_needed_for_simulated_share_lte_35pct": future_actual_needed,
    }


def build_report() -> dict[str, Any]:
    readiness = load_json(READINESS_JSON)
    overlay_readiness = load_json(OVERLAY_READINESS_JSON)
    monitor = load_json(MONITOR_JSON)
    path_confirmed = load_json(PATH_CONFIRMED_JSON)
    raw_entry_overlay_gate = load_json(FROZEN_RAW_ENTRY_CALIBRATED_JSON)
    frozen = readiness.get("frozen_forward") or {}
    overlay_rows = raw_entry_overlay_gate.get("ranked") if isinstance(raw_entry_overlay_gate.get("ranked"), list) else []
    plus05 = next((row for row in overlay_rows if row.get("overlay") == "entry_conditioned_plus05_probability"), {})
    raw = next((row for row in overlay_rows if row.get("overlay") == "raw_probability"), {})
    settled = int(as_float(monitor.get("settled_selected_count") or plus05.get("settled") or plus05.get("count")) or 0)
    denominator = int(as_float(monitor.get("clean_forward_market_count") or raw_entry_overlay_gate.get("forward_market_denominator")) or 0)
    selected = int(as_float(monitor.get("selected_clean_count") or raw_entry_overlay_gate.get("future_entry_rows")) or 0)
    pending = int(as_float(monitor.get("pending_selected_count")) or 0)
    remaining_settled = max(0, MIN_SETTLED - settled)
    future_selected_to_min = max(0, MIN_SETTLED - settled - pending)
    current_coverage = as_float(plus05.get("coverage_pct") or monitor.get("coverage_pct"))
    misses_to_target_if_too_high = needed_misses_to_reenter_coverage(selected, denominator) if current_coverage is not None and current_coverage > COVERAGE_MAX else 0
    miss_budget_after_min = max_misses_before_low_coverage(selected, denominator, future_selected_to_min)
    brier_delta = plus05.get("brier_delta_vs_raw")
    logloss_delta = plus05.get("logloss_delta_vs_raw")
    bakeoff = overlay_bakeoff(raw_entry_overlay_gate)
    best_overlay = next((row for row in bakeoff.get("ranked") or [] if row.get("overlay") == bakeoff.get("current_best_overlay")), {})
    overlay_ready_rows = overlay_readiness.get("candidates") if isinstance(overlay_readiness.get("candidates"), list) else []
    best_readiness = next((row for row in overlay_ready_rows if row.get("overlay") == bakeoff.get("current_best_overlay")), {})
    return {
        "candidate": "v28_raw_entry_fv_overlay_bakeoff",
        "current_best_overlay": bakeoff.get("current_best_overlay"),
        "readiness_blockers": best_readiness.get("blockers") or (readiness.get("readiness") or {}).get("blockers") or [],
        "freeze_ts": frozen.get("freeze_ts"),
        "current": {
            "forward_denominator": denominator,
            "selected_rows": selected,
            "settled_selected_rows": settled,
            "pending_selected_rows": pending,
            "coverage_pct": current_coverage,
            "wins": ((monitor.get("selected_win_loss") or {}).get("wins")),
            "losses": ((monitor.get("selected_win_loss") or {}).get("losses")),
            "net_cents": monitor.get("selected_net_cents"),
            "brier_delta_plus05_minus_raw": brier_delta,
            "logloss_delta_plus05_minus_raw": logloss_delta,
            "raw_brier": raw.get("avg_brier"),
            "plus05_brier": plus05.get("avg_brier"),
            "raw_logloss": raw.get("avg_logloss"),
            "plus05_logloss": plus05.get("avg_logloss"),
            "best_overlay": best_overlay.get("overlay"),
            "best_overlay_brier_delta_vs_raw": best_overlay.get("brier_delta_vs_raw"),
            "best_overlay_logloss_delta_vs_raw": best_overlay.get("logloss_delta_vs_raw"),
        },
        "remaining": {
            "settled_rows_to_min_30": remaining_settled,
            "additional_selected_rows_after_pending_to_min_30": future_selected_to_min,
            "misses_needed_to_reduce_current_high_coverage_to_90pct": misses_to_target_if_too_high,
            "miss_budget_after_reaching_30_selected_before_coverage_below_70pct": miss_budget_after_min,
        },
        "raw_entry_overlay_bakeoff": bakeoff,
        "path_confirmed_runway": path_runway(best_path_candidate(path_confirmed)),
        "early_warning_conditions": [
            "forward Brier delta turns nonnegative after at least 5 settled rows",
            "forward logloss delta turns nonnegative after at least 5 settled rows",
            "any eligible physics bucket with at least 5 settled rows has nonnegative Brier delta",
            "coverage remains above 90% after denominator is large enough to be meaningful",
            "coverage falls below 70% before 30 settled selected rows",
        ],
    }


def overlay_bakeoff(payload: dict[str, Any]) -> dict[str, Any]:
    ranked = payload.get("ranked") if isinstance(payload.get("ranked"), list) else []
    rows = []
    for row in ranked:
        rows.append({
            "overlay": row.get("overlay"),
            "entries": row.get("entries"),
            "settled": row.get("settled"),
            "coverage_pct": row.get("coverage_pct"),
            "avg_brier": row.get("avg_brier"),
            "brier_delta_vs_raw": row.get("brier_delta_vs_raw"),
            "avg_logloss": row.get("avg_logloss"),
            "logloss_delta_vs_raw": row.get("logloss_delta_vs_raw"),
            "avg_p": row.get("avg_p"),
            "win_rate": row.get("win_rate"),
            "net_cents_after_entry_fee": row.get("net_cents_after_entry_fee"),
            "blockers": row.get("blockers") or [],
        })
    return {
        "freeze_ts": payload.get("freeze_ts"),
        "forward_market_denominator": payload.get("forward_market_denominator"),
        "future_entry_rows": payload.get("future_entry_rows"),
        "ranked": rows,
        "current_best_overlay": (rows[0].get("overlay") if rows else None),
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
    cur = report["current"]
    rem = report["remaining"]
    path = report.get("path_confirmed_runway") or {}
    overlay_gate = report.get("raw_entry_overlay_bakeoff") or {}
    lines = [
        "# v28 Calibrated FV Sample Plan",
        "",
        "Forward-evidence runway for raw-entry FV overlays.",
        "",
        f"- Candidate: `{report['candidate']}`",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Readiness blockers: `{', '.join(report['readiness_blockers']) or 'none'}`",
        "",
        "## Current Forward Evidence",
        "",
        f"- Denominator/selected/settled/pending: `{cur['forward_denominator']}/{cur['selected_rows']}/{cur['settled_selected_rows']}/{cur['pending_selected_rows']}`",
        f"- Coverage: `{fmt(cur['coverage_pct'])}`",
        f"- W/L and net: `{cur['wins']}/{cur['losses']}` / `{fmt(cur['net_cents'])}c`",
        f"- Best overlay now: `{cur.get('best_overlay')}`",
        f"- Best overlay Brier/logloss delta vs raw: `{fmt(cur.get('best_overlay_brier_delta_vs_raw'))}` / `{fmt(cur.get('best_overlay_logloss_delta_vs_raw'))}`",
        f"- +5pp Brier/logloss delta vs raw: `{fmt(cur['brier_delta_plus05_minus_raw'])}` / `{fmt(cur['logloss_delta_plus05_minus_raw'])}`",
        "",
        "## Raw-Entry FV Overlay Bakeoff",
        "",
        f"- Freeze timestamp UTC: `{overlay_gate.get('freeze_ts')}`",
        f"- Forward denominator/entry rows: `{overlay_gate.get('forward_market_denominator')}/{overlay_gate.get('future_entry_rows')}`",
        f"- Current best overlay by frozen Brier: `{overlay_gate.get('current_best_overlay')}`",
        "",
        "| overlay | entries | settled | coverage | brier | brier d | logloss | logloss d | avg p | win rate | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in (overlay_gate.get("ranked") or [])[:6]:
        lines.append(
            f"| {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('avg_logloss'))} | "
            f"{fmt(row.get('logloss_delta_vs_raw'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('win_rate'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Remaining Runway",
        "",
        f"- Settled selected rows still needed for 30: `{rem['settled_rows_to_min_30']}`",
        f"- Additional selected rows after current pending rows needed for 30: `{rem['additional_selected_rows_after_pending_to_min_30']}`",
        f"- Misses needed to bring current high coverage down to <=90%: `{rem['misses_needed_to_reduce_current_high_coverage_to_90pct']}`",
        f"- Miss budget after reaching 30 selected before coverage <70%: `{rem['miss_budget_after_reaching_30_selected_before_coverage_below_70pct']}`",
        "",
        "## Path/RMT Candidate Runway",
        "",
        f"- Current best target-coverage path policy: `{path.get('policy')}`",
        f"- Entries/settled: `{path.get('entries')}/{path.get('settled')}`",
        f"- Actual/simulated entries: `{path.get('approved_entry_count')}/{path.get('added_reject_count')}`; simulated share `{fmt(path.get('simulated_share'))}`",
        f"- Coverage/net/Brier: `{fmt(path.get('coverage_pct'))}` / `{fmt(path.get('net_cents_after_entry_fee'))}c` / `{fmt(path.get('avg_brier'))}`",
        f"- Calibration deltas Brier/logloss: `{fmt(path.get('brier_delta_mean_plus05_minus_raw'))}` / `{fmt(path.get('logloss_delta_mean_plus05_minus_raw'))}`",
        f"- Settled rows still needed for 30: `{path.get('settled_rows_to_min_30')}`",
        f"- Additional actual entries needed for simulated share <=35%: `{path.get('actual_entries_needed_for_simulated_share_lte_35pct')}`",
        "",
        "## Early Warnings",
        "",
    ])
    for item in report["early_warning_conditions"]:
        lines.append(f"- {item}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
