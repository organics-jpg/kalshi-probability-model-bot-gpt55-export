"""Frozen future validator for p50/book-plus/edge-nonnegative entry lane.

Research-only; no live bot changes or orders.

This is the closest broad-coverage validation lane in the current runway:
`p50_book_plus_05_edge_nonnegative`. The diagnostic row has target coverage,
but too much rejected-actionable simulation. This validator freezes the exact
rule and scores only rows after its freeze timestamp.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from probe_v28_shadow_entry_policy_bakeoff import observation_pool


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.md"

POLICY = "p50_book_plus_05_edge_nonnegative"
MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
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


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state:
        return state
    state = {
        "candidate": POLICY,
        "freeze_ts_utc": datetime.now(UTC).isoformat(),
        "rule": "ask 1-90c, p_side >= 0.50, v28_minus_ask_prob >= 0.05, edge_cents >= 0",
        "physics": "Only trust v28 over book when raw FV clears the ask by at least 5pp and has nonnegative fee-aware edge; this tests whether book disagreement is usable as a broad entry filter.",
        "source": str(SOURCE_JSON),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def base_tradeable(row: dict[str, Any]) -> bool:
    ask = as_float(row.get("ask_cents"))
    return ask is not None and 1.0 <= ask <= 90.0


def policy_match(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    edge = as_float(row.get("edge_cents"))
    return (
        base_tradeable(row)
        and p_side is not None
        and p_side >= 0.50
        and delta is not None
        and delta >= 0.05
        and edge is not None
        and edge >= 0.0
    )


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None and as_float(row.get("gross_cents")) is not None


def first_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not policy_match(row):
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = row
    return [picked[market] for market in sorted(picked)]


def summarize(rows: list[dict[str, Any]], denominator_markets: int) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    gross_values = [float(row.get("gross_cents") or 0.0) for row in settled_rows]
    approved = sum(1 for row in rows if row.get("source") == "approved_entry")
    simulated = sum(1 for row in rows if row.get("source") == "rejected_actionable")
    coverage = (len({row.get("market") for row in rows if row.get("market")}) / denominator_markets * 100.0) if denominator_markets else 0.0
    sim_share = simulated / len(rows) if rows else None
    return {
        "entries": len(rows),
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
        "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
        "gross_cents": sum(gross_values),
        "avg_gross_cents": sum(gross_values) / len(gross_values) if gross_values else None,
        "approved_entry_count": approved,
        "simulated_or_rejected_count": simulated,
        "simulated_share": sim_share,
        "coverage_pct": coverage,
    }


def build_report() -> dict[str, Any]:
    state = ensure_state()
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    all_rows = observation_pool()
    future_rows = [
        row for row in all_rows
        if (parse_ts(row.get("ts_wall")) is not None and freeze_ts is not None and parse_ts(row.get("ts_wall")) > freeze_ts)
    ]
    denominator_markets = len({row.get("market") for row in future_rows if row.get("market")})
    candidate_rows = first_per_market(future_rows)
    summary = summarize(candidate_rows, denominator_markets)
    blockers = []
    if summary["settled"] < MIN_SETTLED:
        blockers.append("settled_lt_30")
    coverage = as_float(summary.get("coverage_pct"))
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    elif coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if as_float(summary.get("gross_cents")) is None or float(summary["gross_cents"]) <= 0:
        blockers.append("net_not_positive")
    sim_share = as_float(summary.get("simulated_share"))
    if sim_share is None or sim_share > MAX_SIMULATED_SHARE:
        blockers.append("simulated_share_gt_35pct")
    return {
        "freeze": state,
        "future_denominator_markets": denominator_markets,
        "summary": summary,
        "blockers": blockers,
        "candidate_live_ready": not blockers,
        "sample_markets": [row.get("market") for row in candidate_rows[:10]],
        "rows": candidate_rows,
        "interpretation": current_read(summary, blockers, denominator_markets),
    }


def current_read(summary: dict[str, Any], blockers: list[str], denominator: int) -> list[str]:
    return [
        f"Frozen {POLICY} has {summary.get('entries')} future entries across {denominator} future markets.",
        f"Settled/gross/coverage are {summary.get('settled')}/{summary.get('gross_cents')}c/{summary.get('coverage_pct')}%.",
        f"Approved/simulated rows are {summary.get('approved_entry_count')}/{summary.get('simulated_or_rejected_count')} with simulated share {summary.get('simulated_share')}.",
        f"Blockers: {', '.join(blockers) if blockers else 'none'}.",
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
    summary = report.get("summary") or {}
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen p50 Book-Edge Entry",
        "",
        "Future-only validator for the closest broad entry validation lane. No live orders.",
        "",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Freeze timestamp: `{freeze.get('freeze_ts_utc')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future denominator markets: `{report.get('future_denominator_markets')}`",
        f"- Entries/settled/W-L: `{summary.get('entries')}/{summary.get('settled')}/{summary.get('wins')}-{summary.get('losses')}`",
        f"- Gross cents / avg gross: `{fmt(summary.get('gross_cents'))}/{fmt(summary.get('avg_gross_cents'))}`",
        f"- Coverage: `{fmt(summary.get('coverage_pct'))}%`",
        f"- Approved/simulated/share: `{summary.get('approved_entry_count')}/{summary.get('simulated_or_rejected_count')}/{fmt(summary.get('simulated_share'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Sample Markets",
        "",
    ])
    for market in report.get("sample_markets") or []:
        lines.append(f"- `{market}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
