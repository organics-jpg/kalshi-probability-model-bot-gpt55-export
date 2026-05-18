"""Frozen forward validator for raw p52 book-shrink entry.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_p52_book_shrink_entry import build_report as build_shrink_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_latest.md"

FROZEN_POLICY = "gap15_book50_p52_edge0"
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
        "candidate": FROZEN_POLICY,
        "base_policy": "v28_raw_p52_edge0",
        "freeze_ts_utc": datetime.now(UTC).isoformat(),
        "rule": "If raw p - executable ask > 15pp, blend 50% toward executable ask; then require p>=0.52 and edge>=0.",
        "physics": "Large model-book disagreement is treated as path-risk overconfidence, but the response is probabilistic shrinkage rather than a hard skip.",
        "source_artifact": "v28_raw_p52_book_shrink_entry_latest.json",
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


def summarize_rows(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    wins = sum(1 for row in settled if row.get("side_won") is True)
    losses = sum(1 for row in settled if row.get("side_won") is False)
    net = sum(
        float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0)
        for row in rows
        if row.get("gross_cents") is not None
    )
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
        if row.get("p_eff") is not None
    ]
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "shrunk_count": sum(1 for row in rows if row.get("shrunk") is True),
        "actual_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "sim_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


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
    source = build_shrink_report()
    rows = source.get("rows") if isinstance(source.get("rows"), list) else []
    base_rows = [
        row for row in rows
        if row.get("policy") == "raw_probability_p52_edge0" and str(row.get("market") or "") in forward_markets
    ]
    candidate_rows = [
        row for row in rows
        if row.get("policy") == FROZEN_POLICY and str(row.get("market") or "") in forward_markets
    ]
    base_summary = summarize_rows(base_rows, len(forward_markets))
    candidate_summary = summarize_rows(candidate_rows, len(forward_markets))
    cand_blockers = blockers(candidate_summary)
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "base": base_summary,
        "candidate_summary": candidate_summary,
        "delta_net_cents": candidate_summary["net_cents"] - base_summary["net_cents"],
        "blockers": cand_blockers,
        "candidate_live_ready": not cand_blockers,
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
        "# v28 Frozen Raw p52 Book-Shrink Entry",
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
        "| row | entries | settled | W/L | coverage | net c | avg brier | shrunk | actual/sim |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["base", "candidate_summary"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_brier'))} | "
            f"{row.get('shrunk_count')} | {row.get('actual_count')}/{row.get('sim_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
