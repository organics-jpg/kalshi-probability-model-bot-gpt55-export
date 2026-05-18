"""Frozen forward watch for the dual exit mix candidate.

Research-only; no live bot changes or orders.

Diagnostic mix/match found that book-gap exit suppression dominated reduce
suppression on their common window, while reduce-only rows added positive net
outside that window. This probe freezes the composite from a new timestamp:
use the book-gap candidate row when present, otherwise fall back to the reduce
suppression candidate row.

Important: on a clean shared future window this may collapse to the book-gap
rule if every reduce row is also present in the book-gap ledger. That outcome is
useful evidence, not a failure of the probe.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_state.json"
EXIT_REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
EXIT_BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.md"

MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3


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
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "dual_exit_book_gap_else_reduce",
        "rule": (
            "For each post-freeze settled live v28 exit row, use "
            "suppress_soft_gap15_or_p_hold75 when that ledger has the row; "
            "otherwise use suppress_reduce_p_hold_ge_075."
        ),
        "physics": (
            "Soft exit marks can be spread/turbulence artifacts; book-gap "
            "context is preferred when observable, while reduce-suppression "
            "is retained only as a fallback for rows outside the book-gap ledger."
        ),
        "source_artifacts": [
            str(EXIT_BOOK_GAP_JSON),
            str(EXIT_REDUCE_JSON),
        ],
        "strict_forward_note": "Rows before this timestamp are diagnostic only.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def row_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("exit_ts") or row.get("entry_ts"))


def row_key(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (row.get("market"), row.get("side"), row.get("entry_ts"))


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_cents(row: dict[str, Any], *fields: str) -> float | None:
    for field in fields:
        value = as_float(row.get(field))
        if value is not None:
            return value
    return None


def future_source_rows(path: Path, freeze_ts: str) -> dict[tuple[Any, Any, Any], dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    payload = load_json(path)
    out: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        ts = row_ts(row)
        if freeze_dt is not None and ts is not None and ts < freeze_dt:
            continue
        key = row_key(row)
        if key[0] and key[2]:
            out[key] = row
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    current_vals = [row_cents(row, "current_cents", "current_net_cents") for row in rows]
    candidate_vals = [row_cents(row, "candidate_cents", "candidate_net_cents") for row in rows]
    current = [float(value) for value in current_vals if value is not None]
    candidate = [float(value) for value in candidate_vals if value is not None]
    suppressed = [row for row in rows if row.get("suppressed")]
    loss_control_cost = sum(
        row_cents(row, "delta_cents") or 0.0
        for row in suppressed
        if str(row.get("result") or "").lower() != str(row.get("side") or "").lower()
    )
    winner_recovery = sum(
        row_cents(row, "delta_cents") or 0.0
        for row in suppressed
        if str(row.get("result") or "").lower() == str(row.get("side") or "").lower()
    )
    net = sum(candidate)
    return {
        "rows": len(rows),
        "settled": len(candidate),
        "current_gross_cents": sum(current),
        "candidate_gross_cents": net,
        "delta_vs_current_cents": net - sum(current),
        "current_wins": sum(1 for value in current if value >= 0.0),
        "current_losses": sum(1 for value in current if value < 0.0),
        "candidate_wins": sum(1 for value in candidate if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate if value < 0.0),
        "suppressed_exits": len(suppressed),
        "winner_clip_recovered_cents": winner_recovery,
        "loss_control_cost_cents": loss_control_cost,
        "full_loss_cushion_estimate": int(net // 100) if net > 0.0 else 0,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    reduce_rows = future_source_rows(EXIT_REDUCE_JSON, freeze_ts)
    book_rows = future_source_rows(EXIT_BOOK_GAP_JSON, freeze_ts)
    keys = sorted(set(reduce_rows) | set(book_rows), key=lambda key: str(key))
    rows: list[dict[str, Any]] = []
    source_counts = {"book_gap": 0, "reduce_fallback": 0}
    for key in keys:
        if key in book_rows:
            source = "book_gap"
            row = dict(book_rows[key])
        else:
            source = "reduce_fallback"
            row = dict(reduce_rows[key])
        source_counts[source] += 1
        row["selected_source"] = source
        rows.append(row)
    rows.sort(key=lambda row: str(row.get("exit_ts") or row.get("entry_ts") or ""))
    summary = summarize(rows)
    blockers = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        blockers.append("delta_not_positive")
    if float(summary.get("candidate_gross_cents") or 0.0) <= 0.0:
        blockers.append("net_not_positive")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        blockers.append("suppressed_loss_control_cost_negative")
    if int(summary.get("full_loss_cushion_estimate") or 0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if source_counts["reduce_fallback"] == 0 and source_counts["book_gap"] > 0:
        blockers.append("degenerates_to_book_gap_on_shared_window")
    return {
        "freeze": state,
        "summary": summary,
        "source_counts": source_counts,
        "rows": rows,
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "interpretation": [
            f"Dual exit composite has {summary.get('settled')} settled post-freeze rows.",
            f"Selected source counts are {source_counts}.",
            f"Candidate/current/delta are {summary.get('candidate_gross_cents')}c/{summary.get('current_gross_cents')}c/{summary.get('delta_vs_current_cents')}c.",
            "If reduce_fallback stays zero, the clean future composite is simply the book-gap exit candidate.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    summary = report.get("summary") or {}
    lines = [
        "# v28 Frozen Dual Exit Book-Gap Else Reduce",
        "",
        "Research-only frozen forward watch. No live bot changes.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future rows/settled: `{summary.get('rows')}/{summary.get('settled')}`",
        f"- Current/candidate gross: `{summary.get('current_gross_cents')}c/{summary.get('candidate_gross_cents')}c`",
        f"- Delta vs current: `{summary.get('delta_vs_current_cents')}c`",
        f"- W/L: `{summary.get('candidate_wins')}/{summary.get('candidate_losses')}`",
        f"- Full-loss cushion estimate: `{summary.get('full_loss_cushion_estimate')}`",
        f"- Source counts: `{report.get('source_counts')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | result | source | reason | current c | candidate c | delta c | suppressed |",
        "|---|---|---|---|---|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | "
            f"{row.get('selected_source')} | {row.get('exit_reason')} | "
            f"{row.get('current_cents')} | {row.get('candidate_cents')} | "
            f"{fmt(row.get('delta_cents'))} | {row.get('suppressed')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
