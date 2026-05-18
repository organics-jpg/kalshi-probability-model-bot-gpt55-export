"""Robustness audit for v28 danger-zone entry/FV candidates.

Research-only; no live bot changes or orders.

The danger-zone idea is physically plausible, but the sample is small. This
audit removes one market at a time and checks whether the entry-valve P&L lift
and danger-to-book FV calibration improvement survive.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_approved_entry_state_valves import book_prob, raw_book_gap, raw_prob, sorted_rows, with_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_danger_zone_robustness_audit_latest.json"
OUT_MD = OUT_DIR / "v28_danger_zone_robustness_audit_latest.md"


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def is_same_side_reentry(row: dict[str, Any]) -> bool:
    return int(row.get("market_side_entry_index") or 0) > 0


def danger_zone(row: dict[str, Any]) -> bool:
    gap = raw_book_gap(row)
    if gap is None:
        return False
    return gap > 0.30 or (is_same_side_reentry(row) and gap > 0.15)


def keep_entry(row: dict[str, Any]) -> bool:
    return not danger_zone(row)


def danger_to_book_p(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    if raw is None:
        return None
    return book if danger_zone(row) and book is not None else raw


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def entry_delta(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if keep_entry(row)]
    skipped = [row for row in rows if not keep_entry(row)]
    control_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    candidate_gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in selected)
    return {
        "control_gross_cents": control_gross,
        "candidate_gross_cents": candidate_gross,
        "delta_cents": candidate_gross - control_gross,
        "selected": len(selected),
        "skipped": len(skipped),
        "skipped_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in skipped),
    }


def fv_delta(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw_briers: list[float] = []
    danger_briers: list[float] = []
    raw_losses: list[float] = []
    danger_losses: list[float] = []
    for row in rows:
        raw = raw_prob(row)
        danger_p = danger_to_book_p(row)
        if raw is None or danger_p is None:
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        raw = clamp_prob(float(raw))
        danger_p = clamp_prob(float(danger_p))
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
        "brier_delta_vs_raw": None if raw_brier is None or danger_brier is None else danger_brier - raw_brier,
        "logloss_delta_vs_raw": None if raw_loss is None or danger_loss is None else danger_loss - raw_loss,
    }


def build_report() -> dict[str, Any]:
    rows = with_state(sorted_rows())
    markets = sorted({str(row.get("market") or "") for row in rows})
    full_entry = entry_delta(rows)
    full_fv = fv_delta(rows)
    leave_one = []
    for market in markets:
        subset = [row for row in rows if str(row.get("market") or "") != market]
        e = entry_delta(subset)
        f = fv_delta(subset)
        removed = [row for row in rows if str(row.get("market") or "") == market]
        leave_one.append({
            "removed_market": market,
            "removed_rows": len(removed),
            "removed_danger_rows": sum(1 for row in removed if danger_zone(row)),
            "removed_danger_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in removed if danger_zone(row)),
            "entry_delta_cents": e.get("delta_cents"),
            "fv_brier_delta_vs_raw": f.get("brier_delta_vs_raw"),
            "fv_logloss_delta_vs_raw": f.get("logloss_delta_vs_raw"),
        })
    entry_failures = [row for row in leave_one if float(row.get("entry_delta_cents") or 0.0) <= 0.0]
    fv_failures = [
        row for row in leave_one
        if row.get("fv_brier_delta_vs_raw") is None or float(row.get("fv_brier_delta_vs_raw") or 0.0) >= 0.0
    ]
    leave_one.sort(key=lambda row: float(row.get("entry_delta_cents") or 0.0))
    return {
        "surface": "actual_v28_approved_entries_only",
        "rows": len(rows),
        "markets": len(markets),
        "full_entry": full_entry,
        "full_fv": full_fv,
        "entry_leave_one_failures": len(entry_failures),
        "fv_leave_one_failures": len(fv_failures),
        "pass_entry_robustness": not entry_failures,
        "pass_fv_robustness": not fv_failures,
        "leave_one": leave_one,
        "interpretation": current_read(full_entry, full_fv, entry_failures, fv_failures),
    }


def current_read(
    full_entry: dict[str, Any],
    full_fv: dict[str, Any],
    entry_failures: list[dict[str, Any]],
    fv_failures: list[dict[str, Any]],
) -> list[str]:
    return [
        f"Full entry valve delta is {full_entry.get('delta_cents')}c; leave-one-market entry failures: {len(entry_failures)}.",
        f"Full danger-to-book FV Brier/logloss deltas are {full_fv.get('brier_delta_vs_raw')}/{full_fv.get('logloss_delta_vs_raw')}; leave-one-market FV failures: {len(fv_failures)}.",
        "If entry robustness fails, treat the entry valve as a watched hypothesis, not a promotion candidate.",
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
        "# v28 Danger-Zone Robustness Audit",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Rows/markets: `{report.get('rows')}/{report.get('markets')}`",
        f"- Entry robustness pass: `{report.get('pass_entry_robustness')}`",
        f"- FV robustness pass: `{report.get('pass_fv_robustness')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Full Sample",
        "",
        f"- Entry control/candidate/delta: `{fmt(entry.get('control_gross_cents'))}c/{fmt(entry.get('candidate_gross_cents'))}c/{fmt(entry.get('delta_cents'))}c`",
        f"- FV rows/danger rows: `{fv.get('rows')}/{fv.get('danger_rows')}`",
        f"- FV Brier/logloss delta: `{fmt(fv.get('brier_delta_vs_raw'))}/{fmt(fv.get('logloss_delta_vs_raw'))}`",
        "",
        "## Worst Leave-One-Market Rows",
        "",
        "| removed market | removed rows | removed danger | removed danger gross c | entry delta c | fv d brier | fv d logloss |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in (report.get("leave_one") or [])[:10]:
        lines.append(
            f"| `{row.get('removed_market')}` | {row.get('removed_rows')} | {row.get('removed_danger_rows')} | "
            f"{fmt(row.get('removed_danger_gross_cents'))} | {fmt(row.get('entry_delta_cents'))} | "
            f"{fmt(row.get('fv_brier_delta_vs_raw'))} | {fmt(row.get('fv_logloss_delta_vs_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
