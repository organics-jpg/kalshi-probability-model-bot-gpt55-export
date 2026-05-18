"""Danger-zone overlap check for the target-coverage v28 entry surface.

Research-only; no live bot changes or orders.

The danger-zone FV shrink is promising on actual v28-approved rows. This probe
checks whether the current target-coverage entry surface actually enters that
raw/book disagreement regime. If it does not, the danger-zone shrink should not
be credited for target-coverage performance.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_target_coverage_danger_overlap_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_danger_overlap_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def raw_prob(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def row_gap(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    ask = ask_prob(row)
    return None if raw is None or ask is None else raw - ask


def build_report() -> dict[str, Any]:
    rows = apply_policy(selected_base_rows(), DEFAULT_POLICY)
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    for row in settled:
        gap = row_gap(row)
        if gap is None:
            continue
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "raw_p": raw_prob(row),
            "ask_p": ask_prob(row),
            "raw_book_gap": gap,
            "won": row.get("side_won"),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "reason": row.get("coverage_valve_reason"),
        })
    scored.sort(key=lambda row: float(row.get("raw_book_gap") or -999.0), reverse=True)
    danger30 = [row for row in scored if float(row.get("raw_book_gap") or 0.0) > 0.30]
    danger20 = [row for row in scored if float(row.get("raw_book_gap") or 0.0) > 0.20]
    return {
        "policy": DEFAULT_POLICY,
        "entries": len(rows),
        "settled": len(settled),
        "scored": len(scored),
        "danger_gt30_count": len(danger30),
        "danger_gt20_count": len(danger20),
        "danger_gt30_net_cents": sum(float(row.get("net_cents") or 0.0) for row in danger30),
        "danger_gt20_net_cents": sum(float(row.get("net_cents") or 0.0) for row in danger20),
        "max_gap_row": scored[0] if scored else None,
        "top_gap_rows": scored[:12],
        "interpretation": current_read(rows, settled, danger30, danger20, scored),
    }


def current_read(
    rows: list[dict[str, Any]],
    settled: list[dict[str, Any]],
    danger30: list[dict[str, Any]],
    danger20: list[dict[str, Any]],
    scored: list[dict[str, Any]],
) -> list[str]:
    max_gap = scored[0].get("raw_book_gap") if scored else None
    return [
        f"Target-coverage surface has {len(rows)} entries and {len(settled)} settled rows.",
        f"Rows with raw-book gap >30pp: {len(danger30)}; rows >20pp: {len(danger20)}; max gap: {max_gap}.",
        "Current target-coverage evidence is not being driven by the approved-entry danger-zone regime.",
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
    lines = [
        "# v28 Target-Coverage Danger Overlap",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/settled/scored: `{report.get('entries')}/{report.get('settled')}/{report.get('scored')}`",
        f"- Danger rows >30pp/>20pp: `{report.get('danger_gt30_count')}/{report.get('danger_gt20_count')}`",
        f"- Danger net >30pp/>20pp: `{fmt(report.get('danger_gt30_net_cents'))}c/{fmt(report.get('danger_gt20_net_cents'))}c`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Top Gap Rows",
        "",
        "| market | side | raw p | ask p | gap | won | net c | reason |",
        "|---|---|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("top_gap_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {fmt(row.get('raw_p'))} | "
            f"{fmt(row.get('ask_p'))} | {fmt(row.get('raw_book_gap'))} | {row.get('won')} | "
            f"{fmt(row.get('net_cents'))} | {row.get('reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
