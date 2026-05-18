"""Frozen forward validator for the v28 danger-zone entry valve.

Research-only; no live bot changes or orders.

Freezes the combined danger-zone rule discovered on actual v28-approved
entries:
- block same-side reentries when raw FV exceeds executable book by more than
  15 percentage points;
- block any entry when raw FV exceeds executable book by more than 30
  percentage points.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_approved_entry_state_valves import raw_book_gap, sorted_rows, with_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_danger_zone_entry_valve_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.md"

POLICY = "skip_reentry_gap15_or_gap30"
MIN_SETTLED = 30
MIN_COVERAGE_PCT = 75.0


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
        "rule": (
            "keep row unless raw-book gap > 0.30, or same-market same-side "
            "reentry has raw-book gap > 0.15"
        ),
        "source_artifact": "v28_danger_zone_entry_valve_latest.json",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def is_same_side_reentry(row: dict[str, Any]) -> bool:
    return int(row.get("market_side_entry_index") or 0) > 0


def keep_valve(row: dict[str, Any]) -> bool:
    gap = raw_book_gap(row)
    if gap is None:
        return True
    if gap > 0.30:
        return False
    if is_same_side_reentry(row) and gap > 0.15:
        return False
    return True


def score(rows: list[dict[str, Any]], keep_candidate: bool) -> dict[str, Any]:
    selected = [row for row in rows if (keep_valve(row) if keep_candidate else True)]
    skipped = [row for row in rows if row not in selected]
    markets = {row.get("market") for row in rows}
    selected_markets = {row.get("market") for row in selected}
    return {
        "policy": POLICY if keep_candidate else "current_v28_approved_all",
        "entries": len(selected),
        "settled": len(selected),
        "wins": sum(1 for row in selected if row.get("side_won") is True),
        "losses": sum(1 for row in selected if row.get("side_won") is False),
        "gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in selected),
        "hold_gross_cents": sum(float(row.get("hold_gross_cents") or 0.0) for row in selected),
        "skipped_entries": len(skipped),
        "skipped_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in skipped),
        "skipped_hold_gross_cents": sum(float(row.get("hold_gross_cents") or 0.0) for row in skipped),
        "market_coverage_pct": 100.0 * len(selected_markets) / len(markets) if markets else None,
        "skipped_examples": skipped_examples(skipped),
    }


def skipped_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows[:12]:
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "gross_cents": row.get("actual_gross_cents"),
            "hold_gross_cents": row.get("hold_gross_cents"),
            "p_side": row.get("p_side"),
            "ask_cents": row.get("ask_cents"),
            "raw_book_gap": row.get("raw_book_gap"),
            "market_side_entry_index": row.get("market_side_entry_index"),
        })
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"])
    rows = [
        row for row in with_state(sorted_rows())
        if parse_ts(row.get("entry_ts")) >= freeze_ts
    ]
    control = score(rows, False)
    candidate = score(rows, True)
    candidate["delta_vs_control_cents"] = float(candidate["gross_cents"]) - float(control["gross_cents"])
    blockers = []
    if int(candidate.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    coverage = candidate.get("market_coverage_pct")
    if coverage is not None and float(coverage) < MIN_COVERAGE_PCT:
        blockers.append("coverage_below_75pct")
    if int(candidate.get("settled") or 0) > 0 and float(candidate.get("delta_vs_control_cents") or 0.0) <= 0.0:
        blockers.append("delta_not_positive")
    return {
        "freeze": state,
        "future_rows": len(rows),
        "future_markets": len({row.get("market") for row in rows}),
        "control": control,
        "candidate": candidate,
        "blockers": blockers,
        "interpretation": [
            f"Frozen danger-zone policy {POLICY} has {candidate.get('settled')} future settled approved rows and delta {candidate.get('delta_vs_control_cents')}c vs current approved entries.",
            "This is actual-v28-approved-only forward validation; it does not score rejected simulated entries.",
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
        "# v28 Frozen Danger-Zone Entry Valve",
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
    lines.extend(["", "## Skipped Examples", ""])
    for ex in c.get("skipped_examples") or []:
        lines.append(
            f"- `{ex.get('market')}` `{ex.get('side')}` won `{ex.get('won')}`, gross/hold "
            f"`{fmt(ex.get('gross_cents'))}/{fmt(ex.get('hold_gross_cents'))}`, gap `{fmt(ex.get('raw_book_gap'))}`, "
            f"same-side idx `{ex.get('market_side_entry_index')}`"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
