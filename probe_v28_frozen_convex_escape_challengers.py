"""Frozen forward gate for convex raw-escape candidates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_convex_raw_escape_candidate import build_report as build_convex_report
from probe_v28_frozen_forward_candidates import fmt, fv_validation_checks, market_timing, parse_ts, promotion_checks, summarize
from probe_v28_frozen_forward_candidates import selected_row_details


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_convex_escape_challengers_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_convex_escape_challengers_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_convex_escape_challengers_latest.md"

CHALLENGERS = [
    {
        "policy": "raw_edge20_else_first_side_raw_later_book_p60_edge0",
        "role": "convex_raw_escape_first_side_wait",
        "physics": "Use raw p50 only when raw edge is at least 20pp; otherwise use first-side p60 forgetting.",
    },
    {
        "policy": "raw_edge20_else_rmt_repetition_forget_p60_edge0",
        "role": "convex_raw_escape_rmt_wait",
        "physics": "Use raw p50 only when raw edge is at least 20pp; otherwise use RMT repetition p60 forgetting.",
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
        "policies": CHALLENGERS,
        "promotion_floor": {
            "min_settled": 30,
            "max_simulated_share": 0.35,
            "required_coverage_pct_min": 70.0,
            "required_coverage_pct_max": 90.0,
            "must_be_net_positive": True,
        },
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def normalize_policy(row: dict[str, Any]) -> str:
    return str(row.get("meta_policy") or row.get("policy") or "")


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    payload = build_convex_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    future_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    floor = state.get("promotion_floor") or {}
    summary: list[dict[str, Any]] = []
    for item in state.get("policies") or CHALLENGERS:
        policy = item["policy"]
        policy_rows = [{**row, "policy": policy} for row in future_rows if normalize_policy(row) == policy]
        s = summarize(policy, policy_rows, len(forward_markets))
        selected_markets = {str(row.get("market") or "") for row in policy_rows if row.get("market")}
        summary.append({
            **s,
            "role": item.get("role"),
            "missed_forward_market_count": len(forward_markets - selected_markets),
            "missed_forward_markets": sorted(forward_markets - selected_markets),
            "selected_forward_rows": selected_row_details(policy_rows),
            "raw_high_convex_edge": sum(1 for row in policy_rows if row.get("selection_reason") == "raw_high_convex_edge"),
            "use_wait_policy": sum(1 for row in policy_rows if row.get("selection_reason") == "use_wait_policy"),
            "fv_validation_checks": fv_validation_checks(s, floor),
            "execution_promotion_checks": promotion_checks(s, floor),
        })
    return {
        "freeze_ts": state["freeze_ts"],
        "forward_market_denominator": len(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "future_candidate_rows": len(future_rows),
        "policies": state.get("policies") or CHALLENGERS,
        "summary": summary,
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Convex Raw-Escape Challengers",
        "",
        "Rows before this freeze do not count. These candidates were created after the first raw-convexity frozen win.",
        "",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Forward market denominator: `{report['forward_market_denominator']}`",
        f"- Excluded in-progress post-freeze markets: `{len(report['excluded_in_progress_markets'])}`",
        f"- Future candidate rows: `{report['future_candidate_rows']}`",
        "",
        "## Forward Scorecard",
        "",
        "| policy | entries | settled | wins/losses | coverage | net c | avg brier | raw escape | wait | actual/shadow | FV blockers | execution blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["summary"]:
        fv_checks = row.get("fv_validation_checks") or {}
        exec_checks = row.get("execution_promotion_checks") or {}
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_brier'])} | "
            f"{row.get('raw_high_convex_edge')} | {row.get('use_wait_policy')} | "
            f"{row['approved_entry_count']}/{row['added_reject_count']} | "
            f"{', '.join(fv_checks.get('blockers') or []) or 'none'} | "
            f"{', '.join(exec_checks.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Missed Forward Markets", ""])
    for row in report["summary"]:
        lines.append(f"- `{row['policy']}` missed `{row['missed_forward_market_count']}`: {', '.join(row.get('missed_forward_markets') or []) or 'none'}")
    lines.extend(["", "## Selected Forward Rows", ""])
    for row in report["summary"]:
        lines.append(f"### {row['policy']}")
        selected = row.get("selected_forward_rows") or []
        if not selected:
            lines.append("none")
            continue
        lines.append("| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|")
        for item in selected[-10:]:
            lines.append(
                f"| {item.get('market')} | {item.get('ts_wall')} | {item.get('side')} | {item.get('source')} | "
                f"{fmt(item.get('market_observation_index'))} | {fmt(item.get('seconds_to_close'))} | "
                f"{fmt(item.get('p_eff'))} | {fmt(item.get('p_side'))} | {fmt(item.get('ask_prob'))} | "
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
