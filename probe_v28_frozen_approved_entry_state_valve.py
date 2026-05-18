"""Frozen forward validator for the approved-entry state valve.

Research-only; no live bot changes or orders.

Freezes the best actual-only state-valve mechanism discovered from approved
v28 entries: allow first same-side entry in a market, but block same-side
reentries when raw FV exceeds executable book by more than 15 percentage points.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_approved_entry_state_valves import raw_book_gap, sorted_rows, with_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_approved_entry_state_valve_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.md"

POLICY = "same_side_reentry_gap_lte_15pp"
MIN_SETTLED = 30


def parse_ts(value: Any) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and payload.get("freeze_ts_utc"):
                return payload
        except json.JSONDecodeError:
            pass
    state = {
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "policy": POLICY,
        "rule": "keep first same-market same-side entry; for same-side reentries require raw_probability - ask_probability <= 0.15",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def keep_valve(row: dict[str, Any]) -> bool:
    if int(row.get("market_side_entry_index") or 0) == 0:
        return True
    gap = raw_book_gap(row)
    return gap is None or gap <= 0.15


def score(rows: list[dict[str, Any]], keep_valve_policy: bool) -> dict[str, Any]:
    selected = [row for row in rows if (keep_valve(row) if keep_valve_policy else True)]
    skipped = [row for row in rows if row not in selected]
    markets = {row.get("market") for row in rows}
    selected_markets = {row.get("market") for row in selected}
    return {
        "policy": POLICY if keep_valve_policy else "current_v28_approved_all",
        "entries": len(selected),
        "settled": len(selected),
        "wins": sum(1 for row in selected if row.get("side_won") is True),
        "losses": sum(1 for row in selected if row.get("side_won") is False),
        "gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in selected),
        "skipped_entries": len(skipped),
        "skipped_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in skipped),
        "market_coverage_pct": 100.0 * len(selected_markets) / len(markets) if markets else None,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"])
    rows = [
        row for row in with_state(sorted_rows())
        if parse_ts(row.get("entry_ts")) >= freeze_ts
    ]
    control = score(rows, False)
    valve = score(rows, True)
    valve["delta_vs_control_cents"] = float(valve["gross_cents"]) - float(control["gross_cents"])
    blockers = []
    if int(valve.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if valve.get("market_coverage_pct") is not None and float(valve["market_coverage_pct"]) < 75.0:
        blockers.append("coverage_below_75pct")
    if float(valve.get("delta_vs_control_cents") or 0.0) <= 0.0 and int(valve.get("settled") or 0) > 0:
        blockers.append("delta_not_positive")
    return {
        "freeze": state,
        "future_rows": len(rows),
        "future_markets": len({row.get("market") for row in rows}),
        "control": control,
        "candidate": valve,
        "blockers": blockers,
        "interpretation": [
            f"Frozen policy {POLICY} has {valve.get('settled')} future settled approved rows and delta {valve.get('delta_vs_control_cents')}c vs current approved entries.",
            "This validates only actual v28-approved entries after the freeze timestamp; it does not use rejected simulated rows.",
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
    c = report.get("candidate") or {}
    control = report.get("control") or {}
    lines = [
        "# v28 Frozen Approved-Entry State Valve",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Policy: `{c.get('policy')}`",
        f"- Future rows/markets: `{report.get('future_rows')}/{report.get('future_markets')}`",
        f"- Candidate entries/W-L/gross: `{c.get('entries')}/{c.get('wins')}-{c.get('losses')}/{fmt(c.get('gross_cents'))}c`",
        f"- Control entries/W-L/gross: `{control.get('entries')}/{control.get('wins')}-{control.get('losses')}/{fmt(control.get('gross_cents'))}c`",
        f"- Delta / coverage / skipped: `{fmt(c.get('delta_vs_control_cents'))}c/{fmt(c.get('market_coverage_pct'))}%/{c.get('skipped_entries')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
