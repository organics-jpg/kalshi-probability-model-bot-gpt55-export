"""Frozen broad target-coverage validator for the book-edge overconfidence gate.

Research-only; no live bot changes or orders.

The actual-approved book-edge discovery suggested that very large raw-v28 edge
over the executable ask can be overconfidence, not free value. This validator
tests that same fixed rule on the broad target-coverage entry surface with only
future rows after its own freeze timestamp.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_COVERAGE_FV_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_target_coverage_book_edge_gate_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_target_coverage_book_edge_gate_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_target_coverage_book_edge_gate_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    target = load_json(TARGET_COVERAGE_FV_JSON)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "target_coverage_skip_raw_edge_ge_15pp",
        "entry_surface": "frozen_target_coverage_raw_entry_valve",
        "base_policy": target.get("policy") or DEFAULT_POLICY,
        "rule": "Start from the target-coverage policy and skip rows where raw_probability - ask_probability >= 0.15.",
        "physics": (
            "If raw v28 claims a very large edge but the executable ask is far lower, this can be a false-conviction "
            "state where the model is treating noisy boundary/path geometry as certainty."
        ),
        "source_discovery": "v28_approved_entry_book_edge_actionability_latest",
        "min_settled": MIN_SETTLED,
        "coverage_floor": COVERAGE_MIN,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ask_probability(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def raw_probability(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def raw_edge(row: dict[str, Any]) -> float | None:
    raw = raw_probability(row)
    ask = ask_probability(row)
    if raw is None or ask is None:
        return None
    return raw - ask


def should_skip(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    return edge is not None and edge >= 0.15


def future_target_rows(state: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    freeze_dt = parse_ts(str(state["freeze_ts_utc"]))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    rows = apply_policy(selected_base_rows(), str(state["base_policy"]))
    out = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in forward_markets:
            continue
        out.append({
            **row,
            "ask_prob": ask_probability(row),
            "raw_probability": raw_probability(row),
            "raw_edge_prob": raw_edge(row),
        })
    return out, len(forward_markets)


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    wins = sum(1 for row in settled if row.get("side_won") is True)
    losses = sum(1 for row in settled if row.get("side_won") is False)
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "coverage_pct": None if denominator <= 0 else 100.0 * len(rows) / denominator,
        "net_cents": net,
        "avg_net_cents": None if not settled else net / len(settled),
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "ask_prob": row.get("ask_prob"),
        "raw_probability": row.get("raw_probability"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    target, denominator = future_target_rows(state)
    skipped = [row for row in target if should_skip(row)]
    candidate = [row for row in target if not should_skip(row)]
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    skipped_summary = summarize(skipped, denominator)
    target_net = as_float(target_summary.get("net_cents")) or 0.0
    candidate_net = as_float(candidate_summary.get("net_cents")) or 0.0
    delta = candidate_net - target_net
    coverage = as_float(candidate_summary.get("coverage_pct"))
    settled = int(as_float(candidate_summary.get("settled")) or 0)
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if delta <= 0.0:
        blockers.append("delta_not_positive")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "target_summary": target_summary,
        "candidate_summary": candidate_summary,
        "skipped_summary": skipped_summary,
        "delta_vs_target_cents": delta,
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "skipped_rows": [compact(row) for row in skipped],
        "interpretation": [
            f"Frozen target-coverage book-edge gate has denominator {denominator}, candidate entries/settled {candidate_summary.get('entries')}/{candidate_summary.get('settled')}.",
            f"Coverage {candidate_summary.get('coverage_pct')}%; candidate net {candidate_net}c versus target {target_net}c; delta {delta}c.",
            f"Skipped rows were {skipped_summary.get('wins')}/{skipped_summary.get('losses')} for {skipped_summary.get('net_cents')}c.",
            f"Promotion blockers: {', '.join(blockers) if blockers else 'none'}.",
            "This is broad shadow validation only; no live bot code or order behavior changed.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Target-Coverage Book-Edge Gate",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Base policy: `{freeze.get('base_policy')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Scorecard",
        "",
        "| surface | entries | settled | W/L | coverage | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for key in ["target_summary", "candidate_summary", "skipped_summary"]:
        row = report.get(key) or {}
        lines.append(
            f"| {key} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend(["", "## Skipped Rows", "", "| market | source | side | won | net c | raw | ask | edge | stc | recross | abs d |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_probability'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
