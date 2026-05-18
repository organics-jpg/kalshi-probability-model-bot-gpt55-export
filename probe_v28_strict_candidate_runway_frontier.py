"""Strict-forward runway frontier for v28 candidates.

Research-only; no live bot changes or orders.

This report ranks strict-forward positive candidates by how many future clean
approved full-win rows they would need to clear the broad live-test gates. It
is intentionally a runway estimate, not promotion evidence.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_strict_candidate_runway_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_strict_candidate_runway_frontier_latest.md"

TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_CUSHION_CENTS = 300.0


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ceil_nonnegative(value: float) -> int:
    return int(max(0, math.ceil(value)))


def coverage_denominator(entries: float, coverage_pct: float | None) -> float | None:
    if coverage_pct is None or coverage_pct <= 0:
        return None
    return entries / (coverage_pct / 100.0)


def clean_rows_for_coverage(entries: float, denom: float | None) -> int | None:
    if denom is None:
        return None
    if denom <= 0:
        return 0
    current = entries / denom
    if current >= TARGET_COVERAGE_MIN / 100.0:
        return 0
    # Assume each future clean selected market increments both numerator and
    # denominator. This is an optimistic runway bound, not proof.
    target = TARGET_COVERAGE_MIN / 100.0
    if target >= 1.0:
        return None
    return ceil_nonnegative((target * denom - entries) / (1.0 - target))


def clean_rows_for_source(sim_share: float | None, entries: float) -> int | None:
    if sim_share is None:
        return None
    if sim_share <= MAX_RECON_SHARE:
        return 0
    reconstructed = sim_share * entries
    return ceil_nonnegative((reconstructed / MAX_RECON_SHARE) - entries)


def score_row(row: dict[str, Any], live_cents: float) -> dict[str, Any] | None:
    if row.get("strict_forward") is not True:
        return None
    net = fnum(row.get("net_cents_after_entry_fee"), -999999.0)
    if net <= 0:
        return None
    entries = fnum(row.get("entries"))
    settled = fnum(row.get("settled"))
    coverage = None if row.get("coverage_pct") in (None, "") else fnum(row.get("coverage_pct"))
    denom = coverage_denominator(entries, coverage)
    sim_share = None if row.get("simulated_share") in (None, "") else fnum(row.get("simulated_share"))
    rows_for_settled = ceil_nonnegative(MIN_SETTLED - settled)
    rows_for_live = ceil_nonnegative((live_cents - net) / 100.0)
    rows_for_cushion = ceil_nonnegative((MIN_CUSHION_CENTS - net) / 100.0)
    rows_for_coverage = clean_rows_for_coverage(entries, denom)
    rows_for_source = clean_rows_for_source(sim_share, entries)
    needs = {
        "settled": rows_for_settled,
        "live_baseline": rows_for_live,
        "cushion": rows_for_cushion,
        "coverage": rows_for_coverage,
        "source": rows_for_source,
    }
    known_needs = [value for value in needs.values() if value is not None]
    optimistic_clean_win_rows_needed = max(known_needs) if known_needs else None
    blockers = list(row.get("blockers") or [])
    hard_unknowns = [key for key, value in needs.items() if value is None]
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_above_broad_target")
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": entries,
        "settled": settled,
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": coverage,
        "coverage_denom_est": denom,
        "net_cents": net,
        "delta_vs_live_cents": net - live_cents,
        "simulated_share": sim_share,
        "full_loss_cushion_estimate": row.get("full_loss_cushion_estimate"),
        "reported_blockers": row.get("blockers") or [],
        "runway_needs_clean_full_wins": needs,
        "optimistic_clean_win_rows_needed": optimistic_clean_win_rows_needed,
        "hard_unknowns": hard_unknowns,
        "live_ready": bool(row.get("live_ready")),
    }


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    live = load_json(LIVE_SUMMARY_JSON)
    live_cents = 100.0 * fnum(live.get("net_pnl_total_dollars"))
    rows = []
    for row in tracker.get("rows") or []:
        if isinstance(row, dict):
            scored = score_row(row, live_cents)
            if scored:
                rows.append(scored)
    rows.sort(
        key=lambda row: (
            9999 if row.get("optimistic_clean_win_rows_needed") is None else int(row["optimistic_clean_win_rows_needed"]),
            -float(row.get("net_cents") or -999999),
            abs(float(row.get("coverage_pct") or 75.0) - 75.0),
        )
    )
    broadish = [
        row for row in rows
        if row.get("coverage_pct") is not None and 60.0 <= float(row.get("coverage_pct") or 0.0) <= TARGET_COVERAGE_MAX
    ]
    return {
        "generated_from": {
            "tracker": str(TRACKER_JSON),
            "live_summary": str(LIVE_SUMMARY_JSON),
        },
        "live_baseline_cents": live_cents,
        "strict_positive_rows": len(rows),
        "broadish_rows": len(broadish),
        "top_runway": rows[:80],
        "top_broadish_runway": broadish[:80],
        "interpretation": [
            "Research-only optimistic runway estimate; no live bot changes or orders.",
            "Rows needed assume future selected rows are clean approved full wins worth +100c each, so this is a best-case bound.",
            "If a lane still needs many perfect wins, it needs a new mechanism rather than passive maturation.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Strict Candidate Runway Frontier",
        "",
        "Research-only optimistic runway estimate. No live bot changes or orders.",
        "",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        f"- Strict positive rows: `{report.get('strict_positive_rows')}`",
        f"- Broad-ish strict positive rows: `{report.get('broadish_rows')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Top Broad-ish Strict Runway",
            "",
            "| rank | gate | policy | settled | W/L | coverage | net | delta live | recon | clean wins needed | needs | blockers |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for idx, row in enumerate(report.get("top_broadish_runway") or [], start=1):
        needs = row.get("runway_needs_clean_full_wins") or {}
        lines.append(
            f"| {idx} | `{row.get('gate')}` | `{row.get('policy')}` | {fmt(row.get('settled'))} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))}% | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
            f"{fmt(row.get('simulated_share'))} | {fmt(row.get('optimistic_clean_win_rows_needed'))} | "
            f"{needs} | {', '.join(row.get('reported_blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
