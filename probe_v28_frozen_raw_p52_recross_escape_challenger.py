"""Frozen forward validator for raw p52 recross-escape challengers.

The recross-escape rule was derived after inspecting a fresh p52 loss cluster,
so previous rows are discovery evidence only. This gate starts at first run and
scores only clean future markets.
"""
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
from probe_v28_raw_p52_recross_escape_candidate import build_report as build_recross_report
from probe_v28_raw_p52_recross_escape_candidate import detail


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.md"

POLICIES = [
    {
        "policy": "v28_raw_p52_edge0_base",
        "role": "raw_p52_forward_baseline",
        "physics": "Same-window raw p52 baseline for the recross-escape challenger.",
    },
    {
        "policy": "p52_recross_escape_opp240_oppedge5_keep",
        "role": "coverage_preserving_recross_escape",
        "physics": "Raw p52 baseline, but weak near-strike/high-recross rows may follow a later opposite p52 confirmation only if that opposite has >=5pp executable edge. Otherwise keep raw p52 to preserve coverage.",
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
    payload = build_recross_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    base_rows = payload.get("base_rows") if isinstance(payload.get("base_rows"), list) else []
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    future_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    future_base_rows = [
        detail(row, "v28_raw_p52_edge0_base", "base", row)
        for row in base_rows
        if str(row.get("market") or "") in forward_markets
    ]
    denominator = len(forward_markets)
    floor = state.get("promotion_floor") or {}
    summary: list[dict[str, Any]] = []
    for item in state.get("policies") or POLICIES:
        policy = item["policy"]
        if policy == "v28_raw_p52_edge0_base":
            policy_rows = future_base_rows
        else:
            policy_rows = [row for row in future_rows if row.get("policy") == policy]
        s = summarize(policy, policy_rows, denominator)
        selected_markets = {str(row.get("market") or "") for row in policy_rows if row.get("market")}
        missed_markets = sorted(forward_markets - selected_markets)
        mode_counts: dict[str, int] = {}
        for row in policy_rows:
            mode = str(row.get("mode") or "unknown")
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        summary.append({
            **s,
            "role": item.get("role"),
            "physics": item.get("physics"),
            "mode_counts": mode_counts,
            "missed_forward_markets": missed_markets,
            "missed_forward_market_count": len(missed_markets),
            "selected_forward_rows": recross_selected_row_details(policy_rows),
            "fv_validation_checks": fv_validation_checks(s, floor),
            "execution_promotion_checks": promotion_checks(s, floor),
        })
    baseline = next((row for row in summary if row.get("policy") == "v28_raw_p52_edge0_base"), {})
    for row in summary:
        row["vs_raw_p52_base"] = compare(row, baseline)
    return {
        "freeze_ts": state["freeze_ts"],
        "forward_market_denominator": denominator,
        "forward_markets": sorted(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "post_freeze_observed_markets": sorted(timing["post_freeze_observed_markets"]),
        "future_candidate_rows": len(future_rows),
        "policies": state.get("policies") or POLICIES,
        "promotion_floor": floor,
        "summary": summary,
    }


def recross_selected_row_details(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details = selected_row_details(rows)
    by_key = {
        (str(row.get("market") or ""), str(row.get("side") or ""), str(row.get("ts_wall") or "")): row
        for row in rows
    }
    for item in details:
        source = by_key.get((str(item.get("market") or ""), str(item.get("side") or ""), str(item.get("ts_wall") or "")), {})
        item["mode"] = source.get("mode")
        item["base_side"] = source.get("base_side")
        item["base_p"] = source.get("base_p")
        item["base_edge"] = source.get("base_edge")
        item["delay_seconds"] = source.get("delay_seconds")
    return details


def compare(row: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
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


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Raw p52 Recross-Escape Challenger",
        "",
        "Forward-only validator. Rows before freeze timestamp do not count.",
        "",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Forward market denominator: `{report['forward_market_denominator']}`",
        f"- Future candidate rows: `{report['future_candidate_rows']}`",
        "",
        "## Forward Scorecard",
        "",
        "| policy | entries | settled | wins/losses | coverage | net c | brier | net vs raw | brier vs raw | modes | actual/shadow | FV blockers | execution blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|",
    ]
    for row in report["summary"]:
        fv_checks = row.get("fv_validation_checks") or {}
        exec_checks = row.get("execution_promotion_checks") or {}
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents_after_entry_fee'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt((row.get('vs_raw_p52_base') or {}).get('net_cents_delta'))} | "
            f"{fmt((row.get('vs_raw_p52_base') or {}).get('brier_delta'))} | {row.get('mode_counts')} | "
            f"{row.get('approved_entry_count')}/{row.get('added_reject_count')} | "
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
        lines.append("| market | ts | side | source | mode | stc | p_eff | ask | edge | won | net c |")
        lines.append("|---|---|---|---|---|---:|---:|---:|---:|---|---:|")
        for item in selected:
            lines.append(
                f"| {item.get('market')} | {item.get('ts_wall')} | {item.get('side')} | {item.get('source')} | "
                f"{item.get('mode')} | {fmt(item.get('seconds_to_close'))} | {fmt(item.get('p_eff'))} | "
                f"{fmt(item.get('ask_prob'))} | {fmt(item.get('eff_edge_prob'))} | {item.get('side_won')} | "
                f"{fmt(item.get('net_gross_cents_after_entry_fee'))} |"
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
