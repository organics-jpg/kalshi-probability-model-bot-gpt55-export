"""Frozen forward validator for raw-v28 physics penalty challengers."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import (
    fv_validation_checks,
    market_timing,
    parse_ts,
    promotion_checks,
    selected_row_details,
    summarize,
)
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_physics_challengers_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_raw_physics_challengers_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_raw_physics_challengers_latest.md"

FROZEN_POLICIES = [
    {
        "policy": "v28_raw_p52_edge0",
        "role": "raw_calibration_challenger",
        "physics": "Raises raw v28 confidence floor from 0.50 to 0.52 while keeping nonnegative executable edge. Tests whether a tiny probability margin removes noisy boundary rows while keeping broad coverage.",
    },
    {
        "policy": "raw_fee_friction_p50_edge0",
        "role": "fee_aware_raw_challenger",
        "physics": "Subtracts estimated Kalshi taker fee from raw v28 probability before entry. This is pure execution physics, not a fitted threshold.",
    },
    {
        "policy": "raw_touch_friction_p50_edge0",
        "role": "touch_depth_raw_challenger",
        "physics": "Subtracts fee plus fragile-touch depth penalties. Tests whether thin/crowded touch conditions make raw fair value overconfident.",
    },
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts"):
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "policies": FROZEN_POLICIES,
        "promotion_floor": {
            "min_settled": 30,
            "max_simulated_share": 0.35,
            "required_coverage_pct_min": 70.0,
            "required_coverage_pct_max": 90.0,
            "must_be_net_positive": True,
            "fv_validation_allows_shadow_rows": True,
        },
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    payload = build_raw_physics_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    future_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    forward_denominator = len(forward_markets)
    floor = state.get("promotion_floor") or {}
    summary: list[dict[str, Any]] = []
    for item in state.get("policies") or FROZEN_POLICIES:
        policy = item["policy"]
        policy_rows = [row for row in future_rows if row.get("policy") == policy]
        s = summarize(policy, policy_rows, forward_denominator)
        selected_markets = {str(row.get("market") or "") for row in policy_rows if row.get("market")}
        missed_markets = sorted(forward_markets - selected_markets)
        summary.append({
            **s,
            "role": item.get("role"),
            "physics": item.get("physics"),
            "missed_forward_markets": missed_markets,
            "missed_forward_market_count": len(missed_markets),
            "selected_forward_rows": selected_row_details(policy_rows),
            "fv_validation_checks": fv_validation_checks(s, floor),
            "execution_promotion_checks": promotion_checks(s, floor),
        })
    return {
        "freeze_ts": state["freeze_ts"],
        "forward_market_denominator": forward_denominator,
        "forward_markets": sorted(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "post_freeze_observed_markets": sorted(timing["post_freeze_observed_markets"]),
        "future_candidate_rows": len(future_rows),
        "policies": state.get("policies") or FROZEN_POLICIES,
        "promotion_floor": floor,
        "summary": summary,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Raw Physics Challengers",
        "",
        "Forward-only validator. Rows before freeze timestamp do not count.",
        "",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Forward market denominator: `{report['forward_market_denominator']}`",
        f"- Future candidate rows: `{report['future_candidate_rows']}`",
        "",
        "## Forward Scorecard",
        "",
        "| policy | entries | settled | wins/losses | coverage | net c | avg brier | actual/shadow | FV blockers | execution blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["summary"]:
        fv_checks = row.get("fv_validation_checks") or {}
        exec_checks = row.get("execution_promotion_checks") or {}
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents_after_entry_fee'))} | "
            f"{fmt(row.get('avg_brier'))} | {row.get('approved_entry_count')}/{row.get('added_reject_count')} | "
            f"{', '.join(fv_checks.get('blockers') or []) or 'none'} | "
            f"{', '.join(exec_checks.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Selected Forward Rows", ""])
    for row in report["summary"]:
        lines.extend([f"### {row['policy']}", ""])
        selected = row.get("selected_forward_rows") or []
        if not selected:
            lines.append("none")
            continue
        lines.append("| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|")
        for item in selected:
            lines.append(
                f"| {item.get('market')} | {item.get('ts_wall')} | {item.get('side')} | {item.get('source')} | "
                f"{item.get('market_observation_index')} | {fmt(item.get('seconds_to_close'))} | "
                f"{fmt(item.get('p_eff'))} | {fmt(item.get('raw_p') if item.get('raw_p') is not None else item.get('p_side'))} | {fmt(item.get('ask_prob'))} | "
                f"{fmt(item.get('eff_edge_prob'))} | {item.get('side_won')} | {fmt(item.get('net_gross_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
