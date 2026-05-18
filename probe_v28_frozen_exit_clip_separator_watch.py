"""Frozen forward watch for the v28 exit-clip separator.

Research-only; no live bot changes or orders.

This freezes the diagnostic condition discovered in
probe_v28_exit_clip_separator_diagnostic.py:

    fair_drawdown_cents <= 10 and p_hold >= 0.60

The watch only tracks post-freeze loss rows from the existing loss-escape
ledger. It is not a full exit-PnL simulator and cannot promote a live rule by
itself; it answers whether new matched loss rows keep separating clipped exits
from FV/entry-timing failures.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_clip_separator_watch_state.json"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.md"

MIN_POST_ROWS = 30
MIN_KNOWN_DELTA_CENTS = 300.0


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "fair_drawdown_lte10_p_hold_ge060_exit_clip_separator",
        "rule": "For matched unchanged loss rows, flag rows with fair_drawdown_cents <= 10 and p_hold >= 0.60.",
        "p_hold_floor": 0.60,
        "fair_drawdown_cents_ceiling": 10.0,
        "physics": "A shallow fair-value drawdown with still-adequate p_hold is more likely a clipped-winner exit than a true FV/entry failure.",
        "source_artifact": "v28_exit_clip_separator_diagnostic_latest.json",
        "research_only": True,
    }
    write_json(STATE_JSON, state)
    return state


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


def best_effect(row: dict[str, Any]) -> dict[str, Any]:
    effect = row.get("best_policy_effect")
    return effect if isinstance(effect, dict) else {}


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def row_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("entry_ts") or row.get("exit_ts"))


def is_matched_unchanged(row: dict[str, Any]) -> bool:
    effect = best_effect(row)
    return (
        row.get("escape_class") == "loss_escapes_current_exit_repairs"
        and (effect.get("effect") in {None, "unchanged"} or effect.get("delta_cents") == 0)
    )


def selected(row: dict[str, Any], state: dict[str, Any]) -> bool:
    effect = best_effect(row)
    p_hold = as_float(effect.get("p_hold"))
    drawdown = as_float(effect.get("fair_drawdown_cents"))
    if p_hold is None or drawdown is None:
        return False
    return (
        p_hold >= float(state["p_hold_floor"])
        and drawdown <= float(state["fair_drawdown_cents_ceiling"])
    )


def fail_reasons(row: dict[str, Any], state: dict[str, Any]) -> list[str]:
    effect = best_effect(row)
    p_hold = as_float(effect.get("p_hold"))
    drawdown = as_float(effect.get("fair_drawdown_cents"))
    reasons: list[str] = []
    if p_hold is None:
        reasons.append("p_hold_missing")
    elif p_hold < float(state["p_hold_floor"]):
        reasons.append("p_hold_below_floor")
    if drawdown is None:
        reasons.append("fair_drawdown_missing")
    elif drawdown > float(state["fair_drawdown_cents_ceiling"]):
        reasons.append("fair_drawdown_above_ceiling")
    return reasons


def compact(row: dict[str, Any]) -> dict[str, Any]:
    effect = best_effect(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "failure_class": row.get("failure_class"),
        "actual_cents": row.get("actual_gross_cents"),
        "hold_cents": row.get("hold_gross_cents"),
        "hold_delta_cents": hold_delta(row),
        "p_hold": effect.get("p_hold"),
        "fair_drawdown_cents": effect.get("fair_drawdown_cents"),
        "exit_cents": effect.get("exit_cents") if effect.get("exit_cents") is not None else row.get("exit_cents"),
        "exit_reason": effect.get("exit_reason") or row.get("exit_reason"),
        "selected": None,
        "fail_reasons": [],
        "tags": row.get("physics_tags") or [],
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    known = [row for row in rows if hold_delta(row) is not None]
    helpful = [row for row in known if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known if (hold_delta(row) or 0.0) < 0.0]
    unknown = [row for row in rows if hold_delta(row) is None]
    delta = sum(hold_delta(row) or 0.0 for row in known)
    blockers = []
    if len(rows) < MIN_POST_ROWS:
        blockers.append("post_freeze_rows_lt_30")
    if harmful:
        blockers.append("harmful_hold_rows_present")
    if delta < MIN_KNOWN_DELTA_CENTS:
        blockers.append("known_hold_delta_lt_300c")
    return {
        "rows": len(rows),
        "known_rows": len(known),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "unknown_rows": len(unknown),
        "known_hold_delta_cents": delta,
        "precision_on_known": len(helpful) / len(known) if known else None,
        "failure_class_counts": dict(Counter(str(row.get("failure_class") or "unknown") for row in rows)),
        "exit_reason_counts": dict(Counter(str((best_effect(row).get("exit_reason") or row.get("exit_reason") or "unknown")) for row in rows)),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"])
    payload = load_json(LOSS_ESCAPE_JSON)
    rows = payload.get("loss_rows_with_details") or []
    if not isinstance(rows, list):
        rows = []
    post = [
        row for row in rows
        if is_matched_unchanged(row)
        and freeze_ts is not None
        and (row_ts(row) or datetime.min.replace(tzinfo=timezone.utc)) >= freeze_ts
    ]
    picked = [row for row in post if selected(row, state)]
    missed_known_helpful = [
        row for row in post
        if not selected(row, state)
        and hold_delta(row) is not None
        and (hold_delta(row) or 0.0) > 0.0
    ]
    summary = summarize(picked)
    post_examples = []
    for row in post[:12]:
        item = compact(row)
        item["selected"] = selected(row, state)
        item["fail_reasons"] = fail_reasons(row, state)
        post_examples.append(item)
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "source": str(LOSS_ESCAPE_JSON),
        "post_freeze_matched_unchanged_rows": len(post),
        "candidate_summary": summary,
        "missed_known_helpful_rows": len(missed_known_helpful),
        "candidate_live_ready": False,
        "post_freeze_examples": post_examples,
        "selected_examples": [compact(row) for row in picked[:12]],
        "missed_known_helpful_examples": [compact(row) for row in missed_known_helpful[:12]],
        "interpretation": [
            "Forward watch only; not a full exit-PnL simulator and not promotion evidence by itself.",
            (
                f"Post-freeze matched-unchanged rows: {len(post)}; selected rows: {summary['rows']}; "
                f"known helpful/harmful/unknown: {summary['helpful_rows']}/{summary['harmful_rows']}/{summary['unknown_rows']}."
            ),
            f"Blockers: {summary['blockers']}.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.0f}c"


def example_table(rows: list[dict[str, Any]], include_rule_state: bool = False) -> list[str]:
    lines = [
        (
            "| market | failure | selected | fail reasons | actual | hold | delta | p_hold | drawdown | exit | tags |"
            if include_rule_state
            else "| market | failure | actual | hold | delta | p_hold | drawdown | exit | tags |"
        ),
        (
            "|---|---|---:|---|---:|---:|---:|---:|---:|---|---|"
            if include_rule_state
            else "|---|---|---:|---:|---:|---:|---:|---|---|"
        ),
    ]
    for row in rows:
        if include_rule_state:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('failure_class')}` | {row.get('selected')} | "
                f"`{', '.join(row.get('fail_reasons') or []) or 'none'}` | "
                f"{money(row.get('actual_cents'))} | {money(row.get('hold_cents'))} | "
                f"{money(row.get('hold_delta_cents'))} | {fmt(row.get('p_hold'))} | "
                f"{fmt(row.get('fair_drawdown_cents'))} | `{row.get('exit_reason')}` | `{row.get('tags')}` |"
            )
        else:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('failure_class')}` | {money(row.get('actual_cents'))} | "
                f"{money(row.get('hold_cents'))} | {money(row.get('hold_delta_cents'))} | "
                f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
                f"`{row.get('exit_reason')}` | `{row.get('tags')}` |"
            )
    return lines


def write_outputs(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    state = report.get("state") or {}
    summary = report.get("candidate_summary") or {}
    lines = [
        "# v28 Frozen Exit Clip Separator Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Candidate: `{state.get('candidate')}`",
        f"- Rule: `{state.get('rule')}`",
        f"- Post-freeze matched unchanged rows: `{report.get('post_freeze_matched_unchanged_rows')}`",
        f"- Selected rows: `{summary.get('rows')}`",
        f"- Known helpful/harmful/unknown: `{summary.get('helpful_rows')}/{summary.get('harmful_rows')}/{summary.get('unknown_rows')}`",
        f"- Known hold delta: `{money(summary.get('known_hold_delta_cents'))}`",
        f"- Blockers: `{', '.join(summary.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(["", "## Post-Freeze Denominator Examples", ""])
    lines.extend(example_table(report.get("post_freeze_examples") or [], include_rule_state=True))
    lines.extend(["", "## Selected Examples", ""])
    lines.extend(example_table(report.get("selected_examples") or []))
    lines.extend(["", "## Missed Known Helpful Examples", ""])
    lines.extend(example_table(report.get("missed_known_helpful_examples") or []))
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
