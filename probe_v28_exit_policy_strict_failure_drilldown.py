"""Strict-forward failure drilldown for v28 exit-policy suppressions.

Research-only; no live bot changes or orders.

The high-PnL exit candidates are only useful if their suppressed exits avoid
turning rich exits into full losses. This report inspects the strict common
forward windows and asks which physical guard would have prevented each harmful
suppression.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_book_gap_candidates import hold_book_gap, p_hold as book_p_hold
from probe_v28_exit_policy_candidates import (
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    is_value_over_hold,
    side_won,
)
from probe_v28_exit_policy_common_clock_watch import (
    BOOK_GAP_STATE_JSON,
    DUAL_STATE_JSON,
    LOSS_GUARD_STATE_JSON,
    LOSS_GUARD_V2_STATE_JSON,
    build_scored_rows,
    filter_snapshot,
    loss_guard_load_json,
    max_freeze,
    parse_ts,
    should_book_gap_suppress,
    should_dual_suppress,
    should_loss_guard_suppress,
    should_loss_guard_v2_suppress,
    should_reduce_suppress,
    state_freeze,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_policy_strict_failure_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_exit_policy_strict_failure_drilldown_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def money(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def exit_price_cents(row: dict[str, Any]) -> float | None:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return as_float(features.get("mushroom_v28_exit_bid_cents")) or as_float(row.get("exit_cents"))


def mechanism_tags(row: dict[str, Any]) -> list[str]:
    tags = []
    reason = exit_reason(row)
    gap = hold_book_gap(row)
    p_hold = exit_p_hold(row) or book_p_hold(row)
    drawdown = exit_fair_drawdown(row)
    exit_price = exit_price_cents(row)
    if is_value_over_hold(row):
        tags.append("value_over_hold")
    elif is_probability_reduce(row):
        tags.append("probability_reduce")
    else:
        tags.append(reason or "other_exit")
    if gap is not None and gap < 0.0:
        tags.append("negative_book_gap")
    if exit_price is not None and exit_price >= 80.0:
        tags.append("rich_exit_80_plus")
    if p_hold is not None:
        if p_hold >= 0.85:
            tags.append("p_hold_ge_85")
        elif p_hold >= 0.79:
            tags.append("p_hold_79_85")
        elif p_hold >= 0.75:
            tags.append("p_hold_75_79")
    if drawdown is not None:
        if drawdown <= -5.0:
            tags.append("deep_negative_fair_drawdown")
        elif drawdown > 0.0:
            tags.append("positive_fair_drawdown")
    if "negative_book_gap" in tags and "rich_exit_80_plus" in tags:
        tags.append("book_disagrees_with_hold_at_rich_exit")
    return tags


def policy_delta(row: dict[str, Any], suppress_fn: Callable[[dict[str, Any]], bool]) -> float | None:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    if cur is None or hold is None:
        return None
    if not suppress_fn(row):
        return 0.0
    return float(hold) - float(cur)


def compact_row(
    row: dict[str, Any],
    policy: str,
    v1_suppress: bool,
    v2_suppress: bool,
) -> dict[str, Any]:
    cur = as_float(current_exit(row)) or 0.0
    hold = as_float(hold_to_settlement(row)) or 0.0
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "policy": policy,
        "exit_reason": exit_reason(row),
        "p_hold": exit_p_hold(row) or book_p_hold(row),
        "hold_book_gap": hold_book_gap(row),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "exit_price_cents": exit_price_cents(row),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_cents": hold - cur,
        "loss_guard_v1_would_suppress": v1_suppress,
        "loss_guard_v2_would_suppress": v2_suppress,
        "avoided_by_v1": not v1_suppress,
        "avoided_by_v2": not v2_suppress,
        "tags": mechanism_tags(row),
    }


def summarize_window(
    window_name: str,
    rows: list[dict[str, Any]],
    loss_state: dict[str, Any],
    loss_v2_state: dict[str, Any],
) -> dict[str, Any]:
    suppressors: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
        ("reduce_p_hold_ge_075", should_reduce_suppress),
        ("book_gap_soft_gap15_or_p_hold75", should_book_gap_suppress),
        ("dual_book_gap_else_reduce", should_dual_suppress),
        ("loss_guard_v1", lambda row: should_loss_guard_suppress(row, loss_state)),
        ("loss_guard_v2", lambda row: should_loss_guard_v2_suppress(row, loss_v2_state)),
    ]
    harmful = []
    for policy, suppress_fn in suppressors:
        for row in rows:
            delta = policy_delta(row, suppress_fn)
            if delta is None or delta >= 0.0 or side_won(row) is not False:
                continue
            v1_suppress = should_loss_guard_suppress(row, loss_state)
            v2_suppress = should_loss_guard_v2_suppress(row, loss_v2_state)
            harmful.append(compact_row(row, policy, v1_suppress, v2_suppress))
    policy_counts = Counter(row["policy"] for row in harmful)
    tag_counts = Counter(tag for row in harmful for tag in row.get("tags") or [])
    return {
        "window": window_name,
        "rows": len(rows),
        "harmful_suppressions": len(harmful),
        "policy_counts": dict(policy_counts.most_common()),
        "tag_counts": dict(tag_counts.most_common()),
        "avoided_by_v1": sum(1 for row in harmful if row.get("avoided_by_v1")),
        "avoided_by_v2": sum(1 for row in harmful if row.get("avoided_by_v2")),
        "net_harm_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in harmful),
        "examples": sorted(harmful, key=lambda row: as_float(row.get("delta_cents")) or 0.0)[:12],
    }


def build_report() -> dict[str, Any]:
    loss_state = loss_guard_load_json(LOSS_GUARD_STATE_JSON)
    loss_v2_state = loss_guard_load_json(LOSS_GUARD_V2_STATE_JSON)
    freezes = {
        "book_gap": state_freeze(BOOK_GAP_STATE_JSON),
        "loss_guard": loss_state.get("freeze_ts_utc"),
        "loss_guard_v2": loss_v2_state.get("freeze_ts_utc"),
        "dual": state_freeze(DUAL_STATE_JSON),
    }
    windows = {
        "all_exit_rows_diagnostic": None,
        "book_gap_freeze_comparable": freezes.get("book_gap"),
        "new_exit_mix_common_forward_v1": max_freeze(freezes.get("loss_guard"), freezes.get("dual")),
        "new_exit_mix_common_forward_v2": max_freeze(freezes.get("loss_guard_v2"), freezes.get("dual")),
    }
    scored_rows = build_scored_rows()
    summaries = [
        summarize_window(name, filter_snapshot(scored_rows, freeze_ts), loss_state, loss_v2_state)
        for name, freeze_ts in windows.items()
    ]
    strict_summaries = [
        row for row in summaries
        if str(row.get("window") or "").startswith("new_exit_mix_common_forward")
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_timestamps": freezes,
        "strict_forward_note": "Strict windows are still too small for promotion; this report classifies failure mechanisms only.",
        "summaries": summaries,
        "strict_harmful_suppressions": sum(int(row.get("harmful_suppressions") or 0) for row in strict_summaries),
        "strict_net_harm_cents": sum(as_float(row.get("net_harm_cents")) or 0.0 for row in strict_summaries),
        "interpretation": interpretation(summaries),
    }


def interpretation(summaries: list[dict[str, Any]]) -> list[str]:
    notes = []
    for summary in summaries:
        if str(summary.get("window") or "").startswith("new_exit_mix_common_forward"):
            notes.append(
                f"{summary.get('window')} has {summary.get('harmful_suppressions')} harmful suppressions "
                f"for {summary.get('net_harm_cents')}c net harm; top tags are "
                f"{list((summary.get('tag_counts') or {}).items())[:4]}."
            )
    diagnostic = next((row for row in summaries if row.get("window") == "all_exit_rows_diagnostic"), None)
    if diagnostic:
        notes.append(
            "Across the diagnostic exit sample, the most common harmful-suppression tag is "
            f"{next(iter((diagnostic.get('tag_counts') or {'none': 0}).items()))}."
        )
    notes.append(
        "A harmful suppression with negative book gap and rich executable exit is an exit-policy error, "
        "not an entry edge improvement; a safer rule should usually accept the rich exit."
    )
    return notes


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Policy Strict Failure Drilldown",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze timestamps: `{report.get('freeze_timestamps')}`",
        f"- Strict harmful suppressions: `{report.get('strict_harmful_suppressions')}`",
        f"- Strict net harm: `{money(report.get('strict_net_harm_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for summary in report.get("summaries") or []:
        lines.extend([
            "",
            f"## {summary.get('window')}",
            "",
            f"- Rows: `{summary.get('rows')}`",
            f"- Harmful suppressions: `{summary.get('harmful_suppressions')}`",
            f"- Net harm: `{money(summary.get('net_harm_cents'))}`",
            f"- Avoided by loss-guard v1/v2: `{summary.get('avoided_by_v1')}/{summary.get('avoided_by_v2')}`",
            f"- Policy counts: `{summary.get('policy_counts')}`",
            f"- Top tags: `{dict(list((summary.get('tag_counts') or {}).items())[:8])}`",
        ])
        examples = summary.get("examples") or []
        if examples:
            lines.extend([
                "",
                "| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | avoided v1/v2 | tags |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
            ])
            for row in examples:
                lines.append(
                    f"| `{row.get('policy')}` | {row.get('market')} | {row.get('side')}/{row.get('result')} | "
                    f"{row.get('exit_reason')} | {row.get('p_hold')} | {row.get('hold_book_gap')} | "
                    f"{row.get('fair_drawdown_cents')} | {row.get('exit_price_cents')} | "
                    f"{money(row.get('delta_cents'))} | {row.get('avoided_by_v1')}/{row.get('avoided_by_v2')} | "
                    f"{', '.join(row.get('tags') or [])} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
