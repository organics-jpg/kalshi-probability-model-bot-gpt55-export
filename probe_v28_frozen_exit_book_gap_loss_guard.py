"""Frozen forward watch for loss-guarded v28 book-gap exit suppression.

Research-only; no live bot changes or orders.

Discovery finding:
    Plain book-gap/soft-exit suppression is strongly positive, but the observed
    harm comes from suppressing probability_reduce exits that were not clearly
    mispriced by the book. This watch keeps the broad value-over-hold repair and
    adds a stricter book-gap guard to probability_reduce suppression.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import (
    exit_bid_prob,
    exit_reason,
    fair_drawdown,
    hold_book_gap,
    is_soft_exit,
    p_hold,
)
from probe_v28_exit_policy_candidates import build_rows, current_exit, hold_to_settlement, side_won
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_state.json"
BOOK_GAP_STATE_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.md"

MIN_SETTLED = 30
VALUE_P_HOLD_FLOOR = 0.85
VALUE_GAP_FLOOR = 0.0
REDUCE_P_HOLD_FLOOR = 0.79
REDUCE_GAP_FLOOR = 0.0


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
        "candidate": "book_gap_loss_guard_value_p85_reduce_p79_gap0",
        "value_p_hold_floor": VALUE_P_HOLD_FLOOR,
        "value_gap_floor": VALUE_GAP_FLOOR,
        "reduce_p_hold_floor": REDUCE_P_HOLD_FLOOR,
        "reduce_gap_floor": REDUCE_GAP_FLOOR,
        "rule": (
            "Suppress value-over-hold soft exits when p_hold >= 0.85 or "
            "p_hold - exit_bid >= 0.00. Suppress probability_reduce exits only "
            "when p_hold >= 0.79 and p_hold - exit_bid >= 0.00. Keep collapse "
            "exits unchanged."
        ),
        "physics": (
            "Soft exits should only be ignored when the held side is either "
            "high-confidence or still clears the executable exit bid; this "
            "keeps winner-recovery upside while shrinking suppressed full-loss "
            "risk."
        ),
        "source_artifact": "v28_frozen_exit_book_gap_suppression_latest.json",
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


def future_rows(freeze_ts: str | None) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def is_value_over_hold(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_exit_value_over_hold"


def is_probability_reduce(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_probability_reduce"


def should_suppress(row: dict[str, Any], state: dict[str, Any]) -> bool:
    if not is_soft_exit(row):
        return False
    p = p_hold(row)
    gap = hold_book_gap(row)
    if is_value_over_hold(row):
        return (
            p is not None
            and p >= float(state.get("value_p_hold_floor") or VALUE_P_HOLD_FLOOR)
        ) or (
            gap is not None
            and gap >= float(state.get("value_gap_floor") or VALUE_GAP_FLOOR)
        )
    if is_probability_reduce(row):
        return (
            p is not None
            and p >= float(state.get("reduce_p_hold_floor") or REDUCE_P_HOLD_FLOOR)
            and gap is not None
            and gap >= float(state.get("reduce_gap_floor") or REDUCE_GAP_FLOOR)
        )
    return False


def candidate_gross(row: dict[str, Any], state: dict[str, Any]) -> float | None:
    if should_suppress(row, state):
        return hold_to_settlement(row)
    return current_exit(row)


def summarize(rows: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, state)
        if cur is None or cand is None:
            continue
        current_vals.append(float(cur))
        candidate_vals.append(float(cand))
        if should_suppress(row, state):
            suppressed.append(row)
    current_gross = sum(current_vals)
    candidate_gross_cents = sum(candidate_vals)
    loss_cost = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is False
    )
    winner_recovery = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is True
    )
    return {
        "rows": len(rows),
        "settled": len(candidate_vals),
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross_cents,
        "delta_vs_current_cents": candidate_gross_cents - current_gross,
        "current_wins": sum(1 for value in current_vals if value >= 0.0),
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "candidate_wins": sum(1 for value in candidate_vals if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "suppressed_exits": len(suppressed),
        "winner_clip_recovered_cents": winner_recovery,
        "loss_control_cost_cents": loss_cost,
    }


def detail_rows(rows: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    out = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, state)
        if cur is None or cand is None:
            continue
        path = path_by_market.get(str(row.get("market"))) or {}
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "exit_ts": row.get("exit_ts"),
            "entry_cents": row.get("entry_cents"),
            "exit_cents": row.get("exit_cents"),
            "exit_reason": exit_reason(row),
            "p_hold": p_hold(row),
            "exit_bid_prob": exit_bid_prob(row),
            "hold_book_gap": hold_book_gap(row),
            "fair_drawdown_cents": fair_drawdown(row),
            "current_cents": cur,
            "hold_cents": hold_to_settlement(row),
            "candidate_cents": cand,
            "delta_cents": float(cand) - float(cur),
            "suppressed": should_suppress(row, state),
            "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
        })
    out.sort(key=lambda row: str(row.get("exit_ts") or row.get("entry_ts") or ""))
    return out


def blockers_for(summary: dict[str, Any]) -> list[str]:
    blockers = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if float(summary.get("delta_vs_current_cents") or 0.0) <= 0.0:
        blockers.append("delta_not_positive")
    if float(summary.get("loss_control_cost_cents") or 0.0) < 0.0:
        blockers.append("suppressed_loss_control_cost_negative")
    if int(summary.get("suppressed_exits") or 0) < MIN_SETTLED:
        blockers.append("suppressed_decisions_lt_30")
    return blockers


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    forward_rows = future_rows(str(state["freeze_ts_utc"]))
    all_rows = future_rows(None)
    book_gap_state = load_json(BOOK_GAP_STATE_JSON)
    comparable_rows = future_rows(book_gap_state.get("freeze_ts_utc"))
    summary = summarize(forward_rows, state)
    discovery_summary = summarize(all_rows, state)
    comparable_summary = summarize(comparable_rows, state)
    blockers = blockers_for(summary)
    return {
        "freeze": state,
        "summary": summary,
        "discovery_summary_existing_exit_sample": discovery_summary,
        "discovery_summary_comparable_book_gap_freeze_sample": comparable_summary,
        "rows": detail_rows(forward_rows, state),
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "interpretation": [
            f"Frozen loss-guarded book-gap candidate has {summary.get('settled')} settled rows after its own freeze.",
            f"Post-freeze delta versus current v28 exits is {summary.get('delta_vs_current_cents')}c.",
            (
                "Discovery sample before this freeze scored "
                f"{discovery_summary.get('candidate_gross_cents')}c with "
                f"{discovery_summary.get('candidate_wins')}/{discovery_summary.get('candidate_losses')} W/L, "
                f"{discovery_summary.get('winner_clip_recovered_cents')}c winner recovery, and "
                f"{discovery_summary.get('loss_control_cost_cents')}c suppressed-loss cost."
            ),
            (
                "On the comparable book-gap freeze window, the same rule scored "
                f"{comparable_summary.get('candidate_gross_cents')}c with "
                f"{comparable_summary.get('winner_clip_recovered_cents')}c winner recovery and "
                f"{comparable_summary.get('loss_control_cost_cents')}c suppressed-loss cost."
            ),
        ],
    }


def fmt_cents(value: Any) -> str:
    try:
        cents = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    discovery = report["discovery_summary_existing_exit_sample"]
    comparable = report["discovery_summary_comparable_book_gap_freeze_sample"]
    freeze = report["freeze"]
    lines = [
        "# v28 Frozen Exit Book-Gap Loss Guard",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Freeze UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Live ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Post-Freeze Summary",
        "",
        "| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {summary.get('settled')} | {summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
            f"{fmt_cents(summary.get('current_gross_cents'))} | {fmt_cents(summary.get('candidate_gross_cents'))} | "
            f"{fmt_cents(summary.get('delta_vs_current_cents'))} | {summary.get('suppressed_exits')} | "
            f"{fmt_cents(summary.get('winner_clip_recovered_cents'))} | {fmt_cents(summary.get('loss_control_cost_cents'))} |"
        ),
        "",
        "## Discovery Sample",
        "",
        "This is diagnostic only; the forward clock starts at the freeze above.",
        "",
        "| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {discovery.get('settled')} | {discovery.get('candidate_wins')}/{discovery.get('candidate_losses')} | "
            f"{fmt_cents(discovery.get('current_gross_cents'))} | {fmt_cents(discovery.get('candidate_gross_cents'))} | "
            f"{fmt_cents(discovery.get('delta_vs_current_cents'))} | {discovery.get('suppressed_exits')} | "
            f"{fmt_cents(discovery.get('winner_clip_recovered_cents'))} | {fmt_cents(discovery.get('loss_control_cost_cents'))} |"
        ),
        "",
        "## Comparable Book-Gap Freeze Window",
        "",
        "This uses the earlier book-gap freeze timestamp for apples-to-apples diagnostic comparison.",
        "",
        "| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {comparable.get('settled')} | {comparable.get('candidate_wins')}/{comparable.get('candidate_losses')} | "
            f"{fmt_cents(comparable.get('current_gross_cents'))} | {fmt_cents(comparable.get('candidate_gross_cents'))} | "
            f"{fmt_cents(comparable.get('delta_vs_current_cents'))} | {comparable.get('suppressed_exits')} | "
            f"{fmt_cents(comparable.get('winner_clip_recovered_cents'))} | {fmt_cents(comparable.get('loss_control_cost_cents'))} |"
        ),
        "",
        "## Rule",
        "",
        str(freeze.get("rule")),
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
