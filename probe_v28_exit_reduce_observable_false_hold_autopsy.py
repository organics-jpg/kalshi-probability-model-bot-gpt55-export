"""Autopsy post-birth false holds in observable reduce-exit loss control.

Research-only; no live bot changes or orders.

The observable reduce loss-control watch looked good diagnostically, but the
post-birth rows are negative. This report inspects the probability-reduce
p_hold>=0.75 denominator and scans simple observable guards to see whether the
fresh harm is separable or whether the mechanism itself is unstable.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import hold_book_gap
from probe_v28_exit_policy_candidates import (
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
)
from probe_v28_frozen_exit_reduce_observable_loss_control_watch import (
    BASE_STATE_JSON,
    STATE_JSON,
    as_float,
    entry_depth,
    entry_feature,
    exit_feature,
    future_rows,
    load_json,
    parse_ts,
    trade_duration_sec,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_reduce_observable_false_hold_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_observable_false_hold_autopsy_latest.md"

MIN_ROWS_FOR_GUARD = 2


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def money(value: Any) -> str:
    number = cents(value)
    return f"{number:.1f}c"


def cents(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def row_delta(row: dict[str, Any]) -> float:
    return cents(hold_to_settlement(row)) - cents(current_exit(row))


def feature_value(row: dict[str, Any], name: str) -> float | None:
    if name == "entry_depth":
        return entry_depth(row)
    if name == "entry_seconds_to_close":
        return entry_feature(row, "mushroom_v28_seconds_to_close")
    if name == "trade_duration_sec":
        return trade_duration_sec(row)
    if name == "entry_book_age_ms":
        return entry_feature(row, "mushroom_v28_book_age_ms")
    if name == "exit_sigma_t_dollars":
        return exit_feature(row, "mushroom_v28_sigma_t_dollars")
    if name == "entry_volshock":
        return entry_feature(row, "mushroom_v28_volshock")
    if name == "exit_cents":
        return as_float(row.get("exit_cents"))
    if name == "p_hold":
        return exit_p_hold(row)
    if name == "fair_drawdown_cents":
        return exit_fair_drawdown(row)
    if name == "hold_book_gap":
        return hold_book_gap(row)
    return None


FEATURES = [
    "entry_depth",
    "entry_seconds_to_close",
    "trade_duration_sec",
    "entry_book_age_ms",
    "exit_sigma_t_dollars",
    "entry_volshock",
    "exit_cents",
    "p_hold",
    "fair_drawdown_cents",
    "hold_book_gap",
]


def candidate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if not is_probability_reduce(row):
            continue
        p_hold = exit_p_hold(row)
        if p_hold is None or p_hold < 0.75:
            continue
        if current_exit(row) is None or hold_to_settlement(row) is None:
            continue
        out.append(row)
    return out


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": exit_reason(row),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "p_hold": exit_p_hold(row),
        "entry_depth": entry_depth(row),
        "entry_seconds_to_close": feature_value(row, "entry_seconds_to_close"),
        "trade_duration_sec": trade_duration_sec(row),
        "entry_book_age_ms": feature_value(row, "entry_book_age_ms"),
        "exit_sigma_t_dollars": feature_value(row, "exit_sigma_t_dollars"),
        "entry_volshock": feature_value(row, "entry_volshock"),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "hold_book_gap": hold_book_gap(row),
        "current_cents": current_exit(row),
        "hold_cents": hold_to_settlement(row),
        "delta_if_suppressed_cents": row_delta(row),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [row_delta(row) for row in rows]
    helpful = [row for row in rows if row_delta(row) > 0.0]
    harmful = [row for row in rows if row_delta(row) < 0.0]
    flat = [row for row in rows if row_delta(row) == 0.0]
    reason_counts = Counter(exit_reason(row) for row in rows)
    return {
        "rows": len(rows),
        "net_delta_cents": sum(deltas),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "helpful_delta_cents": sum(row_delta(row) for row in helpful),
        "harmful_delta_cents": sum(row_delta(row) for row in harmful),
        "avg_delta_cents": (sum(deltas) / len(deltas)) if deltas else 0.0,
        "worst_delta_cents": min(deltas) if deltas else 0.0,
        "best_delta_cents": max(deltas) if deltas else 0.0,
        "exit_reason_counts": dict(reason_counts),
        "rows_detail": [compact(row) for row in sorted(rows, key=row_delta)[:20]],
    }


def scan_guards(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    guards: list[dict[str, Any]] = []
    for feature in FEATURES:
        values = sorted({feature_value(row, feature) for row in rows if feature_value(row, feature) is not None})
        for threshold in values:
            for direction in ("le", "ge"):
                if direction == "le":
                    selected = [row for row in rows if (feature_value(row, feature) is not None and feature_value(row, feature) <= threshold)]
                else:
                    selected = [row for row in rows if (feature_value(row, feature) is not None and feature_value(row, feature) >= threshold)]
                if len(selected) < MIN_ROWS_FOR_GUARD:
                    continue
                summary = summarize_rows(selected)
                guards.append(
                    {
                        "rule": f"{feature}_{direction}_{threshold:.6g}",
                        "feature": feature,
                        "direction": direction,
                        "threshold": threshold,
                        "selected_rows": len(selected),
                        "net_delta_cents": summary["net_delta_cents"],
                        "helpful_rows": summary["helpful_rows"],
                        "harmful_rows": summary["harmful_rows"],
                        "helpful_delta_cents": summary["helpful_delta_cents"],
                        "harmful_delta_cents": summary["harmful_delta_cents"],
                        "avg_delta_cents": summary["avg_delta_cents"],
                        "worst_delta_cents": summary["worst_delta_cents"],
                        "rows_detail": summary["rows_detail"][:8],
                    }
                )
    return sorted(
        guards,
        key=lambda row: (
            row["harmful_rows"] > 0,
            -row["net_delta_cents"],
            -row["selected_rows"],
        ),
    )


def summarize_window(name: str, freeze_ts: str) -> dict[str, Any]:
    rows = candidate_rows(future_rows(freeze_ts))
    summary = summarize_rows(rows)
    guards = scan_guards(rows)
    zero_harm = [row for row in guards if row.get("harmful_rows") == 0]
    return {
        "window": name,
        "freeze_ts_utc": freeze_ts,
        "candidate_summary": summary,
        "best_guards": guards[:15],
        "zero_harm_guards": zero_harm[:15],
    }


def build_report() -> dict[str, Any]:
    base_state = load_json(BASE_STATE_JSON)
    observable_state = load_json(STATE_JSON)
    reduce_freeze = str(base_state.get("freeze_ts_utc") or "")
    observable_freeze = str(observable_state.get("freeze_ts_utc") or "")
    windows = [
        summarize_window("diagnostic_from_reduce_freeze", reduce_freeze),
        summarize_window("post_observable_birth", observable_freeze),
    ]
    diagnostic = windows[0]["candidate_summary"]
    post = windows[1]["candidate_summary"]
    post_zero = windows[1].get("zero_harm_guards") or []
    interpretation = [
        "This is a research-only autopsy; it does not freeze a candidate or change exits.",
        (
            f"Diagnostic p_hold>=0.75 probability-reduce denominator has {diagnostic.get('rows')} rows, "
            f"{diagnostic.get('net_delta_cents')}c net, and harmful delta {diagnostic.get('harmful_delta_cents')}c."
        ),
        (
            f"Post-observable-birth denominator has {post.get('rows')} rows, "
            f"{post.get('net_delta_cents')}c net, and harmful delta {post.get('harmful_delta_cents')}c."
        ),
    ]
    if post.get("net_delta_cents", 0) < 0:
        interpretation.append(
            "The forward denominator itself is negative, so the observable reduce-loss-control mechanism should stay downgraded unless a new frozen guard proves it can avoid false holds."
        )
    if post_zero:
        best = post_zero[0]
        interpretation.append(
            f"Best post-birth zero-harm single-feature guard is {best.get('rule')} with {best.get('selected_rows')} rows and {best.get('net_delta_cents')}c, but this is post-hoc and not promotion evidence."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "reduce_freeze_ts_utc": reduce_freeze,
        "observable_freeze_ts_utc": observable_freeze,
        "windows": windows,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Reduce Observable False-Hold Autopsy",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Reduce freeze UTC: `{report.get('reduce_freeze_ts_utc')}`",
        f"- Observable freeze UTC: `{report.get('observable_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for window in report.get("windows") or []:
        summary = window.get("candidate_summary") or {}
        lines.extend(
            [
                "",
                f"## {window.get('window')}",
                "",
                f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
                f"- Candidate rows: `{summary.get('rows')}`",
                f"- Net/helpful/harmful delta: `{money(summary.get('net_delta_cents'))}` / `{money(summary.get('helpful_delta_cents'))}` / `{money(summary.get('harmful_delta_cents'))}`",
                f"- Helpful/harmful/flat rows: `{summary.get('helpful_rows')}/{summary.get('harmful_rows')}/{summary.get('flat_rows')}`",
                f"- Exit reason counts: `{summary.get('exit_reason_counts')}`",
                "",
                "### Best Single-Feature Guards",
                "",
                "| rule | rows | net c | helpful/harmful | helpful c | harmful c | worst c |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for guard in window.get("best_guards") or []:
            lines.append(
                f"| `{guard.get('rule')}` | {guard.get('selected_rows')} | {money(guard.get('net_delta_cents'))} | "
                f"{guard.get('helpful_rows')}/{guard.get('harmful_rows')} | "
                f"{money(guard.get('helpful_delta_cents'))} | {money(guard.get('harmful_delta_cents'))} | "
                f"{money(guard.get('worst_delta_cents'))} |"
            )
        lines.extend(
            [
                "",
                "### Candidate Rows",
                "",
                "| market | side/result | entry | exit | p_hold | depth | stc | duration | book age | sigma | volshock | drawdown | gap | delta |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in summary.get("rows_detail") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')}/{row.get('result')} | "
                f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | "
                f"{fmt(row.get('entry_depth'))} | {fmt(row.get('entry_seconds_to_close'))} | "
                f"{fmt(row.get('trade_duration_sec'))} | {fmt(row.get('entry_book_age_ms'))} | "
                f"{fmt(row.get('exit_sigma_t_dollars'))} | {fmt(row.get('entry_volshock'))} | "
                f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('hold_book_gap'))} | "
                f"{money(row.get('delta_if_suppressed_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
