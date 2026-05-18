"""Portfolio-level gate for live-trialing v28 candidates.

Research-only; no live bot changes or orders.

Single-candidate readiness can be misleading when the user wants multiple
strategies running at once. This report asks the operational question directly:
are any candidate families evidence-ready, can they be tracked distinctly, and
would stacked exposure be acceptable for the current small account?
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_PATH = ROOT / "state" / "live_mushroom_v28_size2" / "bot_state.json"
READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
RUNWAY_JSON = OUT_DIR / "v28_candidate_live_validation_runway_latest.json"
MATRIX_JSON = OUT_DIR / "v28_fv_candidate_decision_matrix_latest.json"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
OUT_JSON = OUT_DIR / "v28_candidate_portfolio_trial_gate_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_portfolio_trial_gate_latest.md"

DEFAULT_ACCOUNT_BALANCE_CENTS = 2640
POSITION_SIZE = 2
MAX_PARALLEL_RISK_FRACTION = 0.35
MIN_SETTLED = 30
TARGET_MIN_COVERAGE = 75.0
TARGET_MAX_COVERAGE = 90.0


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


def as_int(value: Any) -> int:
    number = as_float(value)
    return int(number) if number is not None else 0


def env_balance_cents() -> int:
    value = os.environ.get("V28_CURRENT_ACCOUNT_BALANCE_CENTS")
    parsed = as_float(value)
    if parsed is not None and parsed > 0:
        return int(parsed)
    return DEFAULT_ACCOUNT_BALANCE_CENTS


def blocker_weight(blocker: str) -> int:
    if blocker == "control_risk_stop_active":
        return 100
    if "net_not_positive" in blocker:
        return 80
    if "simulated_share" in blocker:
        return 70
    if "settled_lt_30" in blocker:
        return 50
    if "coverage" in blocker:
        return 40
    if "brier" in blocker or "logloss" in blocker:
        return 35
    return 20


def near_score(row: dict[str, Any]) -> tuple[int, int, float, float]:
    blockers = [str(item) for item in (row.get("blockers") or [])]
    penalty = sum(blocker_weight(item) for item in blockers)
    settled_gap = max(0, MIN_SETTLED - as_int(row.get("settled")))
    net = as_float(row.get("net_cents_after_entry_fee"))
    brier = as_float(row.get("avg_brier"))
    # Lower tuple is better. Prefer fewer blockers, mature sample, positive PnL,
    # then better calibration delta when it is a delta-style value.
    return (
        penalty,
        settled_gap,
        -(net if net is not None else -99999.0),
        brier if brier is not None else 99999.0,
    )


def coverage_fit(value: Any) -> str:
    coverage = as_float(value)
    if coverage is None:
        return "unknown"
    if coverage < TARGET_MIN_COVERAGE:
        return "low"
    if coverage > TARGET_MAX_COVERAGE:
        return "high"
    return "target"


def state_exposure() -> dict[str, Any]:
    state = load_json(STATE_PATH)
    pos = state.get("position") if isinstance(state.get("position"), dict) else None
    if not pos:
        return {
            "open_position": False,
            "market": None,
            "side": None,
            "count": 0,
            "entry_price_cents": None,
            "risk_cents": 0,
        }
    count = as_int(pos.get("count"))
    entry = as_int(pos.get("entry_fill_price_cents") or pos.get("entry_limit_price_cents"))
    return {
        "open_position": True,
        "market": pos.get("market_ticker"),
        "side": pos.get("side"),
        "count": count,
        "entry_price_cents": entry,
        "risk_cents": count * entry,
    }


def build_report() -> dict[str, Any]:
    readiness = load_json(READINESS_JSON)
    runway = load_json(RUNWAY_JSON)
    matrix = load_json(MATRIX_JSON)
    scorecard = load_json(SCORECARD_JSON).get("summary", {})
    candidates = readiness.get("candidates") if isinstance(readiness.get("candidates"), list) else []
    live_ready = [row for row in candidates if row.get("live_ready") is True]
    ranked_near = sorted(candidates, key=near_score)[:12]

    runway_rows = runway.get("ranked") if isinstance(runway.get("ranked"), list) else []
    validation_lanes = []
    for row in runway_rows[:8]:
        validation_lanes.append({
            "policy": row.get("policy"),
            "coverage_pct": row.get("coverage_pct"),
            "gross_cents": row.get("gross_cents"),
            "simulated_share": row.get("simulated_share"),
            "future_actual_needed": row.get("future_actual_entries_needed_for_sim_share_lte_35"),
            "minimum_future_validation_rows_needed": row.get("minimum_future_validation_rows_needed"),
            "blockers": row.get("blockers") or [],
        })

    exposure = state_exposure()
    account = env_balance_cents()
    current_risk = as_float(exposure.get("risk_cents")) or 0.0
    max_parallel_risk = account * MAX_PARALLEL_RISK_FRACTION
    remaining_parallel_risk = max(0.0, max_parallel_risk - current_risk)
    nominal_candidate_risk = POSITION_SIZE * 85
    additional_slots = int(remaining_parallel_risk // nominal_candidate_risk)

    risk_stop = scorecard.get("risk_stop") is True or readiness.get("control_risk_stop_active") is True
    blockers = []
    if not live_ready:
        blockers.append("no_candidate_live_ready")
    if risk_stop:
        blockers.append("control_risk_stop_active")
    if exposure.get("open_position"):
        blockers.append("live_v28_position_open")
    if additional_slots < 1:
        blockers.append("portfolio_risk_budget_full")

    recommendations = []
    if blockers:
        recommendations.append("Do not start live multi-candidate trading from this state.")
    recommendations.append("Keep candidate validation in shadow with distinct policy tags and actual-vs-simulated attribution.")
    if validation_lanes:
        best_lane = validation_lanes[0]
        recommendations.append(
            f"Closest validation lane is {best_lane.get('policy')} needing {best_lane.get('minimum_future_validation_rows_needed')} future rows."
        )
    matrix_notes = matrix.get("current_read") or matrix.get("interpretation") or []

    return {
        "account_balance_cents": account,
        "max_parallel_risk_fraction": MAX_PARALLEL_RISK_FRACTION,
        "max_parallel_risk_cents": max_parallel_risk,
        "current_live_exposure": exposure,
        "remaining_parallel_risk_cents": remaining_parallel_risk,
        "nominal_candidate_risk_cents": nominal_candidate_risk,
        "additional_candidate_slots_by_risk": additional_slots,
        "any_live_ready": bool(live_ready),
        "risk_stop_active": risk_stop,
        "portfolio_live_trial_ready": not blockers,
        "portfolio_blockers": blockers,
        "live_ready_candidates": live_ready,
        "nearest_candidates": [
            {
                "gate": row.get("gate"),
                "policy": row.get("policy"),
                "entries": row.get("entries"),
                "settled": row.get("settled"),
                "coverage_pct": row.get("coverage_pct"),
                "coverage_fit": coverage_fit(row.get("coverage_pct")),
                "net_cents_after_entry_fee": row.get("net_cents_after_entry_fee"),
                "avg_brier": row.get("avg_brier"),
                "blockers": row.get("blockers") or [],
            }
            for row in ranked_near
        ],
        "validation_lanes": validation_lanes,
        "matrix_notes": matrix_notes[:8] if isinstance(matrix_notes, list) else [],
        "recommendations": recommendations,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    exp = report.get("current_live_exposure") or {}
    lines = [
        "# v28 Candidate Portfolio Trial Gate",
        "",
        "Research-only gate for whether multiple candidate strategies can be live-trialed safely and cleanly.",
        "",
        f"- Portfolio live-trial ready: `{report.get('portfolio_live_trial_ready')}`",
        f"- Any candidate individually live-ready: `{report.get('any_live_ready')}`",
        f"- Risk stop active: `{report.get('risk_stop_active')}`",
        f"- Account balance used: `{fmt(report.get('account_balance_cents'))}c`",
        f"- Current live exposure: `{fmt(exp.get('risk_cents'))}c` on `{exp.get('market')}` `{exp.get('side')}` x `{exp.get('count')}`",
        f"- Remaining parallel risk budget: `{fmt(report.get('remaining_parallel_risk_cents'))}c`",
        f"- Additional nominal candidate slots by risk: `{report.get('additional_candidate_slots_by_risk')}`",
        f"- Portfolio blockers: `{', '.join(report.get('portfolio_blockers') or []) or 'none'}`",
        "",
        "## Recommendations",
        "",
    ]
    for item in report.get("recommendations") or []:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Nearest Candidates",
        "",
        "| gate | policy | settled | coverage | fit | net c | brier | blockers |",
        "|---|---|---:|---:|---|---:|---:|---|",
    ])
    for row in report.get("nearest_candidates") or []:
        lines.append(
            f"| {row.get('gate')} | `{row.get('policy')}` | {fmt(row.get('settled'))} | "
            f"{fmt(row.get('coverage_pct'))} | {row.get('coverage_fit')} | "
            f"{fmt(row.get('net_cents_after_entry_fee'))} | {fmt(row.get('avg_brier'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Validation Lanes",
        "",
        "| policy | coverage | gross c | sim share | future actual needed | min validation rows | blockers |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("validation_lanes") or []:
        lines.append(
            f"| `{row.get('policy')}` | {fmt(row.get('coverage_pct'))} | {fmt(row.get('gross_cents'))} | "
            f"{fmt(row.get('simulated_share'))} | {fmt(row.get('future_actual_needed'))} | "
            f"{fmt(row.get('minimum_future_validation_rows_needed'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
