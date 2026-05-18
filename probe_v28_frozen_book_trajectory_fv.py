"""Frozen forward validator for the v28 book-trajectory FV overlay.

Research-only; no live bot changes or orders.

Frozen candidate:
- raw v28 probability by default;
- if raw probability exceeds executable book probability by >15pp, or the
  same side's book probability has just dropped by >=10pp, shrink 60% toward
  book.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_book_disagreement_trajectory_fv import (
    VARIANTS,
    observation_events,
    rank_view,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_book_trajectory_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_book_trajectory_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_book_trajectory_fv_latest.md"

CANDIDATE = "gap15_or_drawdown10"
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
        "candidate": CANDIDATE,
        "rule": "raw v28 unless raw-book gap >15pp or same-side book drawdown <= -10pp; then blend 40% raw / 60% book",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def candidate_row(ranked: list[dict[str, Any]]) -> dict[str, Any]:
    return next((row for row in ranked if row.get("variant") == CANDIDATE), {})


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"])
    rows = [row for row in observation_events() if parse_ts(row.get("ts_wall")) >= freeze_ts]
    views = []
    for view in ["approved_only", "first_per_market_side", "last_per_market_side", "all_observations"]:
        ranked_view = rank_view(rows, view)
        cand = candidate_row(ranked_view.get("ranked") or [])
        blockers = []
        if int(cand.get("rows") or 0) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if cand.get("brier_delta_vs_raw") is None or float(cand.get("brier_delta_vs_raw") or 0.0) >= 0.0:
            blockers.append("brier_not_better_than_raw")
        if cand.get("logloss_delta_vs_raw") is None or float(cand.get("logloss_delta_vs_raw") or 0.0) >= 0.0:
            blockers.append("logloss_not_better_than_raw")
        views.append({
            **ranked_view,
            "candidate": cand,
            "blockers": blockers,
        })
    return {
        "freeze": state,
        "future_rows": len(rows),
        "future_markets": len({row["market"] for row in rows}),
        "future_market_sides": len({(row["market"], row["side"]) for row in rows}),
        "candidate": CANDIDATE,
        "views": views,
        "interpretation": current_read(views),
    }


def current_read(views: list[dict[str, Any]]) -> list[str]:
    notes = []
    for view in views:
        cand = view.get("candidate") or {}
        notes.append(
            f"View {view.get('view')} candidate rows {cand.get('rows')} with Brier/logloss deltas {cand.get('brier_delta_vs_raw')}/{cand.get('logloss_delta_vs_raw')} and blockers {view.get('blockers')}."
        )
    return notes


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
        "# v28 Frozen Book-Trajectory FV",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Future rows/markets/market-sides: `{report.get('future_rows')}/{report.get('future_markets')}/{report.get('future_market_sides')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Views",
        "",
        "| view | rows | W/L | avg p | win rate | brier d | logloss d | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for view in report.get("views") or []:
        c = view.get("candidate") or {}
        lines.append(
            f"| `{view.get('view')}` | {c.get('rows')} | {c.get('wins')}/{c.get('losses')} | "
            f"{fmt(c.get('avg_p'))} | {fmt(c.get('win_rate'))} | "
            f"{fmt(c.get('brier_delta_vs_raw'))} | {fmt(c.get('logloss_delta_vs_raw'))} | "
            f"{', '.join(view.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    # Guard import drift: fail loudly if the frozen candidate is removed.
    if CANDIDATE not in VARIANTS:
        raise RuntimeError(f"missing frozen candidate {CANDIDATE}")
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
