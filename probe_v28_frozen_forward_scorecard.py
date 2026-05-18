"""Unified post-freeze scorecard for v28 candidate validation.

Research-only; no live bot changes or orders.

Collects the frozen state-valve, book-trajectory FV, pending monitor, and live
control reads into one compact status artifact so the forward sample can be
tracked without cherry-picking separate reports.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_VALVE_JSON = OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.json"
DANGER_VALVE_JSON = OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.json"
BOOK_TRAJ_JSON = OUT_DIR / "v28_frozen_book_trajectory_fv_latest.json"
PENDING_JSON = OUT_DIR / "v28_frozen_pending_monitor_latest.json"
STATUS_JSON = OUT_DIR / "v28_reactivated_shadow_status_latest.json"
EXIT_BOOK_GAP_JSON = OUT_DIR / "v28_exit_book_gap_candidates_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_forward_scorecard_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_forward_scorecard_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def best_view_candidate(book: dict[str, Any], view_name: str) -> dict[str, Any]:
    for view in book.get("views") or []:
        if view.get("view") == view_name:
            return view.get("candidate") or {}
    return {}


def control_summary(status: dict[str, Any]) -> dict[str, Any]:
    summary = status.get("summary") if isinstance(status.get("summary"), dict) else status
    return {
        "trades": summary.get("trades_reconstructed") or summary.get("trades") or summary.get("entries"),
        "resolved": summary.get("resolved_or_exited") or summary.get("resolved_exited_scored_rows") or summary.get("scored_rows"),
        "gross_cents": summary.get("gross_cents"),
        "hold_gross_cents": summary.get("hold_gross_cents"),
        "exit_value_cents": summary.get("exit_value_cents"),
    }


def current_exit_row(exit_book_gap: dict[str, Any]) -> dict[str, Any]:
    return next((row for row in exit_book_gap.get("summary") or [] if row.get("policy") == "current_v28_exit"), {})


def build_report() -> dict[str, Any]:
    state = load_json(STATE_VALVE_JSON)
    danger = load_json(DANGER_VALVE_JSON)
    book = load_json(BOOK_TRAJ_JSON)
    pending = load_json(PENDING_JSON)
    status = load_json(STATUS_JSON)
    exit_book = load_json(EXIT_BOOK_GAP_JSON)

    state_candidate = state.get("candidate") or {}
    danger_candidate = danger.get("candidate") or {}
    book_approved = best_view_candidate(book, "approved_only")
    book_first = best_view_candidate(book, "first_per_market_side")
    book_all = best_view_candidate(book, "all_observations")
    current_exit = current_exit_row(exit_book)

    useful_signals = []
    if int(state_candidate.get("settled") or 0) > 0:
        useful_signals.append(
            f"State valve has {state_candidate.get('settled')} settled post-freeze rows with delta {state_candidate.get('delta_vs_control_cents')}c."
        )
    if int(danger_candidate.get("settled") or 0) > 0:
        useful_signals.append(
            f"Danger-zone valve has {danger_candidate.get('settled')} settled post-freeze rows with delta {danger_candidate.get('delta_vs_control_cents')}c."
        )
    if int(book_all.get("rows") or 0) > 0:
        useful_signals.append(
            f"Book-trajectory all-observation FV delta is {book_all.get('brier_delta_vs_raw')}/{book_all.get('logloss_delta_vs_raw')}."
        )
    if current_exit:
        useful_signals.append(
            f"Current v28 exits are {current_exit.get('gross_cents')}c over {current_exit.get('trades')} trades; simple exit book-gap suppressors are not better."
        )
    return {
        "state_valve": {
            "freeze_ts": (state.get("freeze") or {}).get("freeze_ts_utc"),
            "entries": state_candidate.get("entries"),
            "settled": state_candidate.get("settled"),
            "wins": state_candidate.get("wins"),
            "losses": state_candidate.get("losses"),
            "gross_cents": state_candidate.get("gross_cents"),
            "delta_vs_control_cents": state_candidate.get("delta_vs_control_cents"),
            "coverage_pct": state_candidate.get("market_coverage_pct"),
            "blockers": state.get("blockers"),
        },
        "book_trajectory_fv": {
            "freeze_ts": (book.get("freeze") or {}).get("freeze_ts_utc"),
            "future_rows": book.get("future_rows"),
            "future_markets": book.get("future_markets"),
            "approved_only": book_approved,
            "first_per_market_side": book_first,
            "all_observations": book_all,
        },
        "danger_zone_valve": {
            "freeze_ts": (danger.get("freeze") or {}).get("freeze_ts_utc"),
            "entries": danger_candidate.get("entries"),
            "settled": danger_candidate.get("settled"),
            "wins": danger_candidate.get("wins"),
            "losses": danger_candidate.get("losses"),
            "gross_cents": danger_candidate.get("gross_cents"),
            "delta_vs_control_cents": danger_candidate.get("delta_vs_control_cents"),
            "coverage_pct": danger_candidate.get("market_coverage_pct"),
            "blockers": danger.get("blockers"),
        },
        "pending": {
            "state_valve_count": pending.get("pending_state_valve_count"),
            "book_trajectory_count": pending.get("pending_book_trajectory_count"),
            "state_rows": pending.get("pending_state_valve_rows"),
        },
        "control": control_summary(status),
        "exit_control": current_exit,
        "interpretation": useful_signals or ["No post-freeze settled signal yet."],
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
    state = report.get("state_valve") or {}
    book = report.get("book_trajectory_fv") or {}
    danger = report.get("danger_zone_valve") or {}
    pending = report.get("pending") or {}
    control = report.get("control") or {}
    exit_control = report.get("exit_control") or {}
    all_obs = book.get("all_observations") or {}
    approved = book.get("approved_only") or {}
    first = book.get("first_per_market_side") or {}
    lines = [
        "# v28 Frozen Forward Scorecard",
        "",
        "Unified forward-only scorecard for frozen v28 state/FV candidates.",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## State Valve",
        "",
        f"- Freeze: `{state.get('freeze_ts')}`",
        f"- Entries/settled/W-L: `{state.get('entries')}/{state.get('settled')}/{state.get('wins')}-{state.get('losses')}`",
        f"- Gross/delta/coverage: `{fmt(state.get('gross_cents'))}c/{fmt(state.get('delta_vs_control_cents'))}c/{fmt(state.get('coverage_pct'))}%`",
        f"- Blockers: `{', '.join(state.get('blockers') or []) or 'none'}`",
        "",
        "## Danger-Zone Valve",
        "",
        f"- Freeze: `{danger.get('freeze_ts')}`",
        f"- Entries/settled/W-L: `{danger.get('entries')}/{danger.get('settled')}/{danger.get('wins')}-{danger.get('losses')}`",
        f"- Gross/delta/coverage: `{fmt(danger.get('gross_cents'))}c/{fmt(danger.get('delta_vs_control_cents'))}c/{fmt(danger.get('coverage_pct'))}%`",
        f"- Blockers: `{', '.join(danger.get('blockers') or []) or 'none'}`",
        "",
        "## Book-Trajectory FV",
        "",
        f"- Freeze: `{book.get('freeze_ts')}`",
        f"- Future rows/markets: `{book.get('future_rows')}/{book.get('future_markets')}`",
        f"- Approved-only rows and Brier/logloss delta: `{approved.get('rows')}/{fmt(approved.get('brier_delta_vs_raw'))}/{fmt(approved.get('logloss_delta_vs_raw'))}`",
        f"- First market-side rows and Brier/logloss delta: `{first.get('rows')}/{fmt(first.get('brier_delta_vs_raw'))}/{fmt(first.get('logloss_delta_vs_raw'))}`",
        f"- All observation rows and Brier/logloss delta: `{all_obs.get('rows')}/{fmt(all_obs.get('brier_delta_vs_raw'))}/{fmt(all_obs.get('logloss_delta_vs_raw'))}`",
        "",
        "## Pending",
        "",
        f"- Pending state/book rows: `{pending.get('state_valve_count')}/{pending.get('book_trajectory_count')}`",
        "",
        "## Control",
        "",
        f"- Reconstructed/resolved trades: `{control.get('trades')}/{control.get('resolved')}`",
        f"- Gross/hold/exit value: `{fmt(control.get('gross_cents'))}c/{fmt(control.get('hold_gross_cents'))}c/{fmt(control.get('exit_value_cents'))}c`",
        f"- Current exit gross/trades: `{fmt(exit_control.get('gross_cents'))}c/{exit_control.get('trades')}`",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
