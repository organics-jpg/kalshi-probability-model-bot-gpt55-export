"""Sample runway for the active target-coverage v28 FV candidate.

Research-only; no live bot changes or orders.

The best current candidate is still blocked by small forward sample size. This
report makes the waiting problem concrete: how many more settled rows are
needed, which selected rows are pending, and how fragile the current 75-90%
coverage fit is as new markets arrive.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
VALIDATOR_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
PROMOTION_JSON = OUT_DIR / "v28_target_coverage_promotion_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_sample_runway_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_sample_runway_latest.md"

COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
MIN_SETTLED = 30


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


def coverage(entries: int, denominator: int) -> float | None:
    return entries / denominator * 100.0 if denominator > 0 else None


def max_additional_misses(entries: int, denominator: int, floor_pct: float) -> int:
    misses = 0
    while True:
        next_cov = coverage(entries, denominator + misses + 1)
        if next_cov is None or next_cov < floor_pct:
            return misses
        misses += 1


def max_additional_hits(entries: int, denominator: int, ceiling_pct: float) -> int:
    hits = 0
    while True:
        next_cov = coverage(entries + hits + 1, denominator + hits + 1)
        if next_cov is None or next_cov > ceiling_pct:
            return hits
        hits += 1


def build_report() -> dict[str, Any]:
    validator = load_json(VALIDATOR_JSON)
    seq = load_json(SEQ_JSON)
    promotion = load_json(PROMOTION_JSON)
    forward_rows = validator.get("forward_rows") if isinstance(validator.get("forward_rows"), list) else []
    best = {}
    for row in validator.get("forward") or []:
        if row.get("overlay") == seq.get("overlay"):
            best = row
            break
    if not best and isinstance(validator.get("forward"), list) and validator.get("forward"):
        best = validator["forward"][0]

    entries = int(as_float(best.get("entries")) or 0)
    settled = int(as_float(best.get("settled")) or 0)
    denominator = int(as_float(validator.get("forward_denominator")) or 0)
    pending = [row for row in forward_rows if row.get("side_won") is None]
    misses_before_low = max_additional_misses(entries, denominator, COVERAGE_MIN)
    hits_before_high = max_additional_hits(entries, denominator, COVERAGE_MAX)

    rows_to_30 = max(0, MIN_SETTLED - settled)
    current_coverage = coverage(entries, denominator)
    return {
        "policy": validator.get("policy"),
        "overlay": seq.get("overlay"),
        "freeze_ts": validator.get("freeze_ts"),
        "source_coverage_freeze_ts": validator.get("source_coverage_freeze_ts"),
        "forward_denominator": denominator,
        "entries": entries,
        "settled": settled,
        "pending": len(pending),
        "coverage_pct": current_coverage,
        "coverage_band": [COVERAGE_MIN, COVERAGE_MAX],
        "settled_rows_to_30": rows_to_30,
        "coverage_runway": {
            "max_consecutive_future_misses_before_below_75": misses_before_low,
            "coverage_after_that_many_misses": coverage(entries, denominator + misses_before_low),
            "coverage_after_one_more_miss": coverage(entries, denominator + misses_before_low + 1),
            "max_consecutive_future_entries_before_above_90": hits_before_high,
            "coverage_after_that_many_entries": coverage(entries + hits_before_high, denominator + hits_before_high),
            "coverage_after_one_more_entry": coverage(entries + hits_before_high + 1, denominator + hits_before_high + 1),
        },
        "pending_rows": pending,
        "promotion_ready": promotion.get("ready_for_promotion_review"),
        "promotion_remaining": promotion.get("remaining") or {},
        "interpretation": [
            "The target-coverage candidate is currently inside the 75-90% band but sample size is still the hard blocker.",
            "Because the denominator is small, one or two new missed markets can materially change coverage.",
            "Coverage movement should be monitored, but probability promotion remains blocked until settled rows reach 30.",
        ],
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
    runway = report.get("coverage_runway") or {}
    lines = [
        "# v28 Target-Coverage Sample Runway",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Entries/settled/pending/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('pending')}/{report.get('forward_denominator')}`",
        f"- Coverage: `{fmt(report.get('coverage_pct'))}` within `{report.get('coverage_band')}`",
        f"- Settled rows to 30: `{report.get('settled_rows_to_30')}`",
        f"- Promotion ready: `{report.get('promotion_ready')}`",
        "",
        "## Coverage Runway",
        "",
        f"- Max consecutive future missed markets before dropping below 75%: `{runway.get('max_consecutive_future_misses_before_below_75')}`",
        f"- Coverage after that many misses / one more miss: `{fmt(runway.get('coverage_after_that_many_misses'))}` / `{fmt(runway.get('coverage_after_one_more_miss'))}`",
        f"- Max consecutive future selected markets before rising above 90%: `{runway.get('max_consecutive_future_entries_before_above_90')}`",
        f"- Coverage after that many entries / one more entry: `{fmt(runway.get('coverage_after_that_many_entries'))}` / `{fmt(runway.get('coverage_after_one_more_entry'))}`",
        "",
        "## Pending Selected Rows",
        "",
        "| market | side | p raw | ask | edge | stc | reason |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report.get("pending_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {row.get('coverage_valve_reason')} |"
        )
    if not report.get("pending_rows"):
        lines.append("| none |  |  |  |  |  |  |")
    lines.extend(["", "## Interpretation", ""])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
