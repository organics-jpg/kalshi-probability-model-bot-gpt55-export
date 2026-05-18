"""Frozen-only robustness audit for v28 danger-zone candidates.

Research-only; no live bot changes or orders.

The discovery danger-zone audit passes leave-one-market checks, but promotion
evidence must use only rows after the frozen validator timestamp. This script
checks whether the frozen future entry valve and danger-to-book FV lift survive
leave-one-market stress on that post-freeze slice.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_approved_entry_state_valves import raw_prob, sorted_rows, with_state
from probe_v28_frozen_danger_zone_entry_valve import keep_valve
from probe_v28_frozen_danger_zone_fv_calibration import (
    STATE_JSON as FV_STATE_JSON,
    danger_to_book,
    danger_zone,
    parse_ts,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ENTRY_STATE_JSON = OUT_DIR / "v28_frozen_danger_zone_entry_valve_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_danger_zone_robustness_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_danger_zone_robustness_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def future_rows() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    fv_state = load_json(FV_STATE_JSON)
    entry_state = load_json(ENTRY_STATE_JSON)
    freeze_ts = parse_ts(fv_state.get("freeze_ts_utc") or entry_state.get("freeze_ts_utc"))
    rows = [
        row for row in with_state(sorted_rows())
        if parse_ts(row.get("entry_ts")) >= freeze_ts
    ]
    return fv_state, entry_state, rows


def entry_delta(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if keep_valve(row)]
    skipped = [row for row in rows if not keep_valve(row)]
    control_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    candidate_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in selected)
    return {
        "rows": len(rows),
        "selected": len(selected),
        "skipped": len(skipped),
        "control_gross_cents": control_gross,
        "candidate_gross_cents": candidate_gross,
        "delta_cents": candidate_gross - control_gross,
        "skipped_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in skipped),
    }


def fv_delta(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw_briers: list[float] = []
    danger_briers: list[float] = []
    raw_losses: list[float] = []
    danger_losses: list[float] = []
    adjusted = 0
    for row in rows:
        raw = raw_prob(row)
        danger_p = danger_to_book(row)
        if raw is None or danger_p is None:
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        raw = clamp_prob(float(raw))
        danger_p = clamp_prob(float(danger_p))
        if abs(raw - danger_p) > 1e-12:
            adjusted += 1
        raw_briers.append((raw - outcome) ** 2)
        danger_briers.append((danger_p - outcome) ** 2)
        raw_losses.append(logloss(raw, outcome))
        danger_losses.append(logloss(danger_p, outcome))
    raw_brier = avg(raw_briers)
    danger_brier = avg(danger_briers)
    raw_loss = avg(raw_losses)
    danger_loss = avg(danger_losses)
    return {
        "rows": len(raw_briers),
        "danger_rows": sum(1 for row in rows if danger_zone(row)),
        "adjusted_rows": adjusted,
        "brier_delta_vs_raw": None if raw_brier is None or danger_brier is None else danger_brier - raw_brier,
        "logloss_delta_vs_raw": None if raw_loss is None or danger_loss is None else danger_loss - raw_loss,
    }


def build_report() -> dict[str, Any]:
    fv_state, entry_state, rows = future_rows()
    markets = sorted({str(row.get("market") or "") for row in rows})
    full_entry = entry_delta(rows)
    full_fv = fv_delta(rows)
    leave_one = []
    for market in markets:
        removed = [row for row in rows if str(row.get("market") or "") == market]
        subset = [row for row in rows if str(row.get("market") or "") != market]
        e = entry_delta(subset)
        f = fv_delta(subset)
        leave_one.append({
            "removed_market": market,
            "removed_rows": len(removed),
            "removed_danger_rows": sum(1 for row in removed if danger_zone(row)),
            "removed_candidate_skips": sum(1 for row in removed if not keep_valve(row)),
            "removed_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in removed),
            "entry_delta_cents": e.get("delta_cents"),
            "fv_adjusted_rows": f.get("adjusted_rows"),
            "fv_brier_delta_vs_raw": f.get("brier_delta_vs_raw"),
            "fv_logloss_delta_vs_raw": f.get("logloss_delta_vs_raw"),
        })
    entry_failures = [row for row in leave_one if float(row.get("entry_delta_cents") or 0.0) <= 0.0]
    fv_failures = [
        row for row in leave_one
        if row.get("fv_brier_delta_vs_raw") is None or float(row.get("fv_brier_delta_vs_raw") or 0.0) >= 0.0
    ]
    blockers: list[str] = []
    if len(rows) < 30:
        blockers.append("rows_lt_30")
    if full_fv.get("adjusted_rows", 0) < 5:
        blockers.append("adjusted_rows_lt_5")
    if entry_failures:
        blockers.append("entry_leave_one_failure")
    if fv_failures:
        blockers.append("fv_leave_one_failure")
    leave_one.sort(key=lambda row: (float(row.get("entry_delta_cents") or 0.0), float(row.get("fv_brier_delta_vs_raw") or 0.0)))
    return {
        "surface": "actual_v28_approved_entries_only",
        "freeze": fv_state,
        "fv_freeze": fv_state,
        "entry_freeze": entry_state,
        "future_rows": len(rows),
        "future_markets": len(markets),
        "full_entry": full_entry,
        "full_fv": full_fv,
        "entry_leave_one_failures": len(entry_failures),
        "fv_leave_one_failures": len(fv_failures),
        "blockers": blockers,
        "promotion_ready": not blockers,
        "leave_one": leave_one,
        "rows": leave_one,
        "interpretation": current_read(full_entry, full_fv, entry_failures, fv_failures, blockers),
    }


def current_read(
    full_entry: dict[str, Any],
    full_fv: dict[str, Any],
    entry_failures: list[dict[str, Any]],
    fv_failures: list[dict[str, Any]],
    blockers: list[str],
) -> list[str]:
    return [
        f"Frozen entry valve delta is {full_entry.get('delta_cents')}c with {full_entry.get('skipped')} skipped future entries.",
        f"Frozen danger-to-book FV Brier/logloss deltas are {full_fv.get('brier_delta_vs_raw')}/{full_fv.get('logloss_delta_vs_raw')} over {full_fv.get('rows')} rows and {full_fv.get('adjusted_rows')} adjusted rows.",
        f"Leave-one failures entry/FV: {len(entry_failures)}/{len(fv_failures)}.",
        f"Promotion blockers: {', '.join(blockers) or 'none'}.",
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
    entry = report.get("full_entry") or {}
    fv = report.get("full_fv") or {}
    lines = [
        "# v28 Frozen Danger-Zone Robustness",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- FV freeze timestamp UTC: `{(report.get('fv_freeze') or {}).get('freeze_ts_utc')}`",
        f"- Future rows/markets: `{report.get('future_rows')}/{report.get('future_markets')}`",
        f"- Promotion ready: `{report.get('promotion_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Full Future Sample",
        "",
        f"- Entry selected/skipped/control/candidate/delta: `{entry.get('selected')}/{entry.get('skipped')}/{fmt(entry.get('control_gross_cents'))}c/{fmt(entry.get('candidate_gross_cents'))}c/{fmt(entry.get('delta_cents'))}c`",
        f"- FV rows/danger/adjusted: `{fv.get('rows')}/{fv.get('danger_rows')}/{fv.get('adjusted_rows')}`",
        f"- FV Brier/logloss delta: `{fmt(fv.get('brier_delta_vs_raw'))}/{fmt(fv.get('logloss_delta_vs_raw'))}`",
        "",
        "## Worst Leave-One-Market Rows",
        "",
        "| removed market | removed rows | danger | skips | removed gross c | entry delta c | fv adjusted | fv d brier | fv d logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in (report.get("leave_one") or [])[:12]:
        lines.append(
            f"| `{row.get('removed_market')}` | {row.get('removed_rows')} | {row.get('removed_danger_rows')} | "
            f"{row.get('removed_candidate_skips')} | {fmt(row.get('removed_gross_cents'))} | "
            f"{fmt(row.get('entry_delta_cents'))} | {row.get('fv_adjusted_rows')} | "
            f"{fmt(row.get('fv_brier_delta_vs_raw'))} | {fmt(row.get('fv_logloss_delta_vs_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
