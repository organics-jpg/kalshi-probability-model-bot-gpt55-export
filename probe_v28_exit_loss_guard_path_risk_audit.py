"""Path-risk audit for loss-guarded v28 book-gap exit watches.

Research-only; no live bot changes or orders.

The loss-guarded rows are currently clean on settlement delta, but a hold
candidate also needs path-survival evidence. This audit uses the
worst_post_exit_hold_mark_cents already captured in the frozen watch rows to
measure how much adverse mark-to-market risk the suppressed exits required.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_loss_guard_path_risk_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_loss_guard_path_risk_audit_latest.md"

SOURCES = {
    "book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
}


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def strict_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row for row in (payload.get("rows") or [])
        if isinstance(row, dict) and row.get("result") not in (None, "", "unknown")
    ]


def suppressed_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in strict_rows(payload) if row.get("suppressed") is True]


def path_metrics(row: dict[str, Any]) -> dict[str, Any]:
    current = fnum(row.get("current_cents"))
    hold = fnum(row.get("hold_cents"))
    worst = row.get("worst_post_exit_hold_mark_cents")
    worst_val = None if worst is None else fnum(worst)
    adverse_vs_exit = None if worst_val is None else worst_val - current
    adverse_vs_settlement = None if worst_val is None else worst_val - hold
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "exit_reason": row.get("exit_reason"),
        "exit_cents": row.get("exit_cents"),
        "p_hold": row.get("p_hold"),
        "hold_book_gap": row.get("hold_book_gap"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "current_cents": current,
        "hold_cents": hold,
        "delta_cents": fnum(row.get("delta_cents")),
        "worst_post_exit_hold_mark_cents": worst_val,
        "adverse_vs_exit_cents": adverse_vs_exit,
        "adverse_vs_settlement_cents": adverse_vs_settlement,
        "adverse_vs_exit_10c": adverse_vs_exit is not None and adverse_vs_exit <= -10.0,
        "adverse_vs_exit_25c": adverse_vs_exit is not None and adverse_vs_exit <= -25.0,
        "adverse_vs_exit_50c": adverse_vs_exit is not None and adverse_vs_exit <= -50.0,
        "absolute_mark_below_zero": worst_val is not None and worst_val < 0.0,
        "absolute_mark_below_full_loss": worst_val is not None and worst_val <= -100.0,
    }


def summarize(lane: str, payload: dict[str, Any]) -> dict[str, Any]:
    rows = [path_metrics(row) for row in suppressed_rows(payload)]
    with_path = [row for row in rows if row.get("worst_post_exit_hold_mark_cents") is not None]
    adverse10 = [row for row in with_path if row.get("adverse_vs_exit_10c")]
    adverse25 = [row for row in with_path if row.get("adverse_vs_exit_25c")]
    adverse50 = [row for row in with_path if row.get("adverse_vs_exit_50c")]
    below_zero = [row for row in with_path if row.get("absolute_mark_below_zero")]
    below_full = [row for row in with_path if row.get("absolute_mark_below_full_loss")]
    adverse_vals = [fnum(row.get("adverse_vs_exit_cents")) for row in with_path]
    absolute_vals = [fnum(row.get("worst_post_exit_hold_mark_cents")) for row in with_path]
    blockers = []
    if len(rows) < 30:
        blockers.append("suppressed_rows_lt_30")
    if adverse25:
        blockers.append("post_exit_adverse_25c_present")
    if below_zero:
        blockers.append("post_exit_mark_below_zero_present")
    return {
        "lane": lane,
        "freeze_ts_utc": (payload.get("freeze") or {}).get("freeze_ts_utc"),
        "strict_rows": len(strict_rows(payload)),
        "suppressed_rows": len(rows),
        "rows_with_path": len(with_path),
        "suppression_delta_cents": sum(fnum(row.get("delta_cents")) for row in rows),
        "worst_adverse_vs_exit_cents": min(adverse_vals) if adverse_vals else None,
        "avg_adverse_vs_exit_cents": (sum(adverse_vals) / len(adverse_vals)) if adverse_vals else None,
        "worst_absolute_mark_cents": min(absolute_vals) if absolute_vals else None,
        "adverse_vs_exit_10c_rows": len(adverse10),
        "adverse_vs_exit_25c_rows": len(adverse25),
        "adverse_vs_exit_50c_rows": len(adverse50),
        "absolute_mark_below_zero_rows": len(below_zero),
        "absolute_mark_below_full_loss_rows": len(below_full),
        "blockers": blockers,
        "worst_rows": sorted(
            with_path,
            key=lambda row: fnum(row.get("adverse_vs_exit_cents"), 999.0),
        )[:10],
    }


def build_report() -> dict[str, Any]:
    lanes = [summarize(lane, load_json(path)) for lane, path in SOURCES.items()]
    interpretation = [
        "Research-only path-risk audit; no live bot changes or orders.",
        "A clean hold-to-settlement delta is not sufficient if the row requires surviving large adverse marks after the skipped exit.",
    ]
    for lane in lanes:
        interpretation.append(
            f"{lane.get('lane')}: {lane.get('suppressed_rows')} suppressed rows, "
            f"worst adverse vs exit {lane.get('worst_adverse_vs_exit_cents')}c, "
            f"adverse 10/25/50 rows {lane.get('adverse_vs_exit_10c_rows')}/"
            f"{lane.get('adverse_vs_exit_25c_rows')}/{lane.get('adverse_vs_exit_50c_rows')}."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {lane: str(path) for lane, path in SOURCES.items()},
        "lanes": lanes,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Loss-Guard Path Risk Audit",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lane Summary",
            "",
            "| lane | strict rows | suppressed | path rows | delta c | worst adverse vs exit | avg adverse | worst mark | adverse 10/25/50 | below zero | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{lane.get('lane')}`",
                    str(lane.get("strict_rows")),
                    str(lane.get("suppressed_rows")),
                    str(lane.get("rows_with_path")),
                    fmt(lane.get("suppression_delta_cents")),
                    fmt(lane.get("worst_adverse_vs_exit_cents")),
                    fmt(lane.get("avg_adverse_vs_exit_cents")),
                    fmt(lane.get("worst_absolute_mark_cents")),
                    f"{lane.get('adverse_vs_exit_10c_rows')}/{lane.get('adverse_vs_exit_25c_rows')}/{lane.get('adverse_vs_exit_50c_rows')}",
                    str(lane.get("absolute_mark_below_zero_rows")),
                    ", ".join(lane.get("blockers") or []) or "none",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Worst Suppressed Rows", ""])
    for lane in report.get("lanes") or []:
        worst = lane.get("worst_rows") or []
        if not worst:
            continue
        lines.append(f"### {lane.get('lane')}")
        lines.append("")
        lines.append("| market | side | reason | current | hold | delta | worst mark | adverse vs exit | p_hold | gap |")
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
        for row in worst:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('exit_reason')}` | "
                f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
                f"{fmt(row.get('delta_cents'))} | {fmt(row.get('worst_post_exit_hold_mark_cents'))} | "
                f"{fmt(row.get('adverse_vs_exit_cents'))} | {fmt(row.get('p_hold'))} | {fmt(row.get('hold_book_gap'))} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
