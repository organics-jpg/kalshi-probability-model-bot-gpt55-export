"""Replay the v28 exit-clip separator across row-level exit outcomes.

Research-only; no live bot changes or orders.

The separator diagnostic is loss-only. This replay applies the observable rule
to the row-level exit_reduce frozen artifact so non-loss exits and loss-control
cost are counted too. It remains diagnostic unless restricted to rows after the
separate clip-watch freeze timestamp.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
WATCH_STATE_JSON = OUT_DIR / "v28_frozen_exit_clip_separator_watch_state.json"
OUT_JSON = OUT_DIR / "v28_exit_clip_separator_replay_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clip_separator_replay_latest.md"

EXIT_REASONS = {"mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full"}
P_HOLD_FLOOR = 0.60
FAIR_DRAWDOWN_CEILING = 10.0
MIN_SETTLED = 30
MIN_SUPPRESSED = 30
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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    return parse_ts(row.get("entry_ts") or row.get("exit_ts"))


def should_suppress(row: dict[str, Any]) -> bool:
    p_hold = as_float(row.get("p_hold"))
    drawdown = as_float(row.get("fair_drawdown_cents"))
    return (
        str(row.get("exit_reason") or "") in EXIT_REASONS
        and p_hold is not None
        and drawdown is not None
        and p_hold >= P_HOLD_FLOOR
        and drawdown <= FAIR_DRAWDOWN_CEILING
    )


def sign(value: float) -> str:
    if value > 0:
        return "win"
    if value < 0:
        return "loss"
    return "flat"


def summarize(rows: list[dict[str, Any]], label: str, diagnostic: bool) -> dict[str, Any]:
    usable = [
        row for row in rows
        if as_float(row.get("current_cents")) is not None
        and as_float(row.get("hold_cents")) is not None
    ]
    scored = []
    for row in usable:
        current = as_float(row.get("current_cents")) or 0.0
        hold = as_float(row.get("hold_cents")) or 0.0
        suppressed = should_suppress(row)
        candidate = hold if suppressed else current
        scored.append({
            **row,
            "current_cents": current,
            "candidate_cents": candidate,
            "delta_cents": candidate - current,
            "clip_suppressed": suppressed,
        })
    current_values = [row["current_cents"] for row in scored]
    candidate_values = [row["candidate_cents"] for row in scored]
    suppressed_rows = [row for row in scored if row["clip_suppressed"]]
    loss_to_non_loss = [row for row in scored if row["current_cents"] < 0 <= row["candidate_cents"]]
    non_loss_to_loss = [row for row in scored if row["current_cents"] >= 0 > row["candidate_cents"]]
    suppressed_losers = [row for row in suppressed_rows if row["candidate_cents"] < row["current_cents"]]
    candidate_net = sum(candidate_values)
    blockers = []
    if diagnostic:
        blockers.append("diagnostic_replay_not_clip_watch_forward")
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(suppressed_rows) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_net <= 0:
        blockers.append("net_not_positive")
    if suppressed_losers:
        blockers.append("suppressed_losers_present")
    if int(candidate_net // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "label": label,
        "rows": len(scored),
        "current_net_cents": sum(current_values),
        "candidate_net_cents": candidate_net,
        "delta_cents": candidate_net - sum(current_values),
        "current_wins": sum(1 for value in current_values if value > 0),
        "current_losses": sum(1 for value in current_values if value < 0),
        "candidate_wins": sum(1 for value in candidate_values if value > 0),
        "candidate_losses": sum(1 for value in candidate_values if value < 0),
        "loss_count_reduction": sum(1 for value in current_values if value < 0) - sum(1 for value in candidate_values if value < 0),
        "suppressed_rows": len(suppressed_rows),
        "suppressed_losers": len(suppressed_losers),
        "loss_to_non_loss": len(loss_to_non_loss),
        "non_loss_to_loss": len(non_loss_to_loss),
        "full_loss_cushion_estimate": int(candidate_net // 100.0) if candidate_net > 0 else 0,
        "blockers": blockers,
        "top_loss_to_non_loss": [compact(row) for row in sorted(loss_to_non_loss, key=lambda item: item["delta_cents"], reverse=True)[:10]],
        "top_suppressed_losers": [compact(row) for row in sorted(suppressed_losers, key=lambda item: item["delta_cents"])[:10]],
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "exit_reason": row.get("exit_reason"),
        "current_cents": row.get("current_cents"),
        "candidate_cents": row.get("candidate_cents"),
        "delta_cents": row.get("delta_cents"),
        "p_hold": row.get("p_hold"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "exit_cents": row.get("exit_cents"),
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    state = load_json(WATCH_STATE_JSON)
    rows = source.get("rows") or []
    if not isinstance(rows, list):
        rows = []
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    post_watch = [
        row for row in rows
        if freeze_ts is not None
        and (row_ts(row) or datetime.min.replace(tzinfo=timezone.utc)) >= freeze_ts
    ]
    all_summary = summarize(rows, "diagnostic_from_exit_reduce_freeze", diagnostic=True)
    post_summary = summarize(post_watch, "post_clip_watch_freeze", diagnostic=False)
    post_summary["blockers"] = list(dict.fromkeys([*post_summary["blockers"], "post_clip_watch_sample_pending"]))
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(SOURCE_JSON),
        "watch_state": state,
        "rule": {
            "exit_reasons": sorted(EXIT_REASONS),
            "p_hold_floor": P_HOLD_FLOOR,
            "fair_drawdown_cents_ceiling": FAIR_DRAWDOWN_CEILING,
        },
        "summaries": [all_summary, post_summary],
        "interpretation": [
            "Diagnostic replay includes rows before the clip-watch freeze; use it only as mechanism evidence.",
            (
                f"Diagnostic replay delta is {all_summary['delta_cents']}c with "
                f"{all_summary['loss_count_reduction']} fewer losses and {all_summary['suppressed_losers']} suppressed losers."
            ),
            (
                f"Post-watch replay has {post_summary['rows']} rows and remains promotion-blocked until fresh rows accumulate."
            ),
        ],
    }


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.0f}c"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    state = report.get("watch_state") or {}
    lines = [
        "# v28 Exit Clip Separator Replay",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Clip watch freeze UTC: `{state.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Summaries",
        "",
        "| label | rows | current W/L | candidate W/L | current net | candidate net | delta | suppressed | loss reduction | suppressed losers | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("summaries") or []:
        lines.append(
            f"| `{row.get('label')}` | {row.get('rows')} | {row.get('current_wins')}/{row.get('current_losses')} | "
            f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | {money(row.get('current_net_cents'))} | "
            f"{money(row.get('candidate_net_cents'))} | {money(row.get('delta_cents'))} | "
            f"{row.get('suppressed_rows')} | {row.get('loss_count_reduction')} | {row.get('suppressed_losers')} | "
            f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
