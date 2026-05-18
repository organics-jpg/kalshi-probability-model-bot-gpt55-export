"""Pending-row monitor for frozen v28 candidates.

Research-only; no live bot changes or orders.

Frozen validators only score settled rows. This monitor shows unresolved
post-freeze rows already testing the frozen state valve and book-trajectory FV
candidate, plus the win/loss sensitivity for FV scoring.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_book_disagreement_trajectory_fv import VARIANTS
from probe_v28_forward_physics_registry import build_rows as approved_trade_rows
from probe_v28_reactivated_shadow_status import market_result, read_events


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_VALVE_STATE_JSON = OUT_DIR / "v28_frozen_approved_entry_state_valve_state.json"
BOOK_TRAJ_STATE_JSON = OUT_DIR / "v28_frozen_book_trajectory_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_pending_monitor_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_pending_monitor_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def parse_ts(value: Any) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def raw_book_gap(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_cents"))
    return None if p is None or ask is None else p - ask / 100.0


def state_valve_keep(rows: list[dict[str, Any]], row: dict[str, Any]) -> bool:
    same_prior = [
        prior for prior in rows
        if prior is not row
        and str(prior.get("market")) == str(row.get("market"))
        and str(prior.get("side")) == str(row.get("side"))
        and parse_ts(prior.get("entry_ts")) < parse_ts(row.get("entry_ts"))
    ]
    if not same_prior:
        return True
    gap = raw_book_gap(row)
    return gap is None or gap <= 0.15


def pending_state_valve_rows(freeze_ts: datetime) -> list[dict[str, Any]]:
    rows = approved_trade_rows()
    out = []
    for row in rows:
        if parse_ts(row.get("entry_ts")) < freeze_ts:
            continue
        if row.get("side_won") is not None:
            continue
        out.append({
            "market": row.get("market"),
            "entry_ts": row.get("entry_ts"),
            "side": row.get("side"),
            "status": row.get("status"),
            "result": row.get("result"),
            "entry_cents": row.get("entry_cents"),
            "p_side": row.get("p_side"),
            "ask_cents": row.get("ask_cents"),
            "raw_book_gap": raw_book_gap(row),
            "state_valve_keep": state_valve_keep(rows, row),
        })
    return out


def observation_rows(include_unresolved: bool = True) -> list[dict[str, Any]]:
    rows = []
    for event in read_events():
        event_type = str(event.get("event_type") or "")
        if event_type not in {"mushroom_v28_approved", "mushroom_v28_rejected", "plan_built", "fill_full"}:
            continue
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        p_side = as_float(event.get("mushroom_v28_p_side"))
        ask = as_float(event.get("mushroom_v28_ask_cents"))
        if not market or side not in {"yes", "no"} or p_side is None or ask is None:
            continue
        _, result = market_result(market)
        if result in {"yes", "no"} and not include_unresolved:
            continue
        if result in {"yes", "no"}:
            continue
        rows.append({
            "ts_wall": event.get("ts_wall"),
            "market": market,
            "side": side,
            "event_type": event_type,
            "approved": bool(event.get("mushroom_v28_approved")) or event_type in {"plan_built", "fill_full"},
            "p_side": p_side,
            "ask_prob": ask / 100.0,
            "ask_cents": ask,
            "seconds_to_close": as_float(event.get("mushroom_v28_seconds_to_close")),
        })
    rows.sort(key=lambda row: (str(row["market"]), str(row["side"]), parse_ts(row.get("ts_wall"))))
    return add_trajectory(rows)


def add_trajectory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prior_book: dict[tuple[str, str], float] = {}
    out = []
    for row in rows:
        key = (str(row["market"]), str(row["side"]))
        current_book = float(row["ask_prob"])
        enriched = dict(row)
        enriched["book_delta_vs_prior_same_side"] = None if key not in prior_book else current_book - prior_book[key]
        enriched["raw_book_gap"] = float(row["p_side"]) - current_book
        out.append(enriched)
        prior_book[key] = current_book
    return out


def brier_delta_if(row: dict[str, Any], outcome: float) -> float:
    raw = float(VARIANTS["raw_probability"](row))
    cand = float(VARIANTS["gap15_or_drawdown10"](row))
    return (cand - outcome) ** 2 - (raw - outcome) ** 2


def pending_book_traj_rows(freeze_ts: datetime) -> list[dict[str, Any]]:
    rows = []
    for row in observation_rows():
        if parse_ts(row.get("ts_wall")) < freeze_ts:
            continue
        cand_p = float(VARIANTS["gap15_or_drawdown10"](row))
        raw_p = float(VARIANTS["raw_probability"](row))
        rows.append({
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "event_type": row.get("event_type"),
            "approved": row.get("approved"),
            "raw_p": raw_p,
            "candidate_p": cand_p,
            "ask_prob": row.get("ask_prob"),
            "raw_book_gap": row.get("raw_book_gap"),
            "book_delta_vs_prior_same_side": row.get("book_delta_vs_prior_same_side"),
            "if_win_brier_delta": brier_delta_if(row, 1.0),
            "if_loss_brier_delta": brier_delta_if(row, 0.0),
        })
    return rows


def build_report() -> dict[str, Any]:
    state_state = load_json(STATE_VALVE_STATE_JSON)
    book_state = load_json(BOOK_TRAJ_STATE_JSON)
    state_freeze = parse_ts(state_state.get("freeze_ts_utc"))
    book_freeze = parse_ts(book_state.get("freeze_ts_utc"))
    state_rows = pending_state_valve_rows(state_freeze)
    book_rows = pending_book_traj_rows(book_freeze)
    return {
        "state_valve_freeze_ts_utc": state_state.get("freeze_ts_utc"),
        "book_trajectory_freeze_ts_utc": book_state.get("freeze_ts_utc"),
        "pending_state_valve_rows": state_rows,
        "pending_book_trajectory_rows": book_rows[-25:],
        "pending_state_valve_count": len(state_rows),
        "pending_book_trajectory_count": len(book_rows),
        "interpretation": [
            f"Pending state-valve rows: {len(state_rows)}.",
            f"Pending book-trajectory observation rows: {len(book_rows)}.",
            "Pending rows are not evidence yet; they show what will affect frozen validation after settlement.",
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
    lines = [
        "# v28 Frozen Pending Monitor",
        "",
        f"- State-valve freeze: `{report.get('state_valve_freeze_ts_utc')}`",
        f"- Book-trajectory freeze: `{report.get('book_trajectory_freeze_ts_utc')}`",
        f"- Pending state-valve rows: `{report.get('pending_state_valve_count')}`",
        f"- Pending book-trajectory rows: `{report.get('pending_book_trajectory_count')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Pending State Valve Rows", ""])
    if report.get("pending_state_valve_rows"):
        lines.extend([
            "| market | side | entry | p | ask | gap | keep | status |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ])
        for row in report.get("pending_state_valve_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | {row.get('entry_cents')} | "
                f"{fmt(row.get('p_side'))} | {row.get('ask_cents')} | {fmt(row.get('raw_book_gap'))} | "
                f"{row.get('state_valve_keep')} | {row.get('status')} |"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Pending Book-Trajectory Rows", ""])
    if report.get("pending_book_trajectory_rows"):
        lines.extend([
            "| market | side | event | raw p | candidate p | ask | gap | book delta | if win d | if loss d |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in report.get("pending_book_trajectory_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | `{row.get('event_type')}` | "
                f"{fmt(row.get('raw_p'))} | {fmt(row.get('candidate_p'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('raw_book_gap'))} | {fmt(row.get('book_delta_vs_prior_same_side'))} | "
                f"{fmt(row.get('if_win_brier_delta'))} | {fmt(row.get('if_loss_brier_delta'))} |"
            )
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
