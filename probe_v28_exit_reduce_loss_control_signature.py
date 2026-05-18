"""Diagnostic signature of harmful reduce-exit suppression rows.

Research-only; no live bot changes or orders.

The frozen reduce-suppression candidate is profitable but suppresses a small
number of true loss-control exits. This report compares harmful versus helpful
suppressed exits across observable entry/exit features and post-exit path
diagnostics. It is descriptive only; any rule found here must be frozen
separately before it can count as evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    side_won,
)
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_loss_control_signature_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_loss_control_signature_latest.md"


FEATURES = [
    "entry_cents",
    "exit_cents",
    "entry_p_side",
    "entry_edge_cents",
    "entry_raw_edge_cents",
    "entry_abs_d_sigma",
    "entry_seconds_to_close",
    "entry_btc_age_ms",
    "entry_book_age_ms",
    "entry_depth",
    "entry_volshock",
    "exit_p_hold",
    "exit_fair_drawdown_cents",
    "exit_d_sigma",
    "exit_sigma_t_dollars",
    "exit_btc_age_ms",
    "exit_book_age_ms",
    "trade_duration_sec",
    "worst_post_exit_hold_mark_cents",
    "best_post_exit_hold_mark_cents",
    "post_exit_points",
]


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


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows = []
    for row in build_rows():
        exit_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and exit_dt is not None and exit_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def feature(row: dict[str, Any], name: str, path: dict[str, Any]) -> float | None:
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    exit_f = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    if name == "entry_cents":
        return as_float(row.get("entry_cents"))
    if name == "exit_cents":
        return as_float(row.get("exit_cents"))
    if name == "entry_p_side":
        return as_float(entry.get("mushroom_v28_p_side"))
    if name == "entry_edge_cents":
        return as_float(entry.get("mushroom_v28_edge_cents"))
    if name == "entry_raw_edge_cents":
        return as_float(entry.get("mushroom_v28_raw_edge_cents"))
    if name == "entry_abs_d_sigma":
        return as_float(entry.get("mushroom_v28_abs_d_sigma"))
    if name == "entry_seconds_to_close":
        return as_float(entry.get("mushroom_v28_seconds_to_close"))
    if name == "entry_btc_age_ms":
        return as_float(entry.get("mushroom_v28_btc_age_ms"))
    if name == "entry_book_age_ms":
        return as_float(entry.get("mushroom_v28_book_age_ms"))
    if name == "entry_depth":
        return as_float(entry.get("mushroom_v28_eligible_depth"))
    if name == "entry_volshock":
        return as_float(entry.get("mushroom_v28_volshock"))
    if name == "exit_p_hold":
        return exit_p_hold(row)
    if name == "exit_fair_drawdown_cents":
        return exit_fair_drawdown(row)
    if name == "exit_d_sigma":
        return as_float(exit_f.get("mushroom_v28_d_sigma"))
    if name == "exit_sigma_t_dollars":
        return as_float(exit_f.get("mushroom_v28_sigma_t_dollars"))
    if name == "exit_btc_age_ms":
        return as_float(exit_f.get("mushroom_v28_btc_age_ms"))
    if name == "exit_book_age_ms":
        return as_float(exit_f.get("mushroom_v28_book_age_ms"))
    if name == "trade_duration_sec":
        start = parse_ts(row.get("entry_ts"))
        end = parse_ts(row.get("exit_ts"))
        if start is None or end is None:
            return None
        return (end - start).total_seconds()
    if name == "worst_post_exit_hold_mark_cents":
        return as_float(path.get("min_unrealized_hold_gross_cents"))
    if name == "best_post_exit_hold_mark_cents":
        return as_float(path.get("max_unrealized_hold_gross_cents"))
    if name == "post_exit_points":
        return as_float(path.get("post_exit_points"))
    return None


def compact_row(row: dict[str, Any], path: dict[str, Any]) -> dict[str, Any]:
    cur = current_exit(row)
    hold = hold_to_settlement(row)
    values = {name: feature(row, name, path) for name in FEATURES}
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": side_won(row),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": exit_reason(row),
        "current_cents": cur,
        "hold_cents": hold,
        "delta_cents": None if cur is None or hold is None else float(hold) - float(cur),
        **values,
    }


def suppressed_reduce_rows(rows: list[dict[str, Any]], p_hold_floor: float = 0.75) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        p_hold = exit_p_hold(row)
        if is_probability_reduce(row) and p_hold is not None and p_hold >= p_hold_floor:
            out.append(row)
    return out


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summaries: dict[str, Any] = {
        "rows": len(rows),
        "net_delta_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in rows),
        "side_counts": dict(Counter(str(row.get("side") or "") for row in rows)),
    }
    feature_summary = {}
    for name in FEATURES:
        values = [as_float(row.get(name)) for row in rows]
        values = [value for value in values if value is not None]
        if values:
            feature_summary[name] = {
                "min": min(values),
                "avg": mean(values),
                "max": max(values),
            }
    summaries["features"] = feature_summary
    return summaries


def split_score(rows: list[dict[str, Any]], name: str, threshold: float, direction: str) -> dict[str, Any]:
    selected = []
    omitted = []
    for row in rows:
        value = as_float(row.get(name))
        if value is None:
            omitted.append(row)
            continue
        keep = value >= threshold if direction == "ge" else value <= threshold
        (selected if keep else omitted).append(row)
    harmful_selected = sum(1 for row in selected if row.get("side_won") is False)
    helpful_selected = sum(1 for row in selected if row.get("side_won") is True)
    selected_delta = sum(as_float(row.get("delta_cents")) or 0.0 for row in selected)
    omitted_delta = sum(as_float(row.get("delta_cents")) or 0.0 for row in omitted)
    return {
        "feature": name,
        "direction": direction,
        "threshold": threshold,
        "selected_rows": len(selected),
        "selected_helpful": helpful_selected,
        "selected_harmful": harmful_selected,
        "selected_delta_cents": selected_delta,
        "omitted_delta_cents": omitted_delta,
        "harmful_excluded": sum(1 for row in omitted if row.get("side_won") is False),
        "helpful_excluded": sum(1 for row in omitted if row.get("side_won") is True),
    }


def candidate_separators(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for name in FEATURES:
        values = sorted({as_float(row.get(name)) for row in rows if as_float(row.get(name)) is not None})
        if len(values) < 2:
            continue
        thresholds = values
        for threshold in thresholds:
            candidates.append(split_score(rows, name, threshold, "ge"))
            candidates.append(split_score(rows, name, threshold, "le"))
    candidates.sort(
        key=lambda row: (
            -int(row.get("harmful_excluded") or 0),
            int(row.get("helpful_excluded") or 0),
            -float(row.get("selected_delta_cents") or -999999.0),
            -int(row.get("selected_rows") or 0),
        )
    )
    return candidates[:30]


def build_report() -> dict[str, Any]:
    base_state = load_json(BASE_STATE_JSON)
    freeze_ts = str(base_state.get("freeze_ts_utc") or "")
    paths = {str(row.get("market")): row for row in build_post_exit_rows()}
    compact = [
        compact_row(row, paths.get(str(row.get("market"))) or {})
        for row in suppressed_reduce_rows(future_rows(freeze_ts))
    ]
    helpful = [row for row in compact if row.get("side_won") is True]
    harmful = [row for row in compact if row.get("side_won") is False]
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_freeze_ts_utc": freeze_ts,
        "summary": {
            "suppressed_rows": len(compact),
            "helpful_rows": len(helpful),
            "harmful_rows": len(harmful),
            "total_delta_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in compact),
            "helpful_delta_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in helpful),
            "harmful_delta_cents": sum(as_float(row.get("delta_cents")) or 0.0 for row in harmful),
        },
        "helpful_summary": summarize_group(helpful),
        "harmful_summary": summarize_group(harmful),
        "candidate_separators": candidate_separators(compact),
        "harmful_rows": sorted(harmful, key=lambda row: as_float(row.get("delta_cents")) or 0.0),
        "helpful_rows": sorted(helpful, key=lambda row: as_float(row.get("delta_cents")) or 0.0, reverse=True),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary") or {}
    separators = report.get("candidate_separators") or []
    best = separators[0] if separators else {}
    notes = [
        "This is a diagnostic signature report only; candidate separators are retrospective and must be separately frozen before use.",
        f"Suppressed reduce exits: {summary.get('suppressed_rows')} total, {summary.get('helpful_rows')} helpful, {summary.get('harmful_rows')} harmful, net delta {summary.get('total_delta_cents')}c.",
    ]
    if best:
        notes.append(
            f"Best simple separator by harmful-exclusion sort is {best.get('feature')} {best.get('direction')} {best.get('threshold')}: selected {best.get('selected_rows')} rows, selected W/L {best.get('selected_helpful')}/{best.get('selected_harmful')}, delta {best.get('selected_delta_cents')}c, excluded helpful/harmful {best.get('helpful_excluded')}/{best.get('harmful_excluded')}."
        )
    notes.append("Use this to design the next frozen watch, not as promotion evidence.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| market | side | result | delta c | entry | exit | p_hold | drawdown | exit d | entry edge | sec close | duration | worst mark | best mark |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {fmt(row.get('delta_cents'))} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('exit_cents'))} | {fmt(row.get('exit_p_hold'))} | "
            f"{fmt(row.get('exit_fair_drawdown_cents'))} | {fmt(row.get('exit_d_sigma'))} | "
            f"{fmt(row.get('entry_edge_cents'))} | {fmt(row.get('entry_seconds_to_close'))} | "
            f"{fmt(row.get('trade_duration_sec'))} | {fmt(row.get('worst_post_exit_hold_mark_cents'))} | "
            f"{fmt(row.get('best_post_exit_hold_mark_cents'))} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Reduce Loss-Control Signature",
        "",
        "Research-only diagnostic; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source reduce freeze UTC: `{report.get('source_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Candidate Separators", ""])
    lines.extend(
        [
            "| feature | dir | threshold | selected | W/L selected | delta c | excluded helpful | excluded harmful | omitted delta c |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("candidate_separators") or []:
        lines.append(
            f"| {row.get('feature')} | {row.get('direction')} | {fmt(row.get('threshold'))} | "
            f"{row.get('selected_rows')} | {row.get('selected_helpful')}/{row.get('selected_harmful')} | "
            f"{fmt(row.get('selected_delta_cents'))} | {row.get('helpful_excluded')} | "
            f"{row.get('harmful_excluded')} | {fmt(row.get('omitted_delta_cents'))} |"
        )
    lines.extend(["", "## Harmful Suppressed Rows", ""])
    write_rows(lines, report.get("harmful_rows") or [])
    lines.extend(["", "## Helpful Suppressed Rows", ""])
    write_rows(lines, (report.get("helpful_rows") or [])[:24])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
