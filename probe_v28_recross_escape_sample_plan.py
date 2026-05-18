"""Sample-size runway for the p52 recross-escape + plus05 FV candidate.

Research-only. This does not change live bot logic or place orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_RECROSS_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"
FROZEN_PROB_JSON = OUT_DIR / "v28_frozen_recross_escape_probability_calibration_latest.json"
OUT_JSON = OUT_DIR / "v28_recross_escape_sample_plan_latest.json"
OUT_MD = OUT_DIR / "v28_recross_escape_sample_plan_latest.md"

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


def policy_row(payload: dict[str, Any], policy: str) -> dict[str, Any]:
    for row in payload.get("summary") or []:
        if row.get("policy") == policy:
            return row
    return {}


def probability_row(payload: dict[str, Any], probability: str) -> dict[str, Any]:
    for row in payload.get("summaries") or []:
        if row.get("probability") == probability:
            return row
    return {}


def future_actual_needed(entries: int, simulated: int) -> int:
    needed = 0
    while True:
        total = entries + needed
        sim_share = simulated / total if total else 1.0
        if sim_share <= MAX_SIMULATED_SHARE:
            return needed
        needed += 1


def misses_needed_to_reduce_coverage(entries: int, denominator: int) -> int:
    misses = 0
    while denominator + misses > 0:
        coverage = entries / (denominator + misses) * 100.0
        if coverage <= COVERAGE_MAX:
            return misses
        misses += 1
    return 0


def miss_budget_before_low_coverage(entries: int, denominator: int, future_entries: int) -> int:
    misses = 0
    while True:
        denom = denominator + future_entries + misses
        selected = entries + future_entries
        coverage = selected / denom * 100.0 if denom else 0.0
        if coverage < COVERAGE_MIN:
            return max(0, misses - 1)
        misses += 1


def build_report() -> dict[str, Any]:
    recross = load_json(FROZEN_RECROSS_JSON)
    prob = load_json(FROZEN_PROB_JSON)
    challenger = policy_row(recross, "p52_recross_escape_opp240_oppedge5_keep")
    baseline = policy_row(recross, "v28_raw_p52_edge0_base")
    raw_prob = probability_row(prob, "raw_probability")
    plus05 = probability_row(prob, "plus05_probability")

    denominator = int(as_float(recross.get("forward_market_denominator")) or 0)
    entries = int(as_float(challenger.get("entries")) or 0)
    settled = int(as_float(challenger.get("settled")) or 0)
    simulated = int(as_float(challenger.get("added_reject_count")) or 0)
    approved = int(as_float(challenger.get("approved_entry_count")) or 0)
    pending = max(0, entries - settled)
    additional_settled_after_pending = max(0, MIN_SETTLED - settled - pending)
    return {
        "candidate": "p52_recross_escape_opp240_oppedge5_keep_plus05_probability",
        "selector_policy": "p52_recross_escape_opp240_oppedge5_keep",
        "probability_policy": "plus05_probability",
        "freeze_ts": recross.get("freeze_ts"),
        "forward_denominator": denominator,
        "excluded_in_progress_count": len(recross.get("excluded_in_progress_markets") or []),
        "baseline": summarize_row(baseline),
        "selector": summarize_row(challenger),
        "probability": {
            "raw": summarize_probability(raw_prob),
            "plus05": summarize_probability(plus05),
            "plus05_brier_delta_vs_raw": plus05.get("brier_delta_vs_raw"),
            "plus05_logloss_delta_vs_raw": plus05.get("logloss_delta_vs_raw"),
            "plus05_ece_delta_vs_raw": plus05.get("ece_delta_vs_raw"),
        },
        "runway": {
            "settled_rows_to_30": max(0, MIN_SETTLED - settled),
            "pending_rows": pending,
            "additional_settled_after_pending_to_30": additional_settled_after_pending,
            "future_clean_denominator_to_30": max(0, MIN_SETTLED - denominator),
            "actual_entries_needed_for_sim_share_lte_35pct": future_actual_needed(entries, simulated),
            "misses_needed_to_reduce_current_coverage_to_90pct": (
                misses_needed_to_reduce_coverage(entries, denominator)
                if challenger.get("coverage_pct") is not None and float(challenger.get("coverage_pct") or 0.0) > COVERAGE_MAX
                else 0
            ),
            "miss_budget_after_30_before_coverage_below_70pct": miss_budget_before_low_coverage(
                entries,
                denominator,
                max(0, MIN_SETTLED - settled),
            ),
        },
        "blockers": {
            "fv": ((challenger.get("fv_validation_checks") or {}).get("blockers") or []),
            "execution": ((challenger.get("execution_promotion_checks") or {}).get("blockers") or []),
        },
        "acceptance_conditions": [
            "at least 30 settled forward rows",
            "coverage remains between 70% and 90%",
            "net P&L stays positive versus raw p52 on the same future denominator",
            "plus05 Brier and logloss deltas versus raw probability remain negative",
            "simulated/rejected-actionable share falls to <=35% before any live promotion",
        ],
    }


def summarize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents_after_entry_fee": row.get("net_cents_after_entry_fee"),
        "avg_brier": row.get("avg_brier"),
        "approved_entry_count": row.get("approved_entry_count"),
        "added_reject_count": row.get("added_reject_count"),
        "mode_counts": row.get("mode_counts"),
        "vs_raw_p52_base": row.get("vs_raw_p52_base"),
    }


def summarize_probability(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "avg_p": row.get("avg_p"),
        "avg_brier": row.get("avg_brier"),
        "avg_logloss": row.get("avg_logloss"),
        "ece": row.get("ece"),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    selector = report["selector"]
    baseline = report["baseline"]
    prob = report["probability"]
    runway = report["runway"]
    blockers = report["blockers"]
    lines = [
        "# v28 Recross-Escape Sample Plan",
        "",
        "Forward-evidence runway for the p52 recross-escape selector plus +5pp FV overlay.",
        "",
        f"- Candidate: `{report['candidate']}`",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Forward denominator: `{report['forward_denominator']}`",
        f"- Excluded in-progress markets: `{report['excluded_in_progress_count']}`",
        "",
        "## Selector Evidence",
        "",
        f"- Raw p52 baseline entries/settled/W-L/net: `{baseline.get('entries')}/{baseline.get('settled')}/{baseline.get('wins')}-{baseline.get('losses')}/{fmt(baseline.get('net_cents_after_entry_fee'))}c`",
        f"- Recross selector entries/settled/W-L/net: `{selector.get('entries')}/{selector.get('settled')}/{selector.get('wins')}-{selector.get('losses')}/{fmt(selector.get('net_cents_after_entry_fee'))}c`",
        f"- Coverage: `{fmt(selector.get('coverage_pct'))}`",
        f"- Net/Brier vs raw p52: `{fmt((selector.get('vs_raw_p52_base') or {}).get('net_cents_delta'))}c` / `{fmt((selector.get('vs_raw_p52_base') or {}).get('brier_delta'))}`",
        f"- Modes: `{selector.get('mode_counts')}`",
        "",
        "## FV Overlay Evidence",
        "",
        f"- Raw probability settled/Brier/logloss: `{(prob.get('raw') or {}).get('settled')}` / `{fmt((prob.get('raw') or {}).get('avg_brier'))}` / `{fmt((prob.get('raw') or {}).get('avg_logloss'))}`",
        f"- +5 probability settled/Brier/logloss: `{(prob.get('plus05') or {}).get('settled')}` / `{fmt((prob.get('plus05') or {}).get('avg_brier'))}` / `{fmt((prob.get('plus05') or {}).get('avg_logloss'))}`",
        f"- +5 deltas Brier/logloss/ECE: `{fmt(prob.get('plus05_brier_delta_vs_raw'))}` / `{fmt(prob.get('plus05_logloss_delta_vs_raw'))}` / `{fmt(prob.get('plus05_ece_delta_vs_raw'))}`",
        "",
        "## Remaining Runway",
        "",
        f"- Settled rows to 30: `{runway['settled_rows_to_30']}`",
        f"- Current pending rows: `{runway['pending_rows']}`",
        f"- Additional settled rows after pending to 30: `{runway['additional_settled_after_pending_to_30']}`",
        f"- Future clean denominator to 30: `{runway['future_clean_denominator_to_30']}`",
        f"- Actual entries needed for simulated share <=35%: `{runway['actual_entries_needed_for_sim_share_lte_35pct']}`",
        f"- Misses needed to reduce current high coverage to <=90%: `{runway['misses_needed_to_reduce_current_coverage_to_90pct']}`",
        f"- Miss budget after 30 before coverage <70%: `{runway['miss_budget_after_30_before_coverage_below_70pct']}`",
        "",
        "## Current Blockers",
        "",
        f"- FV blockers: `{', '.join(blockers.get('fv') or []) or 'none'}`",
        f"- Execution blockers: `{', '.join(blockers.get('execution') or []) or 'none'}`",
        "",
        "## Acceptance Conditions",
        "",
    ]
    for item in report["acceptance_conditions"]:
        lines.append(f"- {item}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
