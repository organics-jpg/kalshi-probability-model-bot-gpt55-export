"""Materialize the current v28 exit-clock row source once.

Research-only; no live bot changes or orders.

Some exit-clock builders re-score live/settling market outcomes on each call.
This snapshot captures one concrete read so downstream audits can reference a
fixed denominator instead of rebuilding a moving row source repeatedly.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_common_clock_watch import build_scored_rows
from probe_v28_reactivated_shadow_status import EVENTS_PATH


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_clock_materialized_snapshot_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clock_materialized_snapshot_latest.md"


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def compact(row: dict[str, Any]) -> dict[str, Any]:
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    exit_features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "exit_reason": row.get("exit_reason") or exit_features.get("mushroom_v28_exit_reason"),
        "actual_gross_cents": row.get("actual_gross_cents"),
        "hold_gross_cents": row.get("hold_gross_cents"),
        "exit_value_cents": row.get("exit_value_cents"),
        "result": row.get("result"),
        "qty": row.get("qty"),
        "entry_abs_d_sigma": entry.get("mushroom_v28_abs_d_sigma"),
        "entry_raw_edge_cents": entry.get("mushroom_v28_raw_edge_cents"),
        "entry_ask_cents": entry.get("mushroom_v28_ask_cents"),
        "entry_p_side": entry.get("mushroom_v28_p_side"),
        "exit_p_hold": exit_features.get("mushroom_v28_p_hold"),
        "exit_fair_drawdown_cents": exit_features.get("mushroom_v28_fair_drawdown_cents"),
    }


def build_report() -> dict[str, Any]:
    rows = [compact(row) for row in build_scored_rows()]
    rows.sort(key=lambda row: (str(row.get("entry_ts") or ""), str(row.get("market") or ""), str(row.get("side") or "")))
    events_stat = EVENTS_PATH.stat() if EVENTS_PATH.exists() else None
    resolved = [row for row in rows if row.get("actual_gross_cents") is not None and row.get("hold_gross_cents") is not None]
    keys = {(row.get("market"), row.get("side"), row.get("entry_ts")) for row in rows}
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "probe_v28_exit_policy_common_clock_watch.build_scored_rows",
        "events_path": str(EVENTS_PATH),
        "events_last_write": events_stat.st_mtime if events_stat else None,
        "events_size_bytes": events_stat.st_size if events_stat else None,
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "unique_keys": len(keys),
            "resolved_rows": len(resolved),
            "current_net_cents": sum(fnum(row.get("actual_gross_cents")) for row in resolved),
            "hold_net_cents": sum(fnum(row.get("hold_gross_cents")) for row in resolved),
            "first_entry_ts": rows[0].get("entry_ts") if rows else None,
            "last_entry_ts": rows[-1].get("entry_ts") if rows else None,
        },
        "interpretation": [
            "This is a materialized research snapshot, not a candidate and not promotion evidence.",
            "Use it when a downstream audit needs a fixed exit-clock denominator for reproducibility.",
        ],
    }


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Exit-Clock Materialized Snapshot",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Rows / unique keys: `{summary.get('rows')}` / `{summary.get('unique_keys')}`",
        f"- Resolved rows: `{summary.get('resolved_rows')}`",
        f"- Current / hold net: `{money(summary.get('current_net_cents'))}` / `{money(summary.get('hold_net_cents'))}`",
        f"- First / last entry: `{summary.get('first_entry_ts')}` / `{summary.get('last_entry_ts')}`",
        f"- Events size bytes: `{report.get('events_size_bytes')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
