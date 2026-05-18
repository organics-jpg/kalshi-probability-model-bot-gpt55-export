"""Frozen forward validator for raw p52 early-NO boundary skip.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_p52_early_no_boundary_skip import BASE_POLICY, is_early_no_boundary_decay, summarize
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
MAX_SIM_SHARE = 0.35


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "candidate": "raw_p52_skip_early_no_boundary_decay",
        "base_policy": BASE_POLICY,
        "freeze_ts_utc": datetime.now(UTC).isoformat(),
        "rule": "Start from v28_raw_p52_edge0 and skip NO rows with stc>=720, p<0.70, abs_d<=0.45, recross>=0.55.",
        "physics": "Early NO near-boundary trades are exposed to BTC path churn; apparent NO edge may decay before close.",
        "source_artifact": "v28_raw_p52_early_no_boundary_skip_latest.json",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    settled = int(summary.get("settled") or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents"))
    entries = int(summary.get("entries") or 0)
    sim = int(summary.get("sim_count") or 0)
    sim_share = sim / entries if entries else None
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    elif coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if net is None or net <= 0.0:
        out.append("net_not_positive")
    if sim_share is None or sim_share > MAX_SIM_SHARE:
        out.append("simulated_share_gt_35pct")
    return out


def build_report() -> dict[str, Any]:
    state = ensure_state()
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    forward_markets = timing["clean_forward_markets"]
    source = build_raw_report()
    all_rows = source.get("rows") if isinstance(source.get("rows"), list) else []
    base = [
        row for row in all_rows
        if row.get("policy") == BASE_POLICY and str(row.get("market") or "") in forward_markets
    ]
    kept = [row for row in base if not is_early_no_boundary_decay(row)]
    skipped = [row for row in base if is_early_no_boundary_decay(row)]
    base_s = summarize(base, len(forward_markets))
    cand_s = summarize(kept, len(forward_markets))
    skip_s = summarize(skipped, len(forward_markets))
    cand_blockers = blockers(cand_s)
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "base": base_s,
        "candidate_summary": cand_s,
        "skipped_summary": skip_s,
        "delta_net_cents": cand_s["net_cents"] - base_s["net_cents"],
        "blockers": cand_blockers,
        "candidate_live_ready": not cand_blockers,
        "skipped_rows": skipped,
    }


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Raw p52 Early-NO Boundary Skip",
        "",
        "Future-only validator. No live orders.",
        "",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Delta vs base: `{fmt(report.get('delta_net_cents'))}c`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Summary",
        "",
        "| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg abs d | avg recross | net c | actual/sim |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["base", "candidate_summary", "skipped_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('avg_ask'))} | {fmt(row.get('avg_abs_d'))} | {fmt(row.get('avg_recross'))} | "
            f"{fmt(row.get('net_cents'))} | {row.get('actual_count')}/{row.get('sim_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
